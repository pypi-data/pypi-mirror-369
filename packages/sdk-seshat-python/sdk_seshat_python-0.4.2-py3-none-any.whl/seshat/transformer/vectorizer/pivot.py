from typing import Dict, List

import pandas as pd
from pandas import DataFrame
from pyspark.sql import DataFrame as PySparkDataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    FloatType,
)
from pyspark.sql.window import Window
from sklearn.preprocessing import MinMaxScaler

from seshat.data_class import SPFrame
from seshat.data_class.pandas import DFrame
from seshat.general import configs
from seshat.transformer.vectorizer.base import SFrameVectorizer
from seshat.transformer.vectorizer.utils import AggregationStrategy, CountStrategy


class TokenPivotVectorizer(SFrameVectorizer):
    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "vector": configs.VECTOR_SF_KEY,
    }

    def __init__(
        self,
        strategy: AggregationStrategy = CountStrategy(),
        address_cols: List[str] = (configs.FROM_ADDRESS_COL, configs.TO_ADDRESS_COL),
        result_address_col: str = configs.ADDRESS_COL,
        should_normalize: bool = True,
        col_prefix: str = "token_",
        group_keys=None,
        *args,
        **kwargs,
    ):
        super().__init__(group_keys, *args, **kwargs)
        self.strategy = strategy
        self.address_cols = address_cols
        self.should_normalize = should_normalize
        self.col_prefix = col_prefix
        self.result_address_col = result_address_col

    def calculate_complexity(self):
        return 20

    def vectorize_df(
        self, default: DataFrame = None, *args, **kwargs
    ) -> Dict[str, DataFrame]:
        pivots = [
            self.strategy(
                DFrame.from_raw(default), addr, token_column=f"{self.col_prefix}{addr}"
            )
            for addr in self.address_cols
        ]

        vector = (
            pivots[0].fillna(0)
            if len(pivots) == 1
            else pd.merge(*pivots, on=self.result_address_col, how="outer").fillna(0)
        )

        if self.should_normalize:
            vector = self.normalize_df(vector)
        return {"default": default, "vector": vector}

    def vectorize_spf(
        self, default: PySparkDataFrame, *args, **kwargs
    ) -> Dict[str, DataFrame]:
        pivots = [
            self.strategy(
                SPFrame.from_raw(default), addr, token_column=f"{self.col_prefix}{addr}"
            )
            for addr in self.address_cols
        ]
        vector = pivots[0]
        for pivot in pivots[1:]:
            vector = vector.join(pivot, on=self.result_address_col, how="outer")
        vector = vector.na.fill(0)
        if self.should_normalize:
            vector = self.normalize_spf(vector)

        return {"default": default, "vector": vector}

    @staticmethod
    def normalize_df(vector: DataFrame) -> DataFrame:
        scaler = MinMaxScaler()
        columns_to_normalize = vector.columns[1:]
        normalized = scaler.fit_transform(vector[columns_to_normalize])
        normalized = pd.DataFrame(normalized, columns=columns_to_normalize)
        vector = pd.concat(
            [vector.drop(columns=columns_to_normalize), normalized], axis=1
        )
        return vector

    @staticmethod
    def normalize_spf(vector: PySparkDataFrame) -> PySparkDataFrame:
        scaler = MinMaxScaler()
        columns_to_normalize = vector.columns[1:]
        normalized = scaler.fit_transform(vector.select(columns_to_normalize).collect())
        schema = StructType(
            [
                StructField(col_name, FloatType(), True)
                for col_name in columns_to_normalize
            ]
        )

        normalized = SPFrame.get_spark().createDataFrame(normalized, schema=schema)
        for col_name in columns_to_normalize:
            vector = vector.drop(col_name)
        vector = vector.withColumn("index", F.monotonically_increasing_id())
        normalized = normalized.withColumn("index", F.monotonically_increasing_id())
        w = Window.orderBy("index")
        vector = vector.withColumn("index", F.row_number().over(w))
        normalized = normalized.withColumn("index", F.row_number().over(w))
        return vector.join(normalized, "index", "left").drop("index")
