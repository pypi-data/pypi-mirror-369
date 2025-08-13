class BaseField:
    def __init__(self, primary_key: bool = False):
        self.primary_key: bool = primary_key
        self.default: None

class IntegerField(BaseField):
    def __init__(self, primary_key: bool = False, default: int | None = None):
        super().__init__(primary_key=primary_key)
        self.default: int | None = default

class StringField(BaseField):
    def __init__(self, primary_key: bool = False, default: str | None = None):
        super().__init__(primary_key=primary_key)
        self.default: str | None = default

class ListField(BaseField):
    def __init__(self, primary_key: bool = False, default: list | None = None):
        super().__init__(primary_key=primary_key)
        self.default: list | None = default

class DictField(BaseField):
    def __init__(self, primary_key: bool = False, default: dict | None = None):
        super().__init__(primary_key=primary_key)
        self.default: dict | None = default

class AutoField(BaseField):
    def __init__(self):
        super().__init__(primary_key=True)