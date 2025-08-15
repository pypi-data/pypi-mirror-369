from typing import List, Dict, Tuple, Callable

import pandas as pd
from pandas import DataFrame
from pyspark.sql import DataFrame as PySparkDataFrame
from pyspark.sql import functions as F

from seshat.general import configs
from seshat.data_class import SFrame, DFrame
from seshat.transformer import Transformer


class Aggregator(Transformer):
    ONLY_GROUP = False
    HANDLER_NAME = "aggregate"
    DEFAULT_FRAME = DFrame
    DEFAULT_GROUP_KEYS = {"default": configs.DEFAULT_SF_KEY}


class FieldAggregation(Aggregator):
    def __init__(
        self,
        group_by: List[str],
        agg: Dict[str, Tuple[str, str] | Callable],
        group_keys=None,
        *args,
        **kwargs,
    ):
        super().__init__(group_keys, *args, **kwargs)
        self.group_on = group_by
        self.agg = agg

    def calculate_complexity(self):
        return 10

    def validate(self, sf: SFrame):
        super().validate(sf)

        columns = []
        for _, agg_info in self.agg.items():
            if isinstance(agg_info, tuple):
                source_col, _ = agg_info
                columns.append(source_col)
        self._validate_columns(sf, self.default_sf_key, *columns)

    def aggregate_df(self, default: DataFrame, *args, **kwargs) -> Dict[str, DataFrame]:
        grouped = default.groupby(self.group_on)
        result_data = {}

        for col in self.group_on:
            result_data[col] = grouped[col].first().values

        for result_col, agg_info in self.agg.items():
            if isinstance(agg_info, tuple):
                source_col, agg_func = agg_info
                result_data[result_col] = getattr(
                    grouped[source_col], agg_func
                )().values
            else:
                result_values = []
                for _, group in grouped:
                    result_values.append(agg_info(group))
                result_data[result_col] = result_values

        return {"default": pd.DataFrame(result_data)}

    def aggregate_spf(
        self, default: PySparkDataFrame, *args, **kwargs
    ) -> Dict[str, PySparkDataFrame]:
        spark_agg_funcs = {
            "first": F.first,
            "last": F.last,
            "sum": F.sum,
            "mean": F.avg,
            "min": F.min,
            "max": F.max,
            "count": F.count,
        }

        standard_aggs = {}
        for result_col, agg_info in self.agg.items():
            if isinstance(agg_info, tuple) and len(agg_info) == 2:
                source_col, agg_func = agg_info
                if agg_func in spark_agg_funcs:
                    standard_aggs[result_col] = spark_agg_funcs[agg_func](source_col)
                else:
                    return self._fallback_to_pandas(default, *args, **kwargs)

        if any(not isinstance(agg_info, tuple) for agg_info in self.agg.values()):
            return self._fallback_to_pandas(default, *args, **kwargs)

        result = default.groupBy(*self.group_on).agg(
            *[standard_aggs[col].alias(col) for col in standard_aggs]
        )

        return {"default": result}

    def _fallback_to_pandas(
        self, default: PySparkDataFrame, *args, **kwargs
    ) -> Dict[str, PySparkDataFrame]:
        pandas_df = default.toPandas()
        result_dict = self.aggregate_df(pandas_df, *args, **kwargs)
        spark = default.sparkSession
        result_df = spark.createDataFrame(
            result_dict[self.DEFAULT_GROUP_KEYS["default"]]
        )
        return {"default": result_df}
