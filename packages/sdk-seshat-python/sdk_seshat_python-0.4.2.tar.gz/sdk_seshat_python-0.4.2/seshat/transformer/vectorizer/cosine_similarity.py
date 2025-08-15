import typing
from typing import Dict

import numpy as np
import pandas as pd
from pandas import DataFrame
from pyspark.sql import DataFrame as PySparkDataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, FloatType, Row, StringType
from pyspark.sql.window import Window
from sklearn.metrics.pairwise import cosine_similarity

from seshat.data_class import DFrame, SPFrame
from seshat.general import configs
from seshat.transformer.vectorizer.base import SFrameVectorizer
from seshat.transformer.vectorizer.pivot import TokenPivotVectorizer


class CosineSimilarityVectorizer(SFrameVectorizer):
    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "vector": configs.VECTOR_SF_KEY,
        "cosine_sim": configs.COSINE_SIM_SF_KEY,
        "top_address": configs.TOP_ADDRESS_SF_KEY,
        "exclusion": configs.EXCLUSION_SF_KEY,
    }

    def __init__(
        self,
        square_shape: bool = True,
        address_col: str = configs.ADDRESS_COL,
        address_1_col: str = "address_1",
        address_2_col: str = "address_2",
        cosine_col: str = "cosine",
        exclusion_token_col: str = configs.CONTRACT_ADDRESS_COL,
        threshold_value: float | int = 100,
        threshold: typing.Literal["by_count", "by_value", "none"] = "none",
        find_top_address: bool = False,
        top_address_limit: int = 100,
        group_keys=None,
        *args,
        **kwargs,
    ):
        super().__init__(group_keys, *args, **kwargs)
        self.square_shape = square_shape
        self.address_col = address_col
        self.address_1_col = address_1_col
        self.address_2_col = address_2_col
        self.cosine_col = cosine_col
        self.exclusion_token_col = exclusion_token_col
        self.threshold = threshold
        self.threshold_value = threshold_value
        self.find_top_address = find_top_address
        self.top_address_limit = top_address_limit

    def calculate_complexity(self):
        return 20

    def vectorize_df(
        self,
        default: DataFrame = None,
        vector: DataFrame = None,
        exclusion: DataFrame = None,
        *args,
        **kwargs,
    ) -> Dict[str, DataFrame]:
        if vector is None:
            sf_input = DFrame.from_raw(default).make_group(self.default_sf_key)
            sf_output = TokenPivotVectorizer(result_address_col=self.address_col)(
                sf_input
            )
            vector = sf_output.get(configs.VECTOR_SF_KEY).to_raw()
        if exclusion is not None:
            vector = vector[
                ~vector[self.address_col].isin(exclusion[self.exclusion_token_col])
            ]

        attributes = vector.iloc[:, 1:].values
        all_addresses = vector[self.address_col].values
        cosine = cosine_similarity(attributes)
        cosine = pd.DataFrame(columns=all_addresses, index=all_addresses, data=cosine)
        return_kwargs = {"default": default, "cosine_sim": cosine}

        if self.find_top_address:
            top_series = cosine.sum(axis=1).nlargest(self.top_address_limit)
            top_address = pd.DataFrame(
                {self.address_col: top_series.index, self.cosine_col: top_series.values}
            )
            return_kwargs["top_address"] = top_address

        if not self.square_shape:
            mask = np.triu(np.ones(cosine.shape[0])).astype(bool)
            cosine = cosine.where(~mask, 0)
            cosine = cosine.stack().reset_index()
            cosine.columns = [self.address_1_col, self.address_2_col, self.cosine_col]
            cosine = cosine.rename(columns={"index": self.address_2_col})
            cosine = cosine[cosine[self.cosine_col] != 0]
            cosine.reset_index(drop=True, inplace=True)

            if self.threshold == "by_value":
                cosine = cosine[cosine[self.cosine_col] >= self.threshold_value]
            elif self.threshold == "by_count":
                left = cosine
                right = cosine.rename(
                    columns={
                        self.address_1_col: "temp",
                        self.address_2_col: self.address_1_col,
                    }
                ).rename(columns={"temp": self.address_2_col})
                agg_cosine = pd.concat([left, right])
                del left
                del right

                agg_cosine = agg_cosine.sort_values("cosine", ascending=False)
                agg_cosine = agg_cosine.groupby(self.address_1_col).head(
                    self.threshold_value
                )
                agg_cosine[[self.address_1_col, self.address_2_col]] = pd.DataFrame(
                    np.sort(
                        agg_cosine[[self.address_1_col, self.address_2_col]], axis=1
                    ),
                    index=agg_cosine.index,
                )
                cosine = agg_cosine.drop_duplicates().reset_index(drop=True)
            return_kwargs["cosine_sim"] = cosine

        return return_kwargs

    def vectorize_spf(
        self,
        default: PySparkDataFrame = None,
        vector: DataFrame = None,
        *args,
        **kwargs,
    ):
        if vector is None:
            sf_input = SPFrame.from_raw(default).make_group(self.default_sf_key)
            sf_output = TokenPivotVectorizer(result_address_col=self.address_col)(
                sf_input
            )
            vector = sf_output.get(configs.VECTOR_SF_KEY).to_raw()
        attributes = np.array(vector.select(vector.columns[1:]).collect())
        all_address = [
            row[self.address_col] for row in vector.select(self.address_col).collect()
        ]

        cosine = cosine_similarity(attributes)
        schema = StructType(
            [StructField(str(address), FloatType(), True) for address in all_address],
        )
        cosine = SPFrame.get_spark().createDataFrame(cosine, schema=schema)
        return_kwargs = {"default": default, "vector": vector, "cosine_sim": cosine}
        if self.find_top_address:
            top_address = cosine.withColumn(
                self.cosine_col, sum([F.col(c) for c in cosine.columns])
            )
            top_address = top_address.sort(self.cosine_col, ascending=False)
            window = Window.orderBy(self.cosine_col)
            top_address = top_address.withColumn(
                "index", F.row_number().over(window) - 1
            )
            cols = top_address.columns

            def get_address(index):
                return str(cols[index])

            top_address = top_address.withColumn(
                self.address_col, F.udf(get_address, StringType())(F.col("index"))
            )

            to_drop = set(cols) - {self.address_col, self.cosine_col}
            top_address = top_address.drop(*to_drop)
            top_address = top_address.limit(self.top_address_limit)

            return_kwargs["top_address"] = top_address

        if not self.square_shape:
            addresses_rdd = (
                SPFrame.get_spark()
                .sparkContext.parallelize(all_address)
                .map(lambda x: Row(address=x))
            )

            address = SPFrame.get_spark().createDataFrame(addresses_rdd)
            address = address.withColumn("index", F.monotonically_increasing_id())
            cosine = cosine.withColumn("index", F.monotonically_increasing_id())
            w = Window.orderBy("index")
            address = address.withColumn("index", F.row_number().over(w))
            cosine = cosine.withColumn("index", F.row_number().over(w))
            cosine = cosine.join(address, "index", "left").drop("index")

            unpivot_cols = cosine.columns
            unpivot_cols.remove(self.address_col)
            cosine = cosine.melt(
                self.address_col,
                unpivot_cols,
                self.address_2_col,
                self.cosine_col,
            )
            cosine = cosine.withColumnRenamed(self.address_col, self.address_1_col)

            cosine = cosine.withColumn(
                "min_address",
                F.least(F.col(self.address_1_col), F.col(self.address_2_col)),
            ).withColumn(
                "max_address",
                F.greatest(F.col(self.address_1_col), F.col(self.address_2_col)),
            )

            cosine = cosine.dropDuplicates(
                ["min_address", "max_address", self.cosine_col]
            )
            cosine = cosine.drop("min_address", "max_address")

            if self.threshold != "none":
                new_cosine = self.get_threshold_spf_items(all_address[0], cosine)
                for address in all_address[1:]:
                    new_cosine = new_cosine.union(
                        self.get_threshold_spf_items(address, cosine)
                    )
                cosine = new_cosine.drop_duplicates()
            return_kwargs["cosine_sim"] = cosine
        return return_kwargs

    def get_threshold_spf_items(self, address, cosine_sim):
        related_order = cosine_sim.filter(
            (cosine_sim[self.address_1_col] == address)
            | (cosine_sim[self.address_2_col] == address)
        )
        if self.threshold == "by_count":
            return related_order.orderBy(F.col(self.cosine_col).desc()).limit(
                self.threshold_value
            )
        return related_order.filter(F.col(self.cosine_col) >= self.threshold_value)
