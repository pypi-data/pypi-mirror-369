from typing import List

from pandas import DataFrame
from pyspark.sql import DataFrame as PySparkDataFrame
from pyspark.sql import functions as F

from seshat.data_class import SFrame, GroupSFrame
from seshat.data_class.pandas import DFrame
from seshat.general import configs
from seshat.transformer import Transformer


class SFrameTrimmer(Transformer):
    """
    Interface for trimmer, specially set handler name to `trim` for all other trimmers.
    """

    HANDLER_NAME = "trim"
    DEFAULT_FRAME = DFrame
    DEFAULT_GROUP_KEYS = {"default": configs.DEFAULT_SF_KEY}

    def __init__(self, group_keys=None, address_cols=None):
        super().__init__(group_keys)
        self.address_cols = address_cols


class ZeroAddressTrimmer(SFrameTrimmer):
    """
    This trimmer will remove zero address from input sframe.
    """

    def __init__(
        self,
        group_keys=None,
        address_cols=None,
        zero_address=configs.ZERO_ADDRESS,
    ):
        super().__init__(group_keys, address_cols)

        self.zero_address = zero_address
        if address_cols is None:
            self.address_cols = [configs.FROM_ADDRESS_COL, configs.TO_ADDRESS_COL]
        else:
            self.address_cols = address_cols

    def calculate_complexity(self):
        return 1

    def trim_df(self, default: DataFrame, *args, **kwargs):
        for address_col in self.address_cols:
            default = default[default[address_col] != self.zero_address]

        default.reset_index(inplace=True, drop=True)
        return {"default": default}

    def trim_spf(self, default: PySparkDataFrame):
        for address_col in self.address_cols:
            default = default.filter(F.col(address_col) != self.zero_address)

        return {"default": default}


class LowTransactionTrimmer(SFrameTrimmer):
    """
    Responsible for drop addresses that has low transaction based on specified minimum.
    """

    def __init__(
        self,
        group_keys=None,
        address_cols=None,
        exclusive_on_each: bool = False,
        min_transaction_num: int = None,
        min_quantile: float = None,
    ):
        super().__init__(group_keys)
        if address_cols is None:
            self.address_cols = [configs.FROM_ADDRESS_COL, configs.TO_ADDRESS_COL]
        else:
            self.address_cols = address_cols
        self.exclusive_on_each = exclusive_on_each
        self.min_transaction_num = min_transaction_num
        self.min_quantile = min_quantile

    def calculate_complexity(self):
        return 1

    def trim_df(self, default: DataFrame, *args, **kwargs):
        unique_user_set = {}
        for address_col in self.address_cols:
            df_agg = default.groupby(address_col).size().reset_index(name="count")
            if self.min_transaction_num:
                df_agg = df_agg[df_agg["count"] >= self.min_transaction_num]
            elif self.min_quantile:
                threshold_min = df_agg["count"].quantile(self.min_quantile)
                df_agg = df_agg[df_agg["count"] > threshold_min]

            if self.exclusive_on_each:
                default = default[default[address_col].isin(df_agg[address_col])]
            else:
                unique_user_set = (
                    set(df_agg[address_col].unique())
                    if len(unique_user_set) == 0
                    else unique_user_set.intersection(set(df_agg[address_col].unique()))
                )

        if not self.exclusive_on_each:
            for address_col in self.address_cols:
                default = default[default[address_col].isin(unique_user_set)]
        default.reset_index(inplace=True, drop=True)
        return {"default": default}

    def trim_spf(self, default: PySparkDataFrame, *args, **kwargs):
        unique_user_set = set()
        for address_col in self.address_cols:
            agg = default.groupby(address_col).agg(F.count("*").alias("count"))

            if self.min_transaction_num:
                agg = agg.filter(F.col("count") >= self.min_transaction_num)
            elif self.min_transaction_num:
                threshold_min = agg.approxQuantile("count", [self.min_quantile], 0.05)[
                    0
                ]
                agg = agg.filter(F.col("count") > threshold_min)

            filtered = set(agg.select(address_col).rdd.flatMap(lambda x: x).collect())

            if self.exclusive_on_each:
                default = default.filter(F.col(address_col).isin(filtered))
            else:
                unique_user_set = (
                    filtered
                    if len(unique_user_set) == 0
                    else unique_user_set.intersection(filtered)
                )

        if not self.exclusive_on_each:
            unique_user_ls = list(unique_user_set)
            for address_col in self.address_cols:
                default = default.filter(F.col(address_col).isin(unique_user_ls))

        return {"default": default}


class FeatureTrimmer(SFrameTrimmer):
    """
    Feature Trimmer will drop all columns except the feature columns that get as params.
    """

    def __init__(self, group_keys=None, columns=None):
        super().__init__(group_keys)

        if columns is None:
            self.columns = [
                configs.CONTRACT_ADDRESS_COL,
                configs.FROM_ADDRESS_COL,
                configs.TO_ADDRESS_COL,
                configs.AMOUNT_PRICE_COL,
                configs.BLOCK_NUM_COL,
            ]
        else:
            self.columns = columns

    def calculate_complexity(self):
        return 1

    def trim_df(self, default: DataFrame, *args, **kwargs):
        default = default.drop(
            [col for col in default.columns if col not in set(self.columns)],
            axis=1,
        )
        return {"default": default}

    def trim_spf(self, default: PySparkDataFrame, *args, **kwargs):
        default = default.select(*self.columns)
        return {"default": default}


class ContractTrimmer(SFrameTrimmer):
    """
    This trimmer will be used to based on the function find the top contract address and just
    keep these contract addresses and drop all others.

    Parameters
    ----------
    contract_list_fn : callable
        The function that is used to find contract addresses
    contract_list_args : tuple
        The args that passed to contract list func
    contract_list_kwargs : dict
        The awards that must be passed to the contract list func
    exclude: bool
        The flag that shows the condition computed contract address must be kept to exclude
    contract_address_col : str
        The column of contract address in default sframe
    """

    def __init__(
        self,
        contract_list_fn,
        group_keys=None,
        contract_list_args=(),
        contract_list_kwargs=None,
        exclude=False,
        contract_address_col=configs.CONTRACT_ADDRESS_COL,
    ):
        super().__init__(group_keys)

        if contract_list_kwargs is None:
            contract_list_kwargs = {}

        self.contract_list_fn = contract_list_fn
        self.contract_list_args = contract_list_args
        self.contract_list_kwargs = contract_list_kwargs
        self.exclude = exclude
        self.contract_address_col = contract_address_col

    def calculate_complexity(self):
        return 1

    def trim_df(self, default: DataFrame, *args, **kwargs):
        contract_list = self.contract_list_fn(
            default, *self.contract_list_args, **self.contract_list_kwargs
        )
        condition = default[self.contract_address_col].isin(contract_list)
        if self.exclude:
            condition = ~condition
        default = default[condition]
        return {"default": default}

    def trim_spf(self, default: PySparkDataFrame, *args, **kwargs):
        contract_list = self.contract_list_fn(
            default, *self.contract_list_args, **self.contract_list_kwargs
        )

        condition = F.col(self.contract_address_col).isin(contract_list)
        if self.exclude:
            condition = ~condition
        default = default.filter(condition)
        return {"default": default}


class DuplicateTrimmer(SFrameTrimmer):
    def __init__(self, subset: List[str] = None, group_keys=None, *args, **kwargs):
        super().__init__(group_keys, *args, **kwargs)
        self.subset = subset

    def trim_df(self, default: DataFrame, *args, **kwargs):
        default = default.drop_duplicates(subset=self.subset)
        return {"default": default}

    def trim_spf(self, default: PySparkDataFrame, *args, **kwargs):
        default = default.dropDuplicates(subset=self.subset)
        return {"default": default}


class NaNTrimmer(SFrameTrimmer):
    def __init__(
        self, subset: List[str] = None, group_keys=None, how="all", *args, **kwargs
    ):
        super().__init__(group_keys, *args, **kwargs)
        self.subset = subset
        self.how = how

    def calculate_complexity(self):
        return 1

    def trim_df(self, default: DataFrame, *args, **kwargs):
        default = default.dropna(subset=self.subset, how=self.how)
        return {"default": default}

    def trim_spf(self, default: PySparkDataFrame, *args, **kwargs):
        default = default.dropna(subset=self.subset, how=self.how)
        return {"default": default}


class GroupTrimmer(SFrameTrimmer):
    """
    This trimmer will remove the default sf from the group sframe.
    """

    ONLY_GROUP = True

    def calculate_complexity(self):
        return 1

    def __call__(self, sf_input: SFrame, *args: object, **kwargs: object) -> SFrame:
        sf_output: GroupSFrame = sf_input.from_raw(**self.get_from_raw_kwargs(sf_input))
        sf_output.children.pop(self.default_sf_key)
        return sf_output


class InclusionTrimmer(SFrameTrimmer):
    """
    Inclusion trimmer drop rows from default that exists in other.
    Also with exclude arg condition will be excluded.
    """

    ONLY_GROUP = True
    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "other": configs.OTHER_SF_KEY,
    }

    def __init__(
        self,
        default_col: str = configs.CONTRACT_ADDRESS_COL,
        other_col: str = configs.CONTRACT_ADDRESS_COL,
        exclude: bool = True,
        group_keys=None,
        *args,
        **kwargs,
    ):
        super().__init__(group_keys, *args, **kwargs)
        self.default_col = default_col
        self.other_col = other_col
        self.exclude = exclude

    def calculate_complexity(self):
        return 1

    def trim_df(self, default: DataFrame, other: DataFrame, *args, **kwargs):
        condition = default[self.default_col].isin(other[self.other_col])
        if self.exclude:
            condition = ~condition
        default = default[condition]
        default = default.reset_index(drop=True)
        return {"default": default, "other": other}

    def trim_spf(
        self, default: PySparkDataFrame, other: PySparkDataFrame, *args, **kwargs
    ):
        values = [
            row[self.other_col]
            for row in other.select(self.other_col).distinct().collect()
        ]
        condition = F.col(self.default_col).isin(values)
        if self.exclude:
            condition = ~condition

        default = default.filter(condition)
        return {"default": default, "other": other}


class FilterTrimmer(SFrameTrimmer):
    def __init__(
        self,
        group_keys=None,
        col=None,
        op=None,
        value=None,
        conditions=None,
        combine_method="and",
    ):
        super().__init__(group_keys)
        self.col = col
        self.op = op
        self.value = value
        self.conditions = conditions if conditions else []
        self.combine_method = combine_method

        if col and op and value is not None:
            self.conditions = [{"col": col, "op": op, "value": value}]

        self.valid_operators = {
            "=": lambda df_col, val: df_col == val,
            "!=": lambda df_col, val: df_col != val,
            ">": lambda df_col, val: df_col > val,
            ">=": lambda df_col, val: df_col >= val,
            "<": lambda df_col, val: df_col < val,
            "<=": lambda df_col, val: df_col <= val,
            "in": lambda df_col, val: df_col.isin(val),
            "not in": lambda df_col, val: ~df_col.isin(val),
            "contains": lambda df_col, val: df_col.str.contains(val, na=False),
            "startswith": lambda df_col, val: df_col.str.startswith(val, na=False),
            "endswith": lambda df_col, val: df_col.str.endswith(val, na=False),
        }

        self.spark_operators = {
            "=": lambda col, val: F.col(col) == val,
            "!=": lambda col, val: F.col(col) != val,
            ">": lambda col, val: F.col(col) > val,
            ">=": lambda col, val: F.col(col) >= val,
            "<": lambda col, val: F.col(col) < val,
            "<=": lambda col, val: F.col(col) <= val,
            "in": lambda col, val: F.col(col).isin(val),
            "not in": lambda col, val: ~F.col(col).isin(val),
            "contains": lambda col, val: F.col(col).contains(val),
            "startswith": lambda col, val: F.col(col).startswith(val),
            "endswith": lambda col, val: F.col(col).endswith(val),
        }

        self._validate_conditions()

    def calculate_complexity(self):
        return 2

    def _validate_conditions(self):
        if not self.conditions:
            return

        valid_operators = list(self.valid_operators.keys())

        for condition in self.conditions:
            if not all(k in condition for k in ["col", "op", "value"]):
                raise ValueError(
                    "Each condition must have 'col', 'op', and 'value' keys"
                )

            if condition["op"] not in valid_operators:
                raise ValueError(f"Operator must be one of {valid_operators}")

            if condition["op"] in ["in", "not in"] and not isinstance(
                condition["value"], (list, tuple)
            ):
                raise ValueError(
                    f"Value for '{condition['op']}' operator must be a list or tuple"
                )

    def _apply_conditions(self, df, operators, is_spark=False):
        if not self.conditions:
            return df

        combined = None
        for condition in self.conditions:
            col = condition["col"]
            op = condition["op"]
            value = condition["value"]

            condition_func = operators[op]
            condition_result = (
                condition_func(df[col], value)
                if not is_spark
                else condition_func(col, value)
            )
            if combined is None:
                combined = condition_result
            elif self.combine_method == "and":
                combined = combined & condition_result
            else:
                combined = combined | condition_result

        if is_spark:
            return df.filter(combined)
        else:
            filtered_df = df[combined]
            filtered_df.reset_index(inplace=True, drop=True)
            return filtered_df

    def trim_df(self, default: DataFrame, *args, **kwargs):
        return {
            "default": self._apply_conditions(
                default, self.valid_operators, is_spark=False
            )
        }

    def trim_spf(self, default: PySparkDataFrame, *args, **kwargs):
        return {
            "default": self._apply_conditions(
                default, self.spark_operators, is_spark=True
            )
        }


class ChangeColumnNameTrimmer(SFrameTrimmer):
    """
    Change Column Name Trimmer will change the name of columns.
    """

    def __init__(self, group_keys=None, columns_map=None):
        super().__init__(group_keys)

        self.columns_map = columns_map

    def trim_df(self, default: DataFrame, *args, **kwargs):
        if self.columns_map is not None:
            default = default.rename(columns=self.columns_map)

        return {"default": default}

    def trim_spf(self, default: PySparkDataFrame, *args, **kwargs):
        # ToDo: add spf
        return {"default": default}
