class SmartValidateMixin:
    def clean(self):
        cleaned = super().clean()
        for field_name, validator in getattr(self, 'smart_validators', {}).items():
            validator(cleaned.get(field_name))
        return cleaned
