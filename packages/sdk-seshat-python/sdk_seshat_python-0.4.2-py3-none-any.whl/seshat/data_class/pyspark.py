from typing import Dict, Iterable, List

from pandas import DataFrame
from pyspark.sql import DataFrame as PySparkDataFrame
from pyspark.sql import SparkSession

from seshat.data_class import DFrame, SFrame
from seshat.data_class.base import GroupSFrame
from seshat.general import configs


class SPFrame(SFrame):
    frame_name = "spf"
    data: PySparkDataFrame

    def make_group(self, default_key=configs.DEFAULT_SF_KEY):
        return GroupSFrame({default_key: self}, sframe_class=self.__class__)

    def get_columns(self, *args) -> Iterable[str]:
        return self.data.columns

    def to_dict(self, *cols: str, key: str = configs.DEFAULT_SF_KEY) -> List[Dict]:
        selected = self.data.select(*cols).distinct() if cols else self.data
        return [row.asDict() for row in selected.collect()]

    def iterrows(self, column_name: str, key: str = configs.DEFAULT_SF_KEY):
        for row in self.data.collect():
            yield row[column_name]

    def to_df(self) -> SFrame:
        from seshat.data_class import DFrame

        return DFrame.from_raw(self.data.toPandas())

    def extend_vertically(self, other: PySparkDataFrame):
        super().extend_vertically(other)
        self.data = self.data.unionByName(other)

    def extend_horizontally(
        self, other: PySparkDataFrame, on: str, left_on: str, right_on: str, how: str
    ):
        super().extend_horizontally(other, on, left_on, right_on, how)

        if left_on and right_on:
            on = getattr(self.data, left_on) == getattr(other, right_on)

        self.data = self.data.drop_duplicates().join(
            other.drop_duplicates(), on=on, how=how
        )

    @classmethod
    def read_csv(cls, path, *args, **kwargs) -> "PySparkDataFrame":
        kwargs.setdefault("header", True)
        return cls.get_spark().read.csv(path, *args, **kwargs)

    @classmethod
    def from_raw(cls, data, *args, **kwargs) -> "SPFrame":
        if isinstance(data, DataFrame):
            data = DFrame.from_raw(data).convert(cls).to_raw()
        elif not isinstance(data, PySparkDataFrame) and data:
            data = cls.get_spark().createDataFrame(data or [])
        return cls(data)

    @staticmethod
    def get_spark():
        return SparkSession.builder.appName(configs.SPARK_APP_NAME).getOrCreate()
