from typing import Type

from seshat.data_class import SF_MAP
from seshat.data_class.base import SFrame
from seshat.general import configs
from seshat.general.exceptions import InvalidModeError
from seshat.transformer.schema import Schema


class Source:
    """
    An interface class for data retrieval that allows querying and optional schema transformation.
    This class reads data based on a provided query, modifies the data's schema
    if a schema is provided, and returns the result in a specified SFrame format.

    The class includes a `mode` parameter to define result of source must be which sframe.
    """

    query: str
    data_class: Type[SFrame]
    schema: Schema
    mode: str

    def __init__(self, query=None, schema=None, mode=configs.DEFAULT_MODE):
        self.query = query
        self.schema = schema
        self.mode = mode
        try:
            self.data_class = SF_MAP[mode]
        except KeyError:
            raise InvalidModeError()

    def __call__(self, *args, **kwargs) -> SFrame:
        sf = self.fetch(*args, **kwargs)
        if self.schema:
            sf = self.schema(sf)
        return sf

    def calculate_complexity(self):
        return NotImplementedError()

    def fetch(self, *args, **kwargs) -> SFrame:
        pass

    def get_query(self):
        return self.query

    def convert_data_type(self, data) -> SFrame:
        return self.data_class.from_raw(data)
