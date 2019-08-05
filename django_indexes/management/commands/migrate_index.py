# -*- coding: utf-8 -*-
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import connections, transaction

from json_index.models import Index


class Command(BaseCommand):
    def handle(self, *args, **options):
        models = []
        for app, app_models in apps.all_models.items():
            for model in app_models.values():
                if hasattr(model._meta, "json_indices"):
                    models.append(model)
        self.cached_code_indices = self.code_indices(models)
        self.cached_db_indices = self.db_indices()
        create, remove, alter = self.get_diff(
            self.cached_code_indices, self.cached_db_indices
        )

        for key, idx in create.items():
            self.create_index(key, idx)
        for key, idx in remove.items():
            self.remove_index(key, idx)
        for key, idx in alter.items():
            self.alter_index(key, idx)

    @staticmethod
    def code_indices(models):
        indices = {}
        for model in models:
            for idx in model._meta.json_indices:
                key = (model._meta.app_label, model.__name__, idx.name)
                indices[key] = idx
        return indices

    @staticmethod
    def db_indices():
        indices = {}
        for idx in Index.objects.all():  # type: Index
            ct = idx.content_type
            model = ct.model_class()
            key = (model._meta.app_label, model.__name__, idx.name)
            indices[key] = idx.get_structure()
        return indices

    @staticmethod
    def get_diff(code_indices, db_indices):
        code_keys = set(code_indices)
        db_keys = set(db_indices)

        create = {k: code_indices[k] for k in (code_keys - db_keys)}
        remove = {k: db_indices[k] for k in (db_keys - code_keys)}

        alter = {}
        for k in code_keys & db_keys:
            code_index = code_indices[k]
            db_index = db_indices[k]
            if code_index.get_structure() != db_index:
                alter[k] = code_index

        return create, remove, alter

    def create_index(self, key, idx):
        print(f"Create index {key}: {idx}")
        app_label, model_name, idx_name = key
        ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
        model = ct.model_class()
        query = idx.get_sql(model._meta.db_table)
        if idx.concurrently:
            self.exec(key, idx, query, True)
        else:
            self.exec_atomically(key, idx, query, True)

    def remove_index(self, key, idx):
        print(f"Remove index {key}: {idx}")
        query = f"DROP INDEX CONCURRENTLY IF EXISTS {key[2]}"
        self.exec(key, idx, query, False)

    def alter_index(self, key, idx):
        print(f"Alter index {key}: {idx}")
        self.remove_index(key, idx)
        self.create_index(key, idx)

    @classmethod
    def exec_atomically(cls, key, idx, query, create):
        with transaction.atomic():
            cls.exec(key, idx, query, create)

    @staticmethod
    def exec(key, idx, query, create):
        print("executing:", query)
        app_label, model_name, idx_name = key
        ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
        with connections["default"].cursor() as cursor:
            cursor.execute(query)
        if create:
            fields = list(idx.get_structure()["fields"])
            Index.objects.create(
                content_type=ct, name=idx_name, unique=idx.unique, field=fields
            )
        else:
            Index.objects.get(content_type=ct, name=idx_name).delete()
