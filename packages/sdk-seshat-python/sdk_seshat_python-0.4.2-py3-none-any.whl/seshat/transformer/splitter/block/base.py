from typing import Dict

from pandas import DataFrame

from seshat.general import configs
from seshat.general.exceptions import ColDoesNotExistError
from seshat.transformer.splitter import Splitter
from seshat.utils.validation import NumericColumnValidator


class BlockSplitter(Splitter):
    def __init__(
        self,
        percent=0.8,
        block_num_col=configs.BLOCK_NUM_COL,
        group_keys=None,
        *args,
        **kwargs
    ):
        super().__init__(group_keys=group_keys, *args, **kwargs)
        self.block_num_col = block_num_col
        self.percent = percent

    def split_df(self, default: DataFrame, *args, **kwargs) -> Dict[str, object]:
        if self.block_num_col not in default.columns:
            raise ColDoesNotExistError((self.block_num_col,))

        default = NumericColumnValidator().validate(default, self.block_num_col)
        cutoff_block_number = int(
            default[self.block_num_col].min()
            + (
                (default[self.block_num_col].max() - default[self.block_num_col].min())
                * self.percent
            )
        )
        df_train = default[default[self.block_num_col] < cutoff_block_number]
        df_test = default[default[self.block_num_col] >= cutoff_block_number]

        return {"train": df_train, "test": df_test}
