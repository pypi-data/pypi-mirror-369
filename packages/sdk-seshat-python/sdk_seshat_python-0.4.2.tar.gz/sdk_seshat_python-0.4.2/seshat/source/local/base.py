from seshat.data_class import SFrame
from seshat.general import configs
from seshat.source import Source


class LocalSource(Source):
    """
    LocalSource is a data source that can read from a local file or an in-memory source.
    """

    def __init__(
        self,
        data_source,
        query=None,
        schema=None,
        mode=configs.DEFAULT_MODE,
    ):
        super().__init__(query, schema, mode)
        self.data_source = data_source

    def convert_data_type(self, data) -> SFrame:
        return self.data_class.from_raw(data)

    def fetch(self) -> SFrame:
        d = (
            self.data_class.read_csv(path=self.data_source)
            if isinstance(self.data_source, str)
            else self.data_source
        )

        return self.convert_data_type(d)

    def calculate_complexity(self):
        return 10
