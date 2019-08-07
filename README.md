# Create JSON Indexes concurrently

The functionality provided by this Django App is similar to the
[indexes](https://docs.djangoproject.com/en/2.2/ref/models/options/#django.db.models.Options.indexes),
except that it provides an option to create indexes
[concurrently](https://www.postgresql.org/docs/current/sql-createindex.html#SQL-CREATEINDEX-CONCURRENTLY).

Currently, only Postgres JSON Indexes are supported.

## Installation
Install the latest version using pip:
```bash
pip install django_indices
```

Add `django_indices` to `INSTALLED_APPS` in the django settings file:
```python
INSTALLED_APPS = (
    ...,
    "django_indices",
)
```

Run the migrations:
```bash
python manage.py migrate django_indices
```

Add the indices you want to the `Meta` class of the required Model. Then run
the `migrate_indices` management command to add / remove the indices:
```bash
python manage.py migrate_indices
```


## Example
```python
from django.db import models
from django.db.models import Q
from django.contrib.postgres.fields import JSONField

from django_indices import JSONIndex

class Inventory(models.Model):
    data = JSONField()

    class Meta:
        indices = [
            # Creates an index on data->'product_type'
            # Indexes are created concurrently by default, which doesn't lock
            # the table.
            JSONIndex(
                field=["data", "product_type"],
                name="idx_inventory_product_type",
            ),

            # Creates a unique index on data->'product'->>'id'
            #
            # concurrently=False ensures that the index creation will execute
            # in a transaction. So the index is either created successfully,
            # or fails cleanly. This will lock the table though.
            JSONIndex(
                field=["data", "product", "id"],
                name="idx_inventory_product_id",
                unique=True,
                concurrently=False,
            ),

            # Creates a partial compound index on
            # (data->'product'->>'brand', data->'product'->>'size')
            # WHERE data->>'product_type' = 'shoe' OR data->>'product_type' = 'crocs'
            JSONIndex(
                field=(["data", "product", "brand"], ["data", "product", "size"]),
                name="idx_inventory_footwear_brand_size",
                where=(Q(data__product_type="shoe") | Q(data__product_type="crocs"),
            ),

        ]
```
