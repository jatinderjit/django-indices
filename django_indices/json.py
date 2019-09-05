from typing import List

from django.db import connections


class JSONIndex:
    def __init__(
        self, field: List[str], name: str, unique=False, concurrently=True, where=None
    ):
        self.field = field
        self.name = name
        self.concurrently = concurrently
        self.unique = unique
        self.where = where
        self.model = None

    def get_structure(self, model):
        if type(self.field[0]) is list or type(self.field[0]) is tuple:
            fields = set(self.get_field(f) for f in self.field)
        else:
            fields = {self.get_field(self.field)}

        where = self.where
        if where:
            query = model.objects.all().query
            compiler = query.get_compiler("default")
            where = where.resolve_expression(query).as_sql(
                compiler, connections["default"]
            )

        return {
            "name": self.name,
            "fields": fields,
            "unique": self.unique,
            "where": where,
        }

    def get_sql(self, model):
        concurrently = "CONCURRENTLY" if self.concurrently else ""
        structure = self.get_structure(model)
        unique = "UNIQUE" if structure["unique"] else ""
        fields = structure["fields"]
        if type(fields) is set:
            fields = ", ".join(fields)
            fields = f"({fields})"

        where = structure["where"]
        params = {}

        if where:
            where, params = where
            where = f"WHERE {where}"

        return (
            f"""
                CREATE {unique} INDEX {concurrently}
                IF NOT EXISTS {self.name}
                ON {model._meta.db_table} {fields}
                {where or ""}
            """,
            params,
        )

    @staticmethod
    def get_field(field: List[str]):
        field = list(field)
        for i, part in enumerate(field[1:], 1):
            field[i] = f"'{part}'"
        field = "->".join(field[:-1]) + "->>" + field[-1]
        return f"({field})"
