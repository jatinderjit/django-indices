from typing import List


class JSONIndex:
    def __init__(self, field: List[str], name: str, unique=False, concurrently=True):
        self.field = field
        self.name = name
        self.concurrently = concurrently
        self.unique = unique

    def get_structure(self):
        if type(self.field[0]) is list or type(self.field[0]) is tuple:
            fields = set(self.get_field(f) for f in self.field)
        else:
            fields = {self.get_field(self.field)}
        return {"name": self.name, "fields": fields, "unique": self.unique}

    def get_sql(self, db_table: str):
        concurrently = "CONCURRENTLY" if self.concurrently else ""
        structure = self.get_structure()
        unique = "UNIQUE" if structure["unique"] else ""
        fields = structure["fields"]
        if type(fields) is set:
            fields = ", ".join(fields)
            fields = f"({fields})"

        return f"""
                CREATE {unique} INDEX {concurrently}
                IF NOT EXISTS {self.name}
                ON {db_table} {fields}
        """

    @staticmethod
    def get_field(field: List[str]):
        field = field[:]
        for i, part in enumerate(field[1:], 1):
            field[i] = f"'{part}'"
        field = "->".join(field[:-1]) + "->>" + field[-1]
        return f"({field})"

