# django-hstore-field



[![PyPI Downloads](https://static.pepy.tech/badge/django-hstore-field)](https://pepy.tech/projects/django-hstore-field) [![CI](https://github.com/baseplate-admin/django-hstore-field/actions/workflows/CI.yaml/badge.svg)](https://github.com/baseplate-admin/django-hstore-field/actions/workflows/CI.yaml) [![Pypi Badge](https://img.shields.io/pypi/v/django-hstore-field.svg)](https://pypi.org/project/django-hstore-field/) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/baseplate-admin/django-hstore-field/master.svg)](https://results.pre-commit.ci/latest/github/baseplate-admin/django-hstore-field/master)

An easy to use [postgres hstore](https://www.postgresql.org/docs/current/hstore.html) field that is based on [`django-hstore-widget`](https://github.com/baseplate-admin/django-hstore-widget)

## Requirements

-   Python 3.9 and Up ( well technically any python version from 3.6 should work )
-   Django 3.2 and Up
-   Modern browsers ( Chrome 112+, Firefox 117+, Safari 16.5+ or [any browsers supporting css nesting](https://caniuse.com/css-nesting) ) 

## Installation

```bash
pip install django-hstore-field
```

## Usage


### Option 1:

Include [`django-hstore-widget`](https://github.com/baseplate-admin/django-hstore-widget) in your `settings.py`'s `INSTALLED_APPS`:

```python

# settings.py

INSTALLED_APPS = [
    ...,
    'django_hstore_widget',
    ...
]

```


### Option 2:

Include  [`django-hstore-widget`](https://github.com/baseplate-admin/django-hstore-widget)'s migration to any of your model's migration:


```python
# Generated migration file
from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):
    dependencies = [
        ("django_hstore_widget", "__latest__"),
    ]

    operations = [
        ...
    ]

```

and then use it:

```python
# yourapp/models.py
from django.db import models
from django_hstore_field import HStoreField


class ExampleModel(models.Model):
    data = HStoreField()
```


### Example: 

Check the [cats directory](https://github.com/baseplate-admin/django-hstore-field/tree/master/tests/cat)

> [!NOTE]  
If you want a lower level implementation, please check [django-hstore-widget](https://github.com/baseplate-admin/django-hstore-widget).

