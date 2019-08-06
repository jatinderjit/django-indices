import django.contrib.postgres.fields as pg
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Index(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    name = models.TextField()
    unique = models.BooleanField()
    field = pg.JSONField()
    where = pg.JSONField(null=True, blank=True)

    def get_structure(self):
        return {
            "name": self.name,
            "fields": set(self.field),
            "unique": self.unique,
            "where": set(self.where) if self.where else None,
        }
