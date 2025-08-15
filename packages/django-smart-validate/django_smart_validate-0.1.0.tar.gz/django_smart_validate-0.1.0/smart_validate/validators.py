import re
from django.core.exceptions import ValidationError

class SmartValidator:
    patterns = {
        "alpha_numeric": r"^[A-Za-z0-9]+$",
        "slug": r"^[a-z0-9-]+$",
        "phone": r"^\+?[0-9]{10,15}$",
        "code": r"^[A-Z0-9]{6,10}$",
    }

    @classmethod
    def validator(cls, pattern, flags=0, message=None):
        regex = cls.patterns.get(pattern, pattern)
        def _validate(value):
            if not re.match(regex, value, flags):
                raise ValidationError(message or f"Value does not match pattern: {pattern}")
        return _validate

    @classmethod
    def email(cls):
        from django.core.validators import validate_email
        return validate_email
