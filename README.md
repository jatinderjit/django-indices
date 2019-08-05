# Create JSON Indexes concurrently

The functionality provided by this Django App is similar to the
[indexes](https://docs.djangoproject.com/en/2.2/ref/models/options/#django.db.models.Options.indexes),
except that it provides an option to create indexes
[concurrently](https://www.postgresql.org/docs/current/sql-createindex.html#SQL-CREATEINDEX-CONCURRENTLY).

Currently, only Postgres JSON Indexes are supported.

## Installation and Usage
Install the latest version using pip:
```bash
pip install django_indices
```

Add `django_indices` to `INSTALLED_APPS` in the django settings file and run
the migrate command:
```python
INSTALLED_APPS = (
    ...,
    "django_indices",
)
```

Add the indices you want to the `Meta` class of the required Model. Then run
the `migrate_indices` management command to add / remove the indices:
```bash
python manage.py migrate_indices
```

## Example
```python
from django.db import models
from django.contrib.postgres.fields import JSONField

from django_indices import JSONIndex

class Model(models.Model):
    data = JSONField()

    class Meta:
        indices = [
            # Creates an index on data->'product'->>'id'
            JSONIndex(
                field=["data", "product", "id"],
                name="idx_product_id",
            ),
            # Creates a unique index on data->'order'->>'id'
            JSONIndex(
                field=["data", "order", "id"],
                name="idx_order_id",
                unique=True,
                concurrently=False,
            )
        ]
```
