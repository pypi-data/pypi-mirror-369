from __future__ import annotations
import json
import os.path
from typing import Type, Any

from .errors import *
from .fields import BaseField, AutoField
from tempfile import NamedTemporaryFile
from pathlib import Path
import portalocker

class Manager:
    def __init__(self, model: Type[Model]):
        self.model: Type[Model] = model

    def get(self, **kwargs) -> Model | None:
        for obj in self._extract_like_objects():
            for k, v in kwargs.items():
                if not hasattr(obj, k):
                    raise FieldDoesNotExistError(f"Field '{k}' does not exist in model.")
                if getattr(obj, k) != v:
                    break
            else:
                return obj
        return None

    def get_or_create(self, **kwargs) -> Model:
        obj = self.get(**kwargs)
        return obj if obj is not None else self.create(**kwargs)

    def all(self) -> list[Model]:
        return self._extract_like_objects()

    def create(self, **kwargs) -> Model:
        fields = {k: v for k, v in self.model.__dict__.items() if isinstance(v, BaseField)}
        primary_key, primary_field = self._get_primary()

        if (primary_key not in kwargs or kwargs[primary_key] is None) and not isinstance(primary_field, AutoField):
            raise MissingPrimaryKeyInObjectError()

        data = self._extract()

        if primary_key in kwargs and str(kwargs[primary_key]) in data:
            raise DuplicatePrimaryKeyError()

        return self._create(data, fields, primary_key, kwargs)

    def update(self, obj: Model):
        data = self._extract()
        self._update(data, obj)

    def delete(self, **kwargs):
        obj = self.get(**kwargs)
        if obj is None or obj.pk() is None:
            raise ObjectNotFoundError()
        self._delete(obj)



    def clear(self):
        self._clear()

    def _create(
        self,
        data: dict[str, dict],
        fields: dict[str, BaseField],
        primary_key: str,
        kwargs: dict[str, Any]
    ) -> Model:
        if primary_key in kwargs and kwargs[primary_key] is not None:
            pk_value = kwargs[primary_key]
        else:
            if isinstance(fields[primary_key], AutoField):
                numbers = [int(k) for k in data.keys()] if data else []
                pk_value = max(numbers) + 1 if numbers else 1
                kwargs[primary_key] = pk_value
            else:
                raise MissingPrimaryKeyInObjectError()

        pk_str = str(pk_value)

        if pk_str in data:
            raise DuplicatePrimaryKeyError()

        data[pk_str] = {}
        for field_name, field in fields.items():
            if field_name in kwargs:
                data[pk_str][field_name] = kwargs[field_name]
            else:
                data[pk_str][field_name] = (
                    pk_value if field_name == primary_key else field.default
                )

        self._insert(data)
        return self.model(**data[pk_str])

    def _update(self, data, obj: Model):
        pk = str(obj.pk())
        # print(data, "9000")
        for k, v in obj.__dict__.items():
            data[pk][k] = v
        self._insert(data)

    def _get_primary(self) -> tuple[str, BaseField]:
        name = self.model._primary_key_field
        return name, getattr(self.model, name)

    def _extract_like_objects(self) -> list[Model]:
        data = self._extract()
        return [self.model(**v) for k, v in data.items()]


    def _extract(self) -> dict[str, dict]:
        with open(self.model.path_to_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def _insert(self, data: dict[str, dict]):
        with portalocker.Lock(self.model.path_to_file + ".lock", timeout=10):
            with NamedTemporaryFile("w", dir=Path(self.model.path_to_file).parent,
                                    delete=False, encoding="utf-8") as tmp:
                json.dump(data, tmp, ensure_ascii=False, indent=4)
                tmp.flush()
                os.fsync(tmp.fileno())
            os.replace(tmp.name, self.model.path_to_file)

    def _delete(self, obj):
        data = self._extract()
        del data[str(obj.pk())]
        self._insert(data)

    def _clear(self):
        self._insert({})

class MetaModel(type):
    def __new__(cls, name, bases, attrs):
        if "path_to_file" not in attrs:
            attrs["path_to_file"] = attrs["__qualname__"].replace(".", "_") + ".json"

        klass = super().__new__(cls, name, bases, attrs)

        primary_keys: list[str] = [
            k for k, v in klass.__dict__.items()
            if isinstance(v, BaseField) and (v.primary_key or isinstance(v, AutoField))
        ]

        if len(primary_keys) == 0:
            setattr(klass, "id", AutoField())
            primary_keys = ["id"]
        elif len(primary_keys) > 1:
            raise MissingPrimaryKeyError("The model must contain exactly one primary key.")
        klass._primary_key_field: str = primary_keys[0]
        klass.objects = Manager(model=klass)
        return klass


class Model(metaclass=MetaModel):
    path_to_file: str | None = None

    def __init__(self, **kwargs):
        for k, v in self.__class__.__dict__.items():
            if not k.startswith('__') and not callable(v) and isinstance(v, BaseField):
                setattr(self, k, kwargs.get(k, getattr(v, "default", None))) # TODO

    def __str__(self):
        return '<%s object (%s)>' % (self.__class__.__name__, self.pk())

    def __repr__(self):
        return '<%s object (%s)>' % (self.__class__.__name__, self.pk())

    @classmethod
    def sync(cls) -> None:
        if not os.path.exists(cls.path_to_file):
            with open(cls.path_to_file, "w", encoding="utf-8") as file:
                file.write("{}")
            return

        with open(cls.path_to_file, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}

        model_fields: dict[str, BaseField] = {
            k: v for k, v in cls.__dict__.items()
            if not k.startswith('__') and not callable(v) and isinstance(v, BaseField)
        }

        primary_keys = [k for k, v in model_fields.items() if v.primary_key or isinstance(v, AutoField)]
        if len(primary_keys) != 1:
            raise MissingPrimaryKeyError("Model must have exactly one primary key.")

        updated = False
        for pk, obj_data in data.items():
            for field_name, field in model_fields.items():
                if field_name not in obj_data:
                    obj_data[field_name] = field.default
                    updated = True

            extra_keys = set(obj_data.keys()) - set(model_fields.keys())
            for key in extra_keys:
                del obj_data[key]
                updated = True

        if updated:
            with open(cls.path_to_file, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

    def save(self):
        if self.pk() is not None:
            self.objects.update(self)
        else:
            self.__dict__ = self.objects.create(**self.__dict__).__dict__

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if not hasattr(self, k):
                raise FieldDoesNotExistError(f"Field '{k}' does not exist in model.")
            setattr(self, k, v)
        self.save()

    def delete(self):
        if self.pk() is not None:
            self.objects.delete(**self.__dict__)

    def pk(self):
        return getattr(self, self.__class__._primary_key_field)


