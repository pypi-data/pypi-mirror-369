from datetime import timedelta
from typing import Any, Callable, Dict, List, Literal, Tuple

import pandas as pd
from pandas import DataFrame
from pyspark.sql import DataFrame as PySparkDataFrame
from pyspark.sql import Window
from pyspark.sql import functions as F
from pyspark.sql.functions import array, array_distinct, array_union, coalesce, lit
from pyspark.sql.types import IntegerType, StructField, StructType

from seshat.data_class import SFrame, SPFrame
from seshat.data_class.base import GroupSFrame
from seshat.data_class.pandas import DFrame
from seshat.general import configs
from seshat.general.exceptions import InvalidArgumentsError
from seshat.transformer import Transformer
from seshat.transformer.merger import Merger
from seshat.transformer.schema import Col, Schema
from seshat.transformer.trimmer.base import FilterTrimmer
from seshat.utils import pandas_func, pyspark_func
from seshat.utils.validation import NumericColumnValidator, TimeStampColumnValidator

SYMBOLS_RECEIVED_COL = "symbols_received"
SYMBOLS_SENT_COL = "symbols_sent"


class SFrameDeriver(Transformer):
    """
    Interface for deriver, specially set handler name to `derive` for all other derivers.
    """

    ONLY_GROUP = False
    HANDLER_NAME = "derive"
    DEFAULT_FRAME = DFrame


class SFrameFromColsDeriver(SFrameDeriver):
    """
    This class is used to create new sframe from specific columns of default sframes.
    If input is contained only one sframe the result is group sframe with two children.

    Parameters
    ----------
    cols : list of str
        List of columns in the default sframe to transformation must apply of them.
    result_col : str
        Column name of result values in address sframe
    """

    ONLY_GROUP = False
    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "address": configs.ADDRESS_SF_KEY,
    }

    def __init__(
        self,
        group_keys=None,
        cols=(configs.FROM_ADDRESS_COL, configs.TO_ADDRESS_COL),
        result_col="extracted_value",
    ):
        super().__init__(group_keys)
        self.cols = cols
        self.result_col = result_col

    def calculate_complexity(self):
        return 1

    def validate(self, sf: SFrame):
        super().validate(sf)
        self._validate_columns(sf, self.default_sf_key, *self.cols)

    def derive_df(self, default: DataFrame, *args, **kwargs) -> Dict[str, DataFrame]:
        new_df = DataFrame()

        new_df[self.result_col] = pd.unique(default[[*self.cols]].values.ravel())
        new_df[self.result_col] = new_df[self.result_col].astype(
            default[self.cols[0]].dtype
        )
        new_df.dropna(subset=[self.result_col], inplace=True)
        return {"default": default, "address": new_df}

    def derive_spf(
        self, default: PySparkDataFrame, *args, **kwargs
    ) -> Dict[str, PySparkDataFrame]:
        temp_spf = default.withColumn(
            self.result_col, F.explode(F.array(*[F.col(c) for c in self.cols]))
        )
        address = temp_spf.select(self.result_col).distinct()
        return {"default": default, "address": address}


class FeatureForAddressDeriver(SFrameDeriver):
    """
    This class is responsible for adding a new column as a new feature to address the sframe
    based on the default sframe.

    Parameters
    ----------
    default_index_col : str
        Columns that group by default will be applied based on this column.
    address_index_col: str
        Column in the address that must be matched to address_col in default sframe.
        Joining default and address sframe using this column and address_col to
        join new column to address.
    result_col : str
        Column name for a new column in address sframe
    agg_func: str
        Function name that aggregation operates based on it. For example count, sum, mean, etc.
    """

    ONLY_GROUP = True
    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "address": configs.ADDRESS_SF_KEY,
    }

    def __init__(
        self,
        value_col,
        group_keys=None,
        default_index_col: str | List[str] = configs.FROM_ADDRESS_COL,
        address_index_col: str | List[str] = configs.ADDRESS_COL,
        result_col="result_col",
        agg_func="mean",
        is_numeric=True,
    ):
        super().__init__(group_keys)

        self.value_col = value_col
        self.default_index_col = default_index_col
        self.address_index_col = address_index_col
        self.result_col = result_col
        self.agg_func = agg_func
        self.is_numeric = is_numeric

    def calculate_complexity(self):
        return 5

    def validate(self, sf: SFrame):
        super().validate(sf)
        self._validate_columns(sf, self.group_keys["default"], self.value_col)
        if isinstance(self.address_index_col, list):
            self._validate_columns(
                sf, self.group_keys["address"], *self.address_index_col
            )
        else:
            self._validate_columns(
                sf, self.group_keys["address"], self.address_index_col
            )

    def derive_df(
        self, default: DataFrame, address: DataFrame, *args, **kwargs
    ) -> Dict[str, DataFrame]:
        if self.is_numeric:
            NumericColumnValidator().validate(default, self.value_col)

        zero_value = pandas_func.get_zero_value(default[self.value_col])
        default.fillna({self.value_col: zero_value}, inplace=True)

        df_agg = (
            default.groupby(self.default_index_col)[self.value_col]
            .agg(self.agg_func)
            .reset_index(name=self.result_col)
        )

        if isinstance(self.default_index_col, str):
            should_dropped = [self.default_index_col]
        else:
            should_dropped = set(self.default_index_col) - set(self.address_index_col)

        address = address.merge(
            df_agg,
            right_on=self.default_index_col,
            left_on=self.address_index_col,
            how="left",
        ).drop(should_dropped, axis=1)

        result_zero_value = pandas_func.get_zero_value(address[self.result_col])
        address.fillna({self.result_col: result_zero_value}, inplace=True)
        return {"default": default, "address": address}

    def derive_spf(
        self, default: PySparkDataFrame, address: PySparkDataFrame, *args, **kwargs
    ) -> Dict[str, PySparkDataFrame]:
        try:
            func = getattr(F, self.agg_func)
        except AttributeError:
            raise AttributeError(
                "agg func %s not available for pyspark dataframe" % self.agg_func
            )
        if self.is_numeric:
            default = NumericColumnValidator().validate(default, self.value_col)

        zero_value = pyspark_func.get_zero_value(default, self.value_col)
        default = default.fillna({self.value_col: zero_value})

        agg_value = (
            default.groupBy(self.default_index_col)
            .agg(func(F.col(self.value_col)).alias(self.result_col))
            .withColumnRenamed(self.default_index_col, self.address_index_col)
        )
        address = address.join(agg_value, on=self.address_index_col, how="left")
        zero_value = pyspark_func.get_zero_value(address, self.result_col)
        address = address.fillna(zero_value, subset=[self.result_col])

        return {"default": default, "address": address}


class OperationOnColsDeriver(SFrameDeriver):
    """
    This deriver does some operation on two different columns of default sframe


    Parameters
    ----------
    cols: list of str
        List of column names that operation must be applied on them
    result_col: str
        Column name of result column
    agg_func: str
        Aggregation function name that operates on specified columns.

    """

    ONLY_GROUP = False
    DEFAULT_GROUP_KEYS = {"default": configs.DEFAULT_SF_KEY}

    def __init__(
        self,
        group_keys=None,
        cols=(configs.AMOUNT_COL,),
        result_col="interacted_value",
        agg_func: str | Callable = "mean",
        is_numeric=False,
    ):
        super().__init__(group_keys)
        self.cols = cols
        self.result_col = result_col
        self.agg_func = agg_func
        self.is_numeric = is_numeric

    def calculate_complexity(self):
        return 15

    def validate(self, sf: SFrame):
        super().validate(sf)
        self._validate_columns(sf, self.default_sf_key, *self.cols)

    def derive_df(self, default: DataFrame, *args, **kwargs):
        if self.is_numeric:
            for col in self.cols:
                default = NumericColumnValidator().validate(default, col)
        if isinstance(self.agg_func, str):
            default[self.result_col] = default[[col for col in self.cols]].agg(
                self.agg_func, axis=1
            )
        else:
            default[self.result_col] = default.apply(self.agg_func, axis=1)

        return {"default": default}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        if self.is_numeric:
            for col in self.cols:
                default = NumericColumnValidator().validate(default, col)
        try:
            func = pyspark_func.func_maps[self.agg_func]
        except KeyError:
            raise KeyError(
                "func %s not available for pyspark dataframe" % self.agg_func
            )
        func_udf = F.udf(func)
        default = default.withColumn(self.result_col, func_udf(*self.cols))
        if self.is_numeric:
            default = NumericColumnValidator().validate(default, self.result_col)
        return {"default": default}


class PercentileTransactionValueDeriver(SFrameDeriver):
    """
    Used to compute percentile of the specific column and insert result as a new column.

    Parameters
    ----------
    value_col: str
        The column that computing percentile will execute on it.
    quantile_probabilities: list of float
        List of quantile probabilities
    result_col: str
        Column name of result column
    """

    def __init__(
        self,
        group_keys=None,
        value_col=configs.AMOUNT_COL,
        result_col="percentile",
        quantile_probabilities=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9),
    ):
        super().__init__(group_keys)

        self.value_col = value_col
        self.result_col = result_col
        self.quantile_probabilities = quantile_probabilities

    def calculate_complexity(self):
        return 2

    def validate(self, sf: SFrame):
        super().validate(sf)
        self._validate_columns(sf, self.default_sf_key, self.value_col)

    def derive_df(self, default: DataFrame, *args, **kwargs) -> Dict[str, DataFrame]:
        default = NumericColumnValidator().validate(default, self.value_col)

        quantiles = default[self.value_col].quantile(
            self.quantile_probabilities, interpolation="linear"
        )
        percentile = pandas_func.PandasPercentile(
            quantiles, self.quantile_probabilities
        )
        default[self.result_col] = default[self.value_col].apply(percentile)
        return {"default": default}

    def derive_spf(
        self, default: PySparkDataFrame, *args, **kwargs
    ) -> Dict[str, PySparkDataFrame]:
        default = NumericColumnValidator().validate(default, self.value_col)

        quantiles = default.approxQuantile(
            self.value_col, self.quantile_probabilities, 0.05
        )

        def get_percentile(value):
            for i, quantile in enumerate(quantiles):
                if value <= quantile:
                    return int(self.quantile_probabilities[i] * 100)
            return 100

        get_percentile_udf = F.udf(get_percentile, IntegerType())
        default = default.withColumn(
            self.result_col, get_percentile_udf(F.col(self.value_col))
        )
        return {"default": default}


class InteractedSymbolsToSentenceDeriver(SFrameDeriver):
    """
    This deriver joins symbols that each user in address sframe
    be interacted with it into a new column in string type.
    If already sent symbols or received symbols are calculated as an array of symbol strings
    deriver use them otherwise compute these columns.

    Parameters
    ----------
    symbol_col: str
        Column name of a symbol column in default sframe
    from_address_col: str
        Column name of from address column in default sframe
    to_address_col: str
        Column name of to address column in default sframe
    address_address_col: str
        Column name of address column in address sframe. This column
        consider as a joining condition between default and address sframe
    sent_symbols_col : str
        Column name for the result of sent symbols column in address sframe. If this parameter is set to None
        sent symbols are computed and this value as a new column name.
    received_symbols_col : str
        Column name for the result of received symbols column in address sframe. If this parameter is set to None
        received symbols are computed and this value is a new column name.
    total_symbols_col : str
        Column name for merged two columns sent_symbols and received_symbols.
    result_col: str
        Column name of interacted symbols column
    """

    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "address": configs.ADDRESS_SF_KEY,
    }

    def __init__(
        self,
        group_keys=None,
        symbol_col=configs.SYMBOL_COL,
        from_address_col=configs.FROM_ADDRESS_COL,
        to_address_col=configs.TO_ADDRESS_COL,
        address_address_col=configs.ADDRESS_COL,
        sent_symbols_col=None,
        received_symbols_col=None,
        total_symbols_col=None,
        result_col=None,
    ):
        super().__init__(group_keys)

        self.symbol_col = symbol_col
        self.from_address_col = from_address_col
        self.to_address_col = to_address_col
        self.address_address_col = address_address_col
        self.sent_symbols_col = sent_symbols_col
        self.received_symbols_col = received_symbols_col
        self.total_symbols_col = total_symbols_col
        self.result_col = result_col

    def calculate_complexity(self):
        return 5

    def validate(self, sf: SFrame):
        super().validate(sf)
        if self.sent_symbols_col is None:
            self._validate_columns(sf, self.default_sf_key, self.from_address_col)
        if self.received_symbols_col is None:
            self._validate_columns(sf, self.default_sf_key, self.to_address_col)

    def derive_df(
        self, address: DataFrame, default: DataFrame = None, *args, **kwargs
    ) -> Dict[str, DataFrame]:
        if self.sent_symbols_col is None:
            group_sf = GroupSFrame(
                children={
                    "default": DFrame.from_raw(default),
                    "address": DFrame.from_raw(address),
                }
            )

            address = (
                FeatureForAddressDeriver(
                    self.symbol_col,
                    self.group_keys,
                    self.from_address_col,
                    self.address_address_col,
                    SYMBOLS_SENT_COL,
                    "unique",
                    is_numeric=False,
                )(group_sf)
                .get(self.group_keys["address"])
                .to_raw()
            )

        if self.received_symbols_col is None:
            group_sf = GroupSFrame(
                children={
                    "default": DFrame.from_raw(default),
                    "address": DFrame.from_raw(address),
                }
            )
            address = (
                FeatureForAddressDeriver(
                    self.symbol_col,
                    self.group_keys,
                    self.to_address_col,
                    self.address_address_col,
                    SYMBOLS_RECEIVED_COL,
                    "unique",
                    is_numeric=False,
                )(group_sf)
                .get(self.group_keys["address"])
                .to_raw()
            )

        final_sent_col = self.sent_symbols_col or SYMBOLS_SENT_COL
        final_received_col = self.received_symbols_col or SYMBOLS_RECEIVED_COL

        address[final_sent_col] = address[final_sent_col].fillna("").apply(list)
        address[final_received_col] = address[final_received_col].fillna("").apply(list)

        address[self.result_col] = address.apply(
            lambda row: ", ".join(set(row[final_sent_col] + row[final_received_col])),
            axis=1,
        )
        return {"default": default, "address": address}

    def derive_spf(
        self,
        address: PySparkDataFrame,
        default: PySparkDataFrame = None,
        *args,
        **kwargs,
    ) -> Dict[str, PySparkDataFrame]:
        if self.sent_symbols_col is None:
            group_sframe = GroupSFrame(
                children={
                    "default": SPFrame.from_raw(default),
                    "address": SPFrame.from_raw(address),
                }
            )

            address = (
                FeatureForAddressDeriver(
                    self.symbol_col,
                    self.group_keys,
                    self.from_address_col,
                    self.address_address_col,
                    SYMBOLS_SENT_COL,
                    "collect_set",
                    is_numeric=False,
                )(group_sframe)
                .get(self.group_keys["address"])
                .to_raw()
            )

        if self.received_symbols_col is None:
            group_sframe = GroupSFrame(
                children={
                    "default": SPFrame.from_raw(default),
                    "address": SPFrame.from_raw(address),
                }
            )
            address = (
                FeatureForAddressDeriver(
                    self.symbol_col,
                    self.group_keys,
                    self.to_address_col,
                    self.address_address_col,
                    SYMBOLS_RECEIVED_COL,
                    "collect_set",
                    is_numeric=False,
                )(group_sframe)
                .get(self.group_keys["address"])
                .to_raw()
            )
        final_sent_col = self.sent_symbols_col or SYMBOLS_SENT_COL
        final_received_col = self.received_symbols_col or SYMBOLS_RECEIVED_COL

        address = address.withColumn(
            final_sent_col, coalesce(final_received_col, array())
        )

        address = address.withColumn(
            self.result_col,
            F.concat_ws(
                ", ",
                array_distinct(array_union(final_received_col, final_sent_col)),
            ),
        )

        return {"default": default, "address": address}


class SenderReceiverTokensDeriver(SFrameDeriver):
    """
    This will find tokens that in at least one record be from_address or to_address.
    The result will save in another sf.
    """

    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "other": configs.OTHER_SF_KEY,
    }

    def __init__(
        self,
        group_keys=None,
        address_cols=(configs.FROM_ADDRESS_COL, configs.TO_ADDRESS_COL),
        contract_address_col=configs.CONTRACT_ADDRESS_COL,
        result_col=configs.CONTRACT_ADDRESS_COL,
        *args,
        **kwargs,
    ):
        super().__init__(group_keys, *args, **kwargs)
        self.address_cols = address_cols
        self.contract_address = contract_address_col
        self.result_col = result_col

    def calculate_complexity(self):
        return 2

    def derive_df(self, default: DataFrame, *args, **kwargs):
        all_tokens = set(default[self.contract_address].tolist())
        addresses = set()
        for address_col in self.address_cols:
            addresses |= set(default[address_col].tolist())

        sender_receiver_tokens = list(addresses & all_tokens)
        other = pd.DataFrame(data={self.result_col: sender_receiver_tokens})
        return {"default": default, "other": other}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        all_tokens = set(
            default.select(self.contract_address).rdd.flatMap(lambda x: x).collect()
        )
        addresses = set()
        for address_col in self.address_cols:
            addresses |= set(
                default.select(address_col).rdd.flatMap(lambda x: x).collect()
            )

        sender_receiver_tokens = list(addresses & all_tokens)
        schema = StructType(
            [
                StructField(
                    self.result_col, default.schema[self.contract_address].dataType
                )
            ]
        )

        data = [{self.result_col: addr} for addr in sender_receiver_tokens]
        other = SPFrame.get_spark().createDataFrame(schema=schema, data=data)
        return {"default": default, "other": other}


class TokenLastPriceDeriver(SFrameDeriver):
    """
    This deriver finds the last usd unit price for every token if there is not zero and no null amount USD.
    To find the last price deriver needs to sort values based on the timestamp column.
    If dtype of this column is something
    except for valid datetime type, the column values will be converted to the proper type.
    """

    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "result": configs.TOKEN_PRICE_SF_KEY,
    }

    def __init__(
        self,
        contract_address_col=configs.CONTRACT_ADDRESS_COL,
        timestamp_col=configs.BLOCK_TIMESTAMP_COL,
        amount_col=configs.AMOUNT_COL,
        amount_usd_col=configs.AMOUNT_USD_COL,
        result_unit_price_col=configs.TOKEN_PRICE_COL,
        group_keys=None,
        *args,
        **kwargs,
    ):
        super().__init__(group_keys, *args, **kwargs)
        self.contract_address_col = contract_address_col
        self.timestamp_col = timestamp_col
        self.amount_col = amount_col
        self.amount_usd_col = amount_usd_col
        self.result_unit_price_col = result_unit_price_col

    def calculate_complexity(self):
        return 1

    def derive_df(self, default: pd.DataFrame, *args, **kwargs):
        default = TimeStampColumnValidator().validate(default, self.timestamp_col)
        price = default[default[self.amount_usd_col] != 0]
        price = price.sort_values(self.timestamp_col, ascending=False)
        price = price.dropna(subset=[self.amount_usd_col])
        last_price = (
            price.groupby([self.contract_address_col]).head(1).reset_index(drop=True)
        ).reset_index(drop=True)

        last_price[self.result_unit_price_col] = (
            last_price["amount_usd"] / last_price["amount"]
        )
        last_price = last_price[[self.contract_address_col, self.result_unit_price_col]]
        return {"default": default, "result": last_price}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        default = TimeStampColumnValidator().validate(default, self.timestamp_col)
        price: PySparkDataFrame = default.filter(
            F.col(self.amount_usd_col) != 0
        ).select(
            self.timestamp_col,
            self.contract_address_col,
            self.amount_usd_col,
            self.amount_col,
        )
        price = price.dropna(subset=[self.amount_usd_col])
        window = Window.partitionBy(self.contract_address_col).orderBy(
            F.col(self.timestamp_col).desc()
        )
        last_price = (
            price.withColumn("_row_number", F.row_number().over(window))
            .filter(F.col("_row_number") == 1)
            .drop("_row_number")
        )
        last_price = last_price.withColumn(
            self.result_unit_price_col,
            last_price[self.amount_usd_col] / last_price[self.amount_col],
        )
        last_price = last_price.select(
            self.contract_address_col, self.result_unit_price_col
        )
        return {"default": default, "result": last_price}


class ProfitLossDeriver(SFrameDeriver):
    """
    Find the profit and loss of addresses with this logic:
    Sum over all buying and selling amount & amount USD, then find the difference between
    buy & sell amount for each address & token. By using the token price sframe the current amount
    of address property will be calculated. The difference between USD that address paid and
    the current amount is the PL for that address & token.

    Parameters
    ----------
    from_address_col : str
        The name of from address column in default sf.
    to_address_col : str
        The name of to address column in default sf.
    contract_address_col : str
        The name of contract address column in default sf.
    timestamp_col : str
        The name of block_timestamp column in default sf.
    amount_col : str
        The name of amount column in default sf.
    amount_usd_col : str
        The name of USD amount column of transactions in default sf.
    token_price_col : str
        The name of price column in price sf.
    address_col : str
        The name of address column in result sf.
    net_amount_col : str
        The name of net amount column in result sf.
    net_amount_usd_col : str
        The name of USD net amount column in result sf.
    current_amount_usd_col : str
        The name of USD amount column in result sf.
    pl_col : str
        The name of profit & loss column in result sf.
    group_keys
        Group keys for the parent Transformer class.
    *args
        Additional positional arguments.
    **kwargs
        Additional keyword arguments.
    """

    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "price": configs.TOKEN_PRICE_SF_KEY,
        "result": configs.PROFIT_LOSS_SF_KEY,
    }

    def __init__(
        self,
        from_address_col=configs.FROM_ADDRESS_COL,
        to_address_col=configs.TO_ADDRESS_COL,
        contract_address_col=configs.CONTRACT_ADDRESS_COL,
        timestamp_col=configs.BLOCK_TIMESTAMP_COL,
        amount_col=configs.AMOUNT_COL,
        amount_usd_col=configs.AMOUNT_USD_COL,
        token_price_col=configs.TOKEN_PRICE_COL,
        address_col=configs.ADDRESS_COL,
        net_amount_col="net_amount",
        net_amount_usd_col="net_amount_usd",
        current_amount_usd_col="current_amount_usd",
        pl_col="pl",
        group_keys=None,
        *args,
        **kwargs,
    ):
        super().__init__(group_keys, *args, **kwargs)
        self.from_address_col = from_address_col
        self.to_address_col = to_address_col
        self.contract_address_col = contract_address_col
        self.timestamp_col = timestamp_col
        self.amount_col = amount_col
        self.amount_usd_col = amount_usd_col
        self.token_price_col = token_price_col
        self.address_col = address_col
        self.net_amount_col = net_amount_col
        self.net_amount_usd_col = net_amount_usd_col
        self.current_amount_usd_col = current_amount_usd_col
        self.pl_col = pl_col

    def calculate_complexity(self):
        return 15

    def validate(self, sf: SFrame):
        super().validate(sf)
        self._validate_columns(
            sf,
            "default",
            self.from_address_col,
            self.to_address_col,
            self.contract_address_col,
            self.timestamp_col,
            self.amount_col,
            self.amount_usd_col,
        )

    def derive_df(self, default: pd.DataFrame, price: pd.DataFrame, *args, **kwargs):
        clean_default = default[default[self.amount_col] != 0]
        selling = (
            clean_default.groupby([self.from_address_col, self.contract_address_col])
            .agg({self.amount_col: "sum", self.amount_usd_col: "sum"})
            .reset_index()
            .rename(
                columns={
                    self.from_address_col: self.address_col,
                    self.amount_col: "sell_amount",
                    self.amount_usd_col: "sell_amount_usd",
                }
            )
        )
        buying = (
            clean_default.groupby([self.to_address_col, self.contract_address_col])
            .agg({self.amount_col: "sum", self.amount_usd_col: "sum"})
            .reset_index()
            .rename(
                columns={
                    self.to_address_col: self.address_col,
                    self.amount_col: "buy_amount",
                    self.amount_usd_col: "buy_amount_usd",
                }
            )
        )
        investing = pd.merge(
            selling, buying, on=[self.address_col, self.contract_address_col]
        )
        del selling
        del buying
        investing[self.net_amount_col] = (
            investing["buy_amount"] - investing["sell_amount"]
        )
        investing[self.net_amount_usd_col] = (
            investing["buy_amount_usd"] - investing["sell_amount_usd"]
        )
        investing = investing[
            [
                self.address_col,
                self.contract_address_col,
                self.net_amount_col,
                self.net_amount_usd_col,
            ]
        ]
        investing = investing[investing[self.net_amount_col] >= 0]

        investing = investing.merge(price, on=self.contract_address_col)
        investing[self.current_amount_usd_col] = (
            investing[self.net_amount_col] * investing[self.token_price_col]
        )

        investing[self.pl_col] = (
            investing[self.current_amount_usd_col] - investing[self.net_amount_usd_col]
        )
        investing = investing.drop(columns=[self.token_price_col])

        return {"default": default, "price": price, "result": investing}

    def derive_spf(
        self, default: PySparkDataFrame, price: PySparkDataFrame, *args, **kwargs
    ):
        clean_default = default.filter(F.col(self.amount_col) != 0)
        selling = (
            clean_default.groupBy([self.from_address_col, self.contract_address_col])
            .agg({self.amount_col: "sum", self.amount_usd_col: "sum"})
            .withColumnRenamed(self.from_address_col, self.address_col)
            .withColumnRenamed(f"sum({self.amount_col})", "sell_amount")
            .withColumnRenamed(f"sum({self.amount_usd_col})", "sell_amount_usd")
        )

        buying = (
            clean_default.groupBy([self.to_address_col, self.contract_address_col])
            .agg({self.amount_col: "sum", self.amount_usd_col: "sum"})
            .withColumnRenamed(self.to_address_col, self.address_col)
            .withColumnRenamed(f"sum({self.amount_col})", "buy_amount")
            .withColumnRenamed(f"sum({self.amount_usd_col})", "buy_amount_usd")
        )

        investing = selling.join(
            buying, on=[self.address_col, self.contract_address_col]
        )

        investing = investing.withColumn(
            self.net_amount_col, investing["buy_amount"] - investing["sell_amount"]
        ).withColumn(
            self.net_amount_usd_col,
            investing["buy_amount_usd"] - investing["sell_amount_usd"],
        )

        investing = investing.select(
            self.address_col,
            self.contract_address_col,
            self.net_amount_col,
            self.net_amount_usd_col,
        )
        investing = investing.filter(F.col(self.net_amount_col) >= 0)
        investing = investing.join(price, on=self.contract_address_col)

        investing = Schema(
            exclusive=False,
            cols=[
                Col(self.net_amount_col, dtype="double"),
                Col(self.net_amount_usd_col, dtype="double"),
                Col(self.token_price_col, dtype="double"),
            ],
        )(SPFrame.from_raw(investing)).to_raw()

        investing = investing.withColumn(
            self.current_amount_usd_col,
            investing[self.net_amount_col] * investing[self.token_price_col],
        )
        investing = investing.withColumn(
            self.pl_col,
            investing[self.current_amount_usd_col] - investing[self.net_amount_usd_col],
        )
        investing = investing.drop(self.token_price_col)
        return {"default": default, "price": price, "result": investing}


class FractionDeriver(SFrameDeriver):
    """
    Find fraction that each rows have from sum of all calculation columns values.

    Parameters
    ----------
    calculation_col : str
        The column that every value of it divide by sum of it over all rows
    result_fraction_col : str
        The column name for result fraction values
    group_keys
        Group keys for the parent Transformer class.
    *args
        Additional positional arguments.
    **kwargs
        Additional keyword arguments.
    """

    DEFAULT_GROUP_KEYS = {
        "default": configs.TOKEN_SF_KEY,
    }

    def __init__(
        self,
        calculation_col: str,
        result_fraction_col: str = "weight",
        group_keys=None,
        *args,
        **kwargs,
    ):
        super().__init__(group_keys, *args, **kwargs)
        self.calculation_col = calculation_col
        self.result_fraction_col = result_fraction_col

    def calculate_complexity(self):
        return 2

    def validate(self, sf: SFrame):
        super().validate(sf)
        self._validate_columns(sf, self.default_sf_key, self.calculation_col)

    def derive_df(self, default: pd.DataFrame, *args, **kwargs):
        default = NumericColumnValidator().validate(default, self.calculation_col)
        default[self.calculation_col] = default[self.calculation_col].fillna(0)
        total_value = default[self.calculation_col].sum()

        default[self.result_fraction_col] = default[self.calculation_col] / total_value
        return {"default": default}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        default = NumericColumnValidator().validate(default, self.calculation_col)
        default = default.fillna(0, subset=[self.calculation_col])
        total_value = default.agg(F.sum(self.calculation_col)).collect()[0][0]
        default = default.withColumn(
            self.result_fraction_col, F.col(self.calculation_col) / F.lit(total_value)
        )
        return {"default": default}


class ChangingOverTimeDeriver(SFrameDeriver):
    DEFAULT_GROUP_KEYS = {"default": configs.DEFAULT_SF_KEY, "result": "result"}

    def __init__(
        self,
        index_col: str,
        value_col: str,
        result_changing_col: str,
        timestamp_col: str = configs.BLOCK_TIMESTAMP_COL,
        group_keys=None,
        *args,
        **kwargs,
    ):
        super().__init__(group_keys, *args, **kwargs)
        self.index_col = index_col
        self.value_col = value_col
        self.result_changing_col = result_changing_col
        self.timestamp_col = timestamp_col

    def calculate_complexity(self):
        return 15

    def derive_df(self, default: pd.DataFrame, *args, **kwargs):
        default = TimeStampColumnValidator().validate(default, self.timestamp_col)

        sorted_default = default.sort_values(self.timestamp_col, ascending=False)
        sorted_default = sorted_default[
            [self.index_col, self.value_col, self.timestamp_col]
        ]
        top = (
            sorted_default.groupby(self.index_col)
            .first()
            .reset_index()
            .rename(columns={self.value_col: "top"})
        )
        sorted_default = sorted_default.sort_values(self.timestamp_col)
        bottom = (
            sorted_default.groupby(self.index_col)
            .first()
            .reset_index()
            .rename(columns={self.value_col: "bottom"})
        )

        result = pd.merge(top, bottom, on=self.index_col)
        result[self.result_changing_col] = (result["top"] + result["bottom"]) / result[
            "bottom"
        ]

        result = result[[self.index_col, self.result_changing_col]]

        result = result.dropna(subset=[self.result_changing_col])

        return {"default": default, "result": result}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        default = TimeStampColumnValidator().validate(default, self.timestamp_col)
        sorted_default = default.sort(F.desc(self.timestamp_col)).select(
            self.index_col, self.value_col, self.timestamp_col
        )
        top = sorted_default.groupBy(self.index_col).agg(
            F.first(self.value_col).alias("top")
        )
        sorted_default = default.orderBy(self.timestamp_col).select(
            self.index_col, self.value_col, self.timestamp_col
        )
        bottom = sorted_default.groupBy(self.index_col).agg(
            F.first(self.value_col).alias("bottom")
        )

        result = top.join(bottom, on=self.index_col)
        result = result.withColumn(
            self.result_changing_col, (F.col("top") + F.col("bottom")) / F.col("bottom")
        )
        result = result.select(self.index_col, self.result_changing_col)

        result = result.dropna(subset=[self.result_changing_col])
        return {"default": default, "result": result}


class GroupByDeriverMeanMax(SFrameDeriver):
    """
    GroupBy Deriver will provide aggregation over different columns.
    """

    def __init__(
        self,
        group_keys=None,
        function=None,
        by_columns=None,
        agg_column=None,
        output_name=None,
    ):
        super().__init__(group_keys)

        if function is None:
            self.function = "mean"
        else:
            self.function = function
        self.by_columns = by_columns
        self.agg_column = agg_column
        if output_name is None:
            self.output_name = "agg_" + self.function
        else:
            self.output_name = output_name

    def derive_df(self, default: DataFrame, *args, **kwargs):
        if self.by_columns is not None and self.agg_column is not None:

            # ToDo: cover more aggregated function
            if self.function == "max":
                agg_df = (
                    default.groupby(self.by_columns)[self.agg_column]
                    .max()
                    .reset_index()
                )
            else:
                agg_df = (
                    default.groupby(self.by_columns)[self.agg_column]
                    .mean()
                    .reset_index()
                )
            agg_df = agg_df.fillna(0)

            agg_df = agg_df.rename(
                columns={self.agg_column: self.agg_column + "-" + self.function}
            )

            return {"default": default, self.output_name: agg_df}
        else:
            return {"default": default}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        # ToDo: add spf
        return {"default": default}


class TimeWindowTransformer(SFrameDeriver):
    """
    A class that derives time series-based features from a default SFrame using a transformer and merger strategy.
    It supports applying transformations over multiple durations and combines the results using a merger.

    Duration labeling can be handled in two ways:
    1. By adding a new column with the name specified in `label_col`, where each row is labeled with its corresponding duration.
    2. By appending the duration label as a suffix to the names of the new columns created by the transformer, excluding those required for merging.

    This behavior is controlled by the `specify_duration_by` parameter.

    Parameters
    ----------
    transformer : Transformer or Callable
        An instance of a transformer or a callable function that performs the transformation on the input data.
    merger : Merger
        An instance of a merger used to combine features generated across different durations.
    time_col : str, optional
        The name of the timestamp column in the SFrame. Defaults to `configs.BLOCK_TIMESTAMP_COL`.
    durations : List[Tuple[str, int]]
        A list of (label, duration) pairs where each label identifies a time window (in minutes) for feature extraction.
    label_col : str, optional
        The name of the column that will store the duration label for each record. Defaults to `configs.DURATION_LABEL_COL`.
    specify_duration_by : {'column', 'suffix'}, default 'column'
        Specifies how duration information is represented in the output:
        * 'column' – Adds a new column (named by `label_col`) containing the duration label.
        * 'suffix' – Appends the duration label as a suffix to the names of columns created by the transformer,
          excluding those required by the merger.
    """

    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "timeseries_feature": configs.TIMESERIES_SF_KEY,
    }

    def __init__(
        self,
        transformer: Transformer | Callable,
        merger: Merger,
        durations: List[Tuple[str, int]],
        time_col=configs.BLOCK_TIMESTAMP_COL,
        label_col=configs.DURATION_LABEL_COL,
        specify_duration_by: Literal["column", "suffix"] = "column",
        group_keys=None,
    ):
        super().__init__(group_keys)
        self.time_col = time_col
        self.transformer = transformer
        self.label_col = label_col
        self.merger = merger
        self.specify_duration_by = specify_duration_by
        self.durations = durations

        # Ensure that the merge works in place and group keys are set to their default values.
        self.merger.inplace = True
        self.merger.group_keys = {"default": "default", "other": "other"}
        if self.specify_duration_by == "column":
            self.merger.axis = 0

    def validate(self, sf: SFrame):
        super().validate(sf)
        self._validate_columns(sf, self.group_keys["default"], self.time_col)

    def _is_empty(self, sf: SFrame) -> bool:
        raw = sf.to_raw()
        if raw is None:
            return True
        elif hasattr(raw, "rdd"):
            return raw.rdd.isEmpty()
        else:
            return len(raw) == 0

    def calculate_metrics(self, sf: SFrame, label, start) -> SFrame:
        trimmer = FilterTrimmer(op=">=", col=self.time_col, value=start)
        filtered = trimmer(sf)

        if self._is_empty(filtered):
            return filtered

        result = self.transformer(sf_input=filtered, label=label, start=start)
        if self.specify_duration_by == "column":
            deriver = StaticValueColumnAdder(col_name=self.label_col, value=label)
            result = deriver(result)

        else:
            # Find columns excluding those used by,
            # the merger for merging.
            cols = set(result[self.transformer].get_columns()) - set(self.merger.on)
            schema = Schema(
                cols=[Col(col, to=f"{col}_{label}") for col in cols],
                exclusive=False,
            )
            result = schema(result)
        return result

    def derive_df(self, default: DataFrame, *args, **kwargs):
        default = TimeStampColumnValidator().validate(default, self.time_col)
        last_timestamp = default[self.time_col].max()
        sf_input = DFrame.from_raw(default)
        result = DFrame()
        return self.derive(sf_input, result, last_timestamp)

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        default = TimeStampColumnValidator().validate(default, self.time_col)
        last_timestamp = default.select(F.max(self.time_col)).collect()[0][0]
        sf_input = SPFrame.from_raw(default)
        result = SPFrame()
        return self.derive(sf_input, result, last_timestamp)

    def derive(self, sf_input: SFrame, result: SFrame, last_timestamp):
        intervals = {
            label: last_timestamp - timedelta(minutes=minutes)
            for label, minutes in self.durations
        }

        for idx, (label, start) in enumerate(intervals.items()):
            metrics = self.calculate_metrics(sf_input, label, start)
            if self._is_empty(metrics):
                continue
            metrics = metrics.make_group()
            metrics["other"] = metrics["default"]
            metrics["default"] = result
            result = (
                metrics["other"]
                if self._is_empty(result)
                else self.merger(metrics)["default"]
            )

        return {
            "default": sf_input[self.default_sf_key].to_raw(),
            "timeseries_feature": result.to_raw(),
        }


class StaticValueColumnAdder(SFrameDeriver):
    """
    A deriver that adds a new column with a static value to a DataFrame.

    This class allows adding a column with either a fixed value or a value generated
    by a function. It supports both pandas DataFrame and PySpark DataFrame.

    Parameters
    ----------
    col_name : str
        The name of the column to be added to the DataFrame.
    value : Any, optional
        The static value to be added to the column. Either this or value_function must be provided.
    value_function : Callable[[], Any], optional
        A function that returns the value to be added to the column. Either this or value must be provided.
    group_keys : dict, optional
        Dictionary mapping group names to their respective keys.

    Raises
    ------
    InvalidArgumentsError
        If neither value nor value_function is provided.

    Examples
    --------
    >>> # Add a column with a static value
    >>> adder = StaticValueColumnAdder(col_name="status", value="active")
    >>> result = adder.derive(dataframe)

    >>> # Add a column with a value from a function
    >>> adder = StaticValueColumnAdder(col_name="timestamp", value_function=lambda: datetime.now())
    >>> result = adder.derive(dataframe)
    """

    def __init__(
        self,
        col_name: str,
        value: Any = None,
        value_function: Callable[[], Any] = None,
        group_keys=None,
    ):
        super().__init__(group_keys)

        self.col_name = col_name
        if not value and not value_function:
            raise InvalidArgumentsError(
                "Either 'value' or 'value_func' must be provided."
            )

        self.value = value
        self.value_func = value_function

    def derive_df(self, default: DataFrame, *args, **kwargs):
        """
        Add a static value column to a pandas DataFrame.

        Parameters
        ----------
        default : DataFrame
            The pandas DataFrame to which the column will be added.
        *args : tuple
            Variable length argument list.
        **kwargs : dict
            Arbitrary keyword arguments.

        Returns
        -------
        dict
            A dictionary with key 'default' containing the modified DataFrame.
        """
        default[self.col_name] = self._get_value()
        return {"default": default}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        """
        Add a static value column to a PySpark DataFrame.

        Parameters
        ----------
        default : PySparkDataFrame
            The PySpark DataFrame to which the column will be added.
        *args : tuple
            Variable length argument list.
        **kwargs : dict
            Arbitrary keyword arguments.

        Returns
        -------
        dict
            A dictionary with key 'default' containing the modified PySpark DataFrame.
        """
        return {"default": default.withColumn(self.col_name, lit(self._get_value()))}

    def _get_value(self):
        return self.value if self.value else self.value_func()


class DateTimeTypeDeriver(SFrameDeriver):
    """
    DateTime Type Deriver will change the type of an object column to a datetime column.
    """

    def __init__(self, group_keys=None, columns=None):
        super().__init__(group_keys)

        self.columns = columns

    def derive_df(self, default: DataFrame, *args, **kwargs):
        if self.columns is not None:
            for column in self.columns:
                default[column] = pd.to_datetime(default[column])

        return {"default": default}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        # ToDo: add spf
        return {"default": default}


class GroupByTimeWindowDeriver(SFrameDeriver):
    """
    GroupBy Time Window Deriver will provide aggregation over different columns and different time windows.
    """

    def __init__(
        self,
        group_keys=None,
        by_columns=None,
        agg_column=None,
        time_column=None,
        window_list=None,
        func_list=None,
        new_agg_column_list=None,
        output_name=None,
    ):
        super().__init__(group_keys)

        self.by_columns = by_columns
        self.agg_column = agg_column
        self.time_column = time_column
        self.window_list = window_list
        self.func_list = func_list
        self.new_agg_column_list = new_agg_column_list
        if output_name is None:
            self.output_name = "agg_window_time"
        else:
            self.output_name = output_name

    def derive_df(self, default: DataFrame, *args, **kwargs):
        if (
            self.by_columns is not None
            and self.agg_column is not None
            and self.time_column is not None
            and self.window_list is not None
            and self.func_list is not None
        ):

            merged_df = None
            for window, func, new_agg_column in zip(
                self.window_list,
                self.func_list,
                self.new_agg_column_list,
            ):

                # Set the start time of the window
                latest_time = default[self.time_column].max()
                start_time = latest_time - window
                filtered_df = default[(default[self.time_column] >= start_time)]

                if func == "count":
                    agg_df = (
                        filtered_df.groupby(self.by_columns)[self.agg_column]
                        .count()
                        .reset_index()
                    )
                elif func == "max":
                    agg_df = (
                        filtered_df.groupby(self.by_columns)[self.agg_column]
                        .max()
                        .reset_index()
                    )
                else:
                    agg_df = (
                        filtered_df.groupby(self.by_columns)[self.agg_column]
                        .mean()
                        .reset_index()
                    )

                agg_df = agg_df.fillna(0)

                agg_df.rename(columns={self.agg_column: new_agg_column}, inplace=True)

                if merged_df is None:
                    merged_df = agg_df
                else:
                    merged_df = pd.merge(
                        merged_df, agg_df, on=self.by_columns, how="outer"
                    ).fillna(0)

            return {"default": default, self.output_name: merged_df}
        else:
            return {"default": default}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        # ToDo: add spf
        return {"default": default}


class GroupByDeriverCount(SFrameDeriver):
    """
    GroupBy Deriver Count will provide aggregation over different columns.
    """

    def __init__(
        self,
        group_keys=None,
        by_columns: list = None,
        kept_column: list = None,
        output_name=None,
    ):
        super().__init__(group_keys)

        self.by_columns = by_columns
        self.kept_column = kept_column
        if output_name is None:
            self.output_name = "agg_count"
        else:
            self.output_name = output_name

    def derive_df(self, default: DataFrame, *args, **kwargs):
        if self.by_columns is not None:

            kept_column_tuples = [(item, "first") for item in self.kept_column]

            # Creating the aggregation dictionary dynamically
            agg_dict = {
                result_name: (col_name, agg_func)
                for (col_name, agg_func), result_name in zip(
                    kept_column_tuples, self.kept_column
                )
            }

            # Adding COUNT to the aggregation
            agg_dict["COUNT"] = (self.by_columns[0], "size")

            # Aggregating
            aggregated_df = (
                default.groupby(self.by_columns).agg(**agg_dict).reset_index()
            )

            return {"default": default, self.output_name: aggregated_df}
        else:
            return {"default": default}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        # ToDo: add spf
        return {"default": default}


class OneColumnPercentileFilterDeriver(SFrameDeriver):
    """
    OneColumnPercentileFilterDeriver
    """

    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "count_aggregated_df": "count_aggregated_df",
    }

    def __init__(
        self,
        group_keys=None,
        column_name=None,
        percentile=0.9,
        output_name=None,
    ):
        super().__init__(group_keys)

        self.column_name = column_name
        self.percentile = percentile
        if output_name is None:
            self.output_name = "percentile_filter"
        else:
            self.output_name = output_name

    def derive_df(
        self, default: DataFrame, count_aggregated_df: DataFrame, *args, **kwargs
    ):
        if self.column_name is not None:
            # Calculate the percentile
            percentile_value = count_aggregated_df[self.column_name].quantile(
                self.percentile
            )

            # Filter the DataFrame
            top_percent_df = count_aggregated_df[
                count_aggregated_df[self.column_name] >= percentile_value
            ]

            return {"default": default, self.output_name: top_percent_df}
        else:
            return {"default": default}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        # ToDo: add spf
        return {"default": default}


class ComprehensiveFeaturesDeriver(SFrameDeriver):
    """
    OneColumnPercentileFilterDeriver
    """

    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "count_aggregated_df": "count_aggregated_df",
        "filtered_count_aggregated_df": "filtered_count_aggregated_df",
    }

    def __init__(
        self,
        group_keys=None,
        output_name=None,
    ):
        super().__init__(group_keys)

        if output_name is None:
            self.output_name = "comprehensive"
        else:
            self.output_name = output_name

    def derive_df(
        self,
        default: DataFrame,
        count_aggregated_df: DataFrame,
        filtered_count_aggregated_df: DataFrame,
        *args,
        **kwargs,
    ):
        def calculate_features(df):

            # Group by TOKEN_ADDRESS to calculate features
            features = (
                df.groupby("TOKEN_ADDRESS")
                .agg(
                    SYMBOL=("SYMBOL", "first"),
                    total_transactions=("TOKEN_ADDRESS", "count"),
                    unique_from_wallets=("FROM_WALLET", "nunique"),
                    unique_to_wallets=("TO_WALLET", "nunique"),
                    total_volume_precise=("AMOUNT_PRECISE", "sum"),
                    total_volume_usd=("AMOUNT_USD", "sum"),
                    avg_transaction_size_precise=("AMOUNT_PRECISE", "mean"),
                    avg_transaction_size_usd=("AMOUNT_USD", "mean"),
                    median_transaction_size_precise=("AMOUNT_PRECISE", "median"),
                    median_transaction_size_usd=("AMOUNT_USD", "median"),
                    min_transaction_size_precise=("AMOUNT_PRECISE", "min"),
                    max_transaction_size_precise=("AMOUNT_PRECISE", "max"),
                    min_transaction_size_usd=("AMOUNT_USD", "min"),
                    max_transaction_size_usd=("AMOUNT_USD", "max"),
                    price_change=(
                        "TOKEN_PRICE",
                        lambda x: (x.iloc[-1] - x.iloc[0]) if len(x) > 1 else 0,
                    ),
                    price_volatility=("TOKEN_PRICE", "std"),
                    first_price=("TOKEN_PRICE", "first"),
                    last_price=("TOKEN_PRICE", "last"),
                    transaction_count_hourly=(
                        "BLOCK_TIMESTAMP",
                        lambda x: (
                            len(x) / ((x.max() - x.min()).total_seconds() / 3600)
                            if (x.max() > x.min())
                            else len(x)
                        ),
                    ),
                )
                .reset_index()
            )

            # Add calculated features that need multiple steps
            features["whale_transactions"] = (
                df[df["AMOUNT_USD"] > 10000].groupby("TOKEN_ADDRESS").size()
            )
            features["whale_transactions"] = (
                features["whale_transactions"].fillna(0).astype(int)
            )

            features["unique_wallets"] = (
                features["unique_from_wallets"] + features["unique_to_wallets"]
            )

            # Replace NaN with 0
            features = features.fillna(0)

            # Round all float columns to 2 decimal places
            features = features.round(2)

            return features

        default = default[
            default["TOKEN_ADDRESS"].isin(
                set(filtered_count_aggregated_df["TOKEN_ADDRESS"])
            )
        ]

        features_df = calculate_features(default)

        features_df = features_df.drop(columns=["TOKEN_ADDRESS"])

        return {"default": default, self.output_name: features_df}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        # ToDo: add spf
        return {"default": default}


class TokenSwapTradeDeriver(SFrameDeriver):
    """
    This will create a dataframe with aggregated trade data per token.
    """

    def __init__(
        self,
        group_keys=None,
        output_name=None,
        time_intervals_trade=None,
        *args,
        **kwargs,
    ):
        super().__init__(group_keys, *args, **kwargs)
        if output_name is None:
            self.output_name = "token_swap_trade_df"
        else:
            self.output_name = output_name
        self.time_intervals_trade = time_intervals_trade

    def derive_df(self, default: DataFrame, *args, **kwargs):

        # SWAP DATA
        df = default.copy()
        # Change columns names to make them compatible with general trading approach
        df.rename(
            columns={
                "AMOUNT_IN": "AMOUNT_OUTFLOW",
                "AMOUNT_OUT": "AMOUNT_INFLOW",
                "TOKEN_IN": "TOKEN_OUTFLOW",
                "TOKEN_OUT": "TOKEN_INFLOW",
                "SYMBOL_IN": "SYMBOL_OUTFLOW",
                "SYMBOL_OUT": "SYMBOL_INFLOW",
            },
            inplace=True,
        )
        df = df[
            [
                "BLOCK_TIMESTAMP",
                "AMOUNT_OUTFLOW",
                "AMOUNT_INFLOW",
                "TOKEN_OUTFLOW",
                "TOKEN_INFLOW",
                "SYMBOL_OUTFLOW",
                "SYMBOL_INFLOW",
            ]
        ]

        # Convert BLOCK_TIMESTAMP to datetime
        df["BLOCK_TIMESTAMP"] = pd.to_datetime(df["BLOCK_TIMESTAMP"])

        # Get the last timestamp in the dataframe
        last_timestamp = df["BLOCK_TIMESTAMP"].max()

        intervals = {}
        for interval_label, hour_value in zip(
            self.time_intervals_trade["last_labels"],
            self.time_intervals_trade["hour_values"],
        ):
            intervals[interval_label] = last_timestamp - timedelta(hours=hour_value)

        # Initialize the final dataframe
        final_df = pd.DataFrame()

        # Function to calculate metrics for a given time interval
        def calculate_metrics(interval_start, interval_label):
            filtered_df = df[df["BLOCK_TIMESTAMP"] >= interval_start]

            # Group by TOKEN_INFLOW and calculate metrics
            token_in_df = filtered_df.groupby("TOKEN_INFLOW", as_index=False).agg(
                VOLUME_INFLOW=("AMOUNT_INFLOW", "sum"),
                TRADE_COUNT_INFLOW=("TOKEN_INFLOW", "size"),
            )
            token_in_df.rename(columns={"TOKEN_INFLOW": "TOKEN"}, inplace=True)

            # Group by TOKEN_OUTFLOW and calculate metrics
            token_out_df = filtered_df.groupby("TOKEN_OUTFLOW", as_index=False).agg(
                VOLUME_OUTFLOW=("AMOUNT_OUTFLOW", "sum"),
                TRADE_COUNT_OUTFLOW=("TOKEN_OUTFLOW", "size"),
            )
            token_out_df.rename(columns={"TOKEN_OUTFLOW": "TOKEN"}, inplace=True)

            # Merge the two dataframes on TOKEN
            merged_df = pd.merge(token_in_df, token_out_df, on="TOKEN", how="outer")

            # Add SYMBOL using the first appearance of SYMBOL_INFLOW or SYMBOL_OUTFLOW
            symbol_map_in = (
                filtered_df.groupby("TOKEN_INFLOW")["SYMBOL_INFLOW"].first().to_dict()
            )
            symbol_map_out = (
                filtered_df.groupby("TOKEN_OUTFLOW")["SYMBOL_OUTFLOW"].first().to_dict()
            )
            symbol_map = {**symbol_map_out, **symbol_map_in}
            merged_df["SYMBOL"] = merged_df["TOKEN"].map(symbol_map)

            # Fill NaN values with 0 for counts and metrics
            merged_df.fillna(0, inplace=True)

            # Rename columns to include the interval label
            for column in [
                "VOLUME_INFLOW",
                "TRADE_COUNT_INFLOW",
                "VOLUME_OUTFLOW",
                "TRADE_COUNT_OUTFLOW",
            ]:
                merged_df.rename(
                    columns={column: f"{column}_{interval_label}"}, inplace=True
                )

            return merged_df

        # Process each interval and merge the results
        for interval_label, interval_start in intervals.items():
            metrics_df = calculate_metrics(interval_start, interval_label)
            if final_df.empty:
                final_df = metrics_df
            else:
                # Merge new metrics into the final dataframe
                final_df = pd.merge(
                    final_df, metrics_df, on=["TOKEN", "SYMBOL"], how="outer"
                )

        # Fill any remaining NaN values with 0
        final_df.fillna(0, inplace=True)

        # ToDo: remove duplicate token SYMBOLS: only keep the one with higher number of transactions

        return {"default": default, self.output_name: final_df}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        # ToDo: add spf
        return {"default": default}


class TokenPriceDeriver(SFrameDeriver):
    """
    This will create a dataframe with aggregated price data per token.
    """

    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "token_swap_trade_df": "token_swap_trade_df",
    }

    def __init__(
        self,
        group_keys=None,
        output_name=None,
        time_intervals_price=None,
        *args,
        **kwargs,
    ):
        super().__init__(group_keys, *args, **kwargs)
        if output_name is None:
            self.output_name = "token_price_df"
        else:
            self.output_name = output_name
        self.time_intervals_price = time_intervals_price

    def derive_df(
        self, default: DataFrame, token_swap_trade_df: DataFrame, *args, **kwargs
    ):

        # PRICE DATA
        # ToDo Fix this: how to read multiple source files at the beginning?
        import os

        df = pd.read_csv(os.getenv("CSV_EZ_PRICES_HOURLY"))
        df.rename(columns={"TOKEN_ADDRESS": "TOKEN", "HOUR": "TIME"}, inplace=True)
        df = df[["TOKEN", "TIME", "PRICE"]]

        # Ensure data is sorted by TOKEN and TIME
        df = df.sort_values(by=["TOKEN", "TIME"]).reset_index(drop=True)

        # Create the new dataframe with the required columns
        result = df.copy()
        result["CURRENT_PRICE"] = result["PRICE"]

        for interval_label, hour_value in zip(
            self.time_intervals_price["ago_labels"],
            self.time_intervals_price["hour_values"],
        ):
            result[f"PRICE_{interval_label}"] = result.groupby("TOKEN")["PRICE"].shift(
                hour_value
            )

        # Keep only the latest row for each TOKEN
        final_df_price = result.groupby("TOKEN").last().reset_index()

        # Remove TIME and PRICE from the final result
        final_df_price = final_df_price.drop(columns=["TIME", "PRICE"])

        # MERGE price and trade

        # Merge the two dataframes on TOKEN
        final_merged_df = pd.merge(
            token_swap_trade_df, final_df_price, on="TOKEN", how="inner"
        )
        final_merged_df.rename(columns={"TOKEN": "TOKEN_ADDRESS"}, inplace=True)
        final_merged_df.rename(
            columns={"SYMBOL": "TOKEN_COIN_NAME_SYMBOL"}, inplace=True
        )

        return {"default": default, self.output_name: final_merged_df}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        # ToDo: add spf
        return {"default": default}


class TokenFeatureTransformationDeriver(SFrameDeriver):
    """
    This will create a dataframe with different token features from price and swap trades.
    """

    DEFAULT_GROUP_KEYS = {
        "default": configs.DEFAULT_SF_KEY,
        "token_price_df": "token_price_df",
    }

    def __init__(
        self,
        group_keys=None,
        output_name=None,
        time_intervals_trade=None,
        time_intervals_price=None,
        *args,
        **kwargs,
    ):
        super().__init__(group_keys, *args, **kwargs)
        if output_name is None:
            self.output_name = "token_feature_transformation_df"
        else:
            self.output_name = output_name
        self.time_intervals_trade = time_intervals_trade
        self.time_intervals_price = time_intervals_price

    def derive_df(self, default: DataFrame, token_price_df: DataFrame, *args, **kwargs):
        epsilon = 1e-10  # Small constant to prevent division by zero

        df = token_price_df.copy()

        for interval_label in self.time_intervals_price["ago_labels"]:

            df[f"Price_Change_Percentage_{interval_label}"] = (
                df["CURRENT_PRICE"] - df[f"PRICE_{interval_label}"]
            ) / df[f"PRICE_{interval_label}"]

        for interval_label in self.time_intervals_trade["last_labels"]:

            df[f"Buy_to_Sell_Volume_Ratio_{interval_label}"] = df[
                f"VOLUME_INFLOW_{interval_label}"
            ] / (df[f"VOLUME_OUTFLOW_{interval_label}"] + epsilon)

            df[f"Buy_to_Sell_Trade_Count_Ratio_{interval_label}"] = df[
                f"TRADE_COUNT_INFLOW_{interval_label}"
            ] / (df[f"TRADE_COUNT_OUTFLOW_{interval_label}"] + epsilon)

            df[f"TRADE_COUNT_TOTAL_{interval_label}"] = (
                df[f"TRADE_COUNT_INFLOW_{interval_label}"]
                + df[f"TRADE_COUNT_OUTFLOW_{interval_label}"]
            )

            df[f"TRADE_COUNT_PERCENTAGE_OVERALL_{interval_label}"] = (
                df[f"TRADE_COUNT_TOTAL_{interval_label}"]
                / df[f"TRADE_COUNT_TOTAL_{interval_label}"].sum()
            )

            # this is the column I will use to filter and remove low liquidity tokens, so pick top 200
            df[f"TRADE_COUNT_RANK_OVERALL_{interval_label}"] = (
                df[f"TRADE_COUNT_PERCENTAGE_OVERALL_{interval_label}"]
                .rank(ascending=False, method="dense")
                .astype(int)
            )

        # this is the one that is used to rank tokens
        df["Profitability_Score"] = (
            0.5 * df["Price_Change_Percentage_6_hours_ago"]
            + 0.3 * df["Buy_to_Sell_Volume_Ratio_last_6_hours"]
            + 0.2 * df["Buy_to_Sell_Trade_Count_Ratio_last_6_hours"]
        )

        df = df.fillna(0)

        # Round all decimal values to four decimal places
        df = df.round(4)

        # Filter and remove all tokens with the Price of 0
        df = df[df["CURRENT_PRICE"] > 0]

        # Convert all column names to lowercase
        df.columns = df.columns.str.lower()

        return {"default": default, self.output_name: df}

    def derive_spf(self, default: PySparkDataFrame, *args, **kwargs):
        # ToDo: add spf
        return {"default": default}
