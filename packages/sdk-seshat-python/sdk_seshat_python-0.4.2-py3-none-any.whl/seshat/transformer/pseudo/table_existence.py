from seshat.data_class import SFrame
from seshat.source.mixins import SQLMixin
from seshat.transformer import Transformer
from seshat.transformer.schema import Schema


class SQLTableExistenceValidator(Transformer, SQLMixin):

    def __init__(
        self,
        schema: Schema,
        url: str,
        table_name: str,
        group_keys=None,
    ):
        super().__init__(group_keys)
        self.table_name = table_name
        self.schema = schema
        self.url = url

    def __call__(self, sf_input: SFrame = None, *args, **kwargs):
        self.ensure_table_exists(self.table_name, self.schema)
        return sf_input

    def calculate_complexity(self):
        return 10
