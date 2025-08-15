from dataclasses import dataclass
from typing import List, Literal

from pandas import DataFrame
from pyspark.sql import DataFrame as PySparkDataFrame
from pyspark.sql.functions import col as pyspark_col

from seshat.data_class import SFrame
from seshat.general.exceptions import ColIdNotSpecifiedError
from seshat.transformer import Transformer

UpdateFuncs = Literal["sum", "mean", "replace"]


@dataclass
class Col:
    """
    A dataclass representing column-specific transformations within a dataframe.

    Attributes
    ----------
    original : str
        The original name of the column in the data source.
    to : str
        The destination name for the column after transformation.
        If no renaming is needed, this must be None.
    dtype : type
        The target data type to which the column should be converted
        during the transformation process.
    is_id : bool
        This column is usefully when trying to identify each row
    """

    original: str
    to: str = None
    dtype: str = None
    is_id: bool = False
    update_func: UpdateFuncs = None


class Schema(Transformer):
    """
    A transformer class designed to modify the structure and data types
    of raw data frames. This class takes raw data as input and each column
    in the data can be renamed, have its data type changed, or be dropped
    if not specified in the columns list when the schema is set to 'exclusive'.

    Parameters
    ----------
    cols : list of Col
        A list of `Col` objects that define the transformations for each column.
        Transformations can include renaming the column and changing its data type.

    exclusive : bool
        If set to True, any columns not explicitly included in the `cols` list
        will be dropped from the data frame. If False, unspecified columns
        will be retained in their original form.

    """

    HANDLER_NAME = "convert"

    def __init__(
        self,
        cols: List[Col],
        exclusive: bool = True,
        convert_type: bool = True,
        group_keys=None,
    ):
        super().__init__(group_keys)

        self.cols = cols
        self.exclusive = exclusive
        self.convert_type = convert_type

    def calculate_complexity(self):
        return 1

    def validate(self, sf: SFrame):
        super().validate(sf)
        self._validate_columns(sf, self.group_keys["default"], *self.selected_cols)

    def convert_df(self, default: DataFrame, *args, **kwargs):
        if self.exclusive:
            default = default[[*self.selected_cols]]

        for col in self.cols:
            if col.dtype and self.convert_type:
                if col.dtype.startswith("datetime"):
                    default[col.original] = (
                        default[col.original].str.replace("Z", "").replace("z", "")
                    )
                default[col.original] = default[col.original].astype(col.dtype)
            if col.to:
                default = default.rename(columns={col.original: col.to})

        return {"default": default}

    def convert_spf(self, default: PySparkDataFrame, *args, **kwargs):
        if self.exclusive:
            default = default.select(*self.selected_cols)

        for col in self.cols:
            if col.dtype and self.convert_type:
                default = default.withColumn(
                    col.original, pyspark_col(col.original).cast(col.dtype)
                )
            if col.to:
                default = default.withColumnRenamed(col.original, col.to)

        return {"default": default}

    @property
    def selected_cols(self) -> List[str]:
        return [col.original for col in self.cols]

    @property
    def selected_cols_str(self, delimiter=",") -> str:
        return delimiter.join(self.selected_cols)

    def get_id(self, return_first=True) -> Col | List[Col]:
        ids = []
        for col in self.cols:
            if col.is_id and return_first:
                return col
            elif col.is_id:
                ids.append(col)
        if ids:
            return ids
        raise ColIdNotSpecifiedError()
