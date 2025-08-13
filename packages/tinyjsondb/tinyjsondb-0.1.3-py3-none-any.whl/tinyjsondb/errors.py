class BaseModelError(Exception):  # ранее BaseError
    """Base exception for model-related errors."""
    pass

class MissingPrimaryKeyError(BaseModelError):
    """Raised when a model does not define any primary key."""
    pass

class MissingPrimaryKeyInObjectError(BaseModelError):
    """Raised when trying to create/update object without a primary key."""
    pass

class DuplicatePrimaryKeyError(BaseModelError):
    """Raised when the primary key already exists in the DB."""
    pass

class FieldDoesNotExistError(BaseModelError):
    """Raised when a field is accessed that does not exist in the model."""
    pass

class ObjectNotFoundError(BaseModelError):
    """Raised when attempting to delete a non-existing object."""
    pass