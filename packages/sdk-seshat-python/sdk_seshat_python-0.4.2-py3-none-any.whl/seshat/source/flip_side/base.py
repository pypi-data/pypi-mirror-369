import hashlib
import os.path
from threading import Thread
from typing import Callable, Optional

from seshat.source.mixins import SQLMixin
from seshat.general import configs
from seshat.general.exceptions import InvalidArgumentsError, EmptyDataError
from seshat.data_class import SFrame
from seshat.source import Source
from seshat.source.exceptions import (
    FlipSideRateLimitError,
    FlipSideQueryError,
    FlipSideApiError,
)
from seshat.source.local import LocalSource
from seshat.utils.file import save_to_csv
from seshat.utils.memory import get_obj_memory_size

_has_flipside = False
try:
    from flipside import Flipside
    from flipside.errors import QueryRunRateLimitError, QueryRunExecutionError, ApiError

    _has_flipside = True
except ImportError:
    Flipside, QueryRunRateLimitError, QueryRunExecutionError, ApiError = (
        None,
        None,
        None,
        None,
    )

STORE_DIRECTORY = "flipside"


class FlipSideSource(SQLMixin, Source):
    """
    A source class that fetches paginated data from Flipside.
    This class handles the retrieval of data page by page
    and each page's results are saved to a uniquely named file.

    The `FlipsideSource` is designed to manage large datasets that
    cannot be fetched in a single request, ensuring efficient
    handling and storage of fetched data.
    """

    api_key: str
    url: str
    _client: Flipside = None
    query_fn: Callable[..., str] = None
    page_size: int
    max_age_minutes: int
    timeout_minutes: int
    store_path: str
    _stored_index: int = 0
    id_col: str = "tx_hash"
    single_item_size: int = None
    loaded_df: SFrame = None
    filters: Optional[dict]
    table_name: str

    def __init__(
        self,
        api_key,
        url=configs.FLIPSIDE_URL,
        query=None,
        query_fn=None,
        max_age_minutes=31 * 24 * 60,
        timeout_minutes=None,
        store_path=None,
        page_size=40000,
        schema=None,
        filters=None,
        table_name="ethereum.core.ez_token_transfers",
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        if query and query_fn:
            raise InvalidArgumentsError(
                "Both query and query_fn cannot be used together"
            )

        self.filters = filters or {}
        self.url = url
        self.api_key = api_key
        self.query = query
        self.query_fn = query_fn
        self.max_age_minutes = max_age_minutes
        self.timeout_minutes = timeout_minutes
        self.page_size = page_size
        self.table_name = table_name
        if not store_path:
            store_path = configs.DEFAULT_SOURCE_STORE
        if store_path.endswith("/"):
            store_path = store_path[:-1]
        self.store_path = store_path
        if schema:
            self.id_col = schema.get_id().original

    def calculate_complexity(self):
        return 40

    @property
    def dir_path(self):
        return f"{self.store_path}/{STORE_DIRECTORY}"

    @property
    def client(self):
        if not _has_flipside:
            raise Exception(
                "Flipside package is not installed, to use this functionality "
                "first install flipside extra: seshat-sdk[flipside_support]"
            )
        if not self._client:
            self._client = Flipside(self.api_key, self.url)
        return self._client

    def generate_sql_from_filter(self, filters):
        sql = ""
        for key, value in filters.items():
            prefix = "AND"
            if not sql:
                prefix = "WHERE"
            if isinstance(value, dict):
                val = value["val"]
                if "type" in value:
                    val = self.get_converted_value(value["val"], value["type"])
                sql += f" {prefix} {key}{value['op']}{val}"
            else:
                sql += f" {prefix} {key}={value}"
        return sql

    def _get_query_columns(self):
        columns = "*"
        if self.schema and self.schema.exclusive:
            columns = ",".join([col.original for col in self.schema.cols])
        return columns

    def get_query(self, filters=None):
        query = f"SELECT {self._get_query_columns()} FROM {self.table_name}"
        if self.query:
            query = self.query
        if self.query_fn:
            query = self.query_fn()
        return query + self.generate_sql_from_filter(
            {**self.filters, **(filters or {})}
        )

    def get_query_hash(self):
        hash_object = hashlib.sha256()
        hash_object.update(self.get_query().encode("utf-8"))

        hex_dig = hash_object.hexdigest()
        return hex_dig

    def chunk_size(self, data):
        if not self.single_item_size:
            self.single_item_size = get_obj_memory_size(data[0])
        return len(data) * self.single_item_size

    def store_in_file(self, data):
        os.makedirs(self.dir_path, exist_ok=True)
        file_path = f"{self.dir_path}/{self.get_query_hash()}_{self.id_col}_{data[-1][self.id_col]}.csv"
        Thread(target=save_to_csv, args=(data, file_path), daemon=True).start()

    def check_local(self, load=True):
        if not os.path.exists(self.dir_path):
            return None
        files_in_directory = os.listdir(self.dir_path)
        stored_chunks = [
            file
            for file in files_in_directory
            if file.startswith(self.get_query_hash())
        ]
        if not stored_chunks:
            return None
        [self.load_from_file(f"{self.dir_path}/{f}") for f in stored_chunks]
        return stored_chunks[-1].split("_")[-1][:-4]

    def load_from_file(self, file_path):
        if not self.loaded_df:
            self.loaded_df = LocalSource(file_path, mode=self.mode).fetch()
        self.loaded_df.extend_from_csv(file_path)

    def store_chunk(self, data, force_store=False):
        if (
            force_store
            or self.chunk_size(data[self._stored_index :])
            > configs.STORE_SIZE_CHECKPOINT
        ):
            self.store_in_file(data[self._stored_index :])
            self._stored_index = len(data)

    def sort_by(self):
        return [{"column": self.id_col, "direction": "asc"}]

    def get_starting_page(self):
        return 1

    def convert_data_type(self, data) -> SFrame:
        sf = self.data_class.from_raw(data)
        if self.loaded_df:
            sf = self.loaded_df + sf
        return sf

    def fetch_paginated(self, query_result):
        current_page_number = self.get_starting_page()
        total_pages = current_page_number + 1
        all_rows = []

        while current_page_number <= total_pages:
            results = self.client.get_query_results(
                query_result.query_id,
                page_number=current_page_number,
                page_size=self.page_size,
                sort_by=self.sort_by(),
            )
            if not results.page:
                raise EmptyDataError(
                    "No result was found, empty data cannot be processed"
                )
            total_pages = results.page.totalPages
            if results.records:
                all_rows = all_rows + results.records
                self.store_chunk(all_rows)
            current_page_number += 1

        self.store_chunk(all_rows, force_store=True)
        return all_rows

    def fetch(self) -> SFrame:
        last_saved_id = self.check_local()
        filters = {}
        if last_saved_id:
            filters = {
                self.id_col: {
                    "val": last_saved_id,
                    "op": ">=",
                    "type": "str",
                }
            }
        try:
            query_result = self.client.query(
                self.get_query(filters=filters),
                max_age_minutes=self.max_age_minutes,
                timeout_minutes=self.timeout_minutes,
            )
        except QueryRunRateLimitError:
            raise FlipSideRateLimitError()
        except QueryRunExecutionError as e:
            raise FlipSideQueryError(e)
        except ApiError as e:
            raise FlipSideApiError(e)

        result = self.fetch_paginated(query_result)
        return self.convert_data_type(result)
