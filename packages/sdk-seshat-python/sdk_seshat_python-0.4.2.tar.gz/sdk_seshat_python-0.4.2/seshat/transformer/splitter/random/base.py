from typing import Dict

from pandas import DataFrame
from pyspark.sql.dataframe import DataFrame as PySparkDataFrame
from sklearn.model_selection import train_test_split

from seshat.transformer.splitter import Splitter


class RandomSplitter(Splitter):
    def __init__(self, percent=0.8, seed=42, group_keys=None, *args, **kwargs):
        super().__init__(group_keys=group_keys, *args, **kwargs)
        self.percent = percent
        if self.percent > 1:
            self.percent /= 100
        self.seed = seed

    def split_df(self, default: DataFrame, *args, **kwargs) -> Dict[str, object]:
        train, test = train_test_split(
            default, train_size=self.percent, random_state=self.seed
        )
        return {"train": train, "test": test}

    def split_spf(self, default: PySparkDataFrame, *args, **kwargs):
        train, test = default.randomSplit(
            [1 - self.percent, self.percent], seed=self.seed
        )
        return {"train": train, "test": test}
