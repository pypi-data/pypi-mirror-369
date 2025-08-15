# django-smart-validate

**Smart reusable validators for Django models & forms.**

`django-smart-validate` provides a collection of pre-built, reusable validators
and a mixin for applying them easily in Django models or forms.

---

## Features
- Ready-to-use common validation patterns (slug, alpha-numeric, phone, email, etc.)
- Simple API for custom regex patterns
- Works in both **Django models** and **forms**
- Lightweight, no extra dependencies except Django

---

## Installation

```bash
pip install django-smart-validate
```

Usage
In a Django Model

```
from django.db import models
from smart_validate.validators import SmartValidator

class MyModel(models.Model):
    user_code = models.CharField(max_length=10, validators=[SmartValidator.validator("code")])
    email = models.CharField(max_length=254, validators=[SmartValidator.email()])
```

In a Django Form with Mixin
```aiignore

from django import forms
from smart_validate.validators import SmartValidator
from smart_validate.mixins import SmartValidateMixin

class MyForm(SmartValidateMixin, forms.Form):
    name = forms.CharField()
    email = forms.CharField()

    smart_validators = {
        "name": SmartValidator.validator("alpha_numeric"),
        "email": SmartValidator.email(),
    }

```

Available Validators

```aiignore

SmartValidator.validator("alpha_numeric")

SmartValidator.validator("slug")

SmartValidator.validator("phone")

SmartValidator.validator("code")

SmartValidator.email()
```