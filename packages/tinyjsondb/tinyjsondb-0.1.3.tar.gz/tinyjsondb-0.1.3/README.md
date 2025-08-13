# tinyjsondb

tinyjsondb is a minimal Python ORM for working with JSON files as a simple database.
It allows defining models with typed fields, creating, reading, updating, and deleting records, all stored in JSON.

## Installation

```bash
pip install tinyjsondb
```

or from source:

```bash
git clone https://github.com/Waland2/tinyjsondb.git
cd tinyjsondb
pip install .
```

## Quick Start

```python
from tinyjsondb import Model, IntegerField, StringField, ListField

class User(Model):
    name = StringField(default="Anonymous")
    hobbies = ListField(default=[])

# Initialize the storage file and sync schema
User.sync()

# Create a record
User.objects.create(name="Alice", hobbies=["reading"])

# Get a record
user = User.objects.get(id=1)
print(user.name)  # Alice

# Update a record
user.update(name="Alice Wonderland")

# Delete a record
user.delete()
user = User.objects.get(id=1)
print(user is None)  # True

# Get all records
users = User.objects.all()
```

## Overview

**Model methods:**

* `sync()` - create or update the JSON file with data.
* `save()` - insert or update the record.
* `update(**kwargs)` - update fields and save.
* `delete()` - remove the record.
* `pk()` - return the primary key value.

**Manager methods (`Model.objects`):**

* `create(**kwargs)` - insert a new record.
* `get(**kwargs)` - return the first matching record or `None`.
* `get_or_create(**kwargs)` - return an existing record or create it.
* `all()` - return all records.
* `update(obj)` - update an existing record.
* `delete(**kwargs)` - remove a record by field values.
* `clear()` - remove all records.

### Field types

* `IntegerField()` - integer field.
* `StringField()` - string field.
* `ListField()` - list field.
* `DictField()` - dictionary field.

## License

This project is licensed under the [MIT License](LICENSE.md).




