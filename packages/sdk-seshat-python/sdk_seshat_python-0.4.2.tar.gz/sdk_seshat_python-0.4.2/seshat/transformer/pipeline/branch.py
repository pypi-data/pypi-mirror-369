from concurrent.futures.process import ProcessPoolExecutor
from typing import List, Dict

from seshat.data_class import SFrame, GroupSFrame
from seshat.general.config import DEFAULT_SF_KEY
from seshat.general.exceptions import InvalidArgumentsError
from seshat.transformer import Transformer
from seshat.transformer.merger.base import SFrameMerger
from seshat.transformer.pipeline import Pipeline


def process_pipeline(sf, sf_key, pipe, index, *args, **kwargs):
    if index is not None:
        return sf_key + f"__{index}", pipe(sf.get(sf_key), *args, **kwargs)
    return sf_key, pipe(sf.get(sf_key), *args, **kwargs)


class Branch(Transformer):
    """
    Branch is a Transformer that runs multiple pipelines simultaneously and merges their outputs.
    It can execute pipelines in parallel using multiple processes.

    Parameters
    ----------
    pipe_map : Dict[str, Pipeline | List[Pipeline]], optional
        A dictionary mapping SFrames to pipelines or lists of pipelines.
    merger : Merger, optional
        An object to merge the pipeline outputs.
    parallel : bool, optional
        Whether to run pipelines in parallel. Default is False.
    max_workers : int, optional
        Maximum number of workers for parallel execution. Default is 16.
    group_keys
        Group keys for the parent Transformer class.
    *args
        Additional positional arguments.
    **kwargs
        Additional keyword arguments.

    Example usage
    ----------
    1. Creating a Branch instance with a list of pipelines:

        >>> sf_input = GroupSFrame(children={"default": DFrame(transaction_df), "address": DFrame(address_df)})
        ... pipe_map = {
        ... "default": [Pipeline(pipes=[ZeroAddressTrimmer(), LowTransactionTrimmer()]),
        ...             Pipeline(pipes=[OperationOnColsDeriver(
        ...                 cols=("sent_count", "received_count"),
        ...                 result_col="tx_count",
        ...                 agg_func="sum",
        ...                 is_numeric=True,
        ...             )])],
        ... }
        ... branch = Branch(pipe_map=pipe_map, merger=Merger())
        ... result = branch(sf_input)

    2. Creating a Branch instance with a single pipeline for each SFrame:

        >>> sf_input = GroupSFrame(children={"default": DFrame(transaction_df), "address": DFrame(address_df)})
        ... pipe_map = {
        ...     "default": Pipeline(pipes=[ZeroAddressTrimmer(), LowTransactionTrimmer()]),
        ...     "address": Pipeline(pipes=[FeatureForAddressDeriver(
        ...         value_col="ez_token_transfers_id",
        ...         result_col="received_count",
        ...         default_index_col="to_address",
        ...         agg_func="nunique",
        ...         is_numeric=False,
        ...     )])
        ... }
        ... branch = Branch(pipe_map=pipe_map, merger=Merger())
        ... result = branch(sf_input)
    """

    merger: SFrameMerger
    parallel: bool
    max_workers: int
    HANDLER_NAME = "run"

    def __init__(
        self,
        pipe_map: Dict[str, Pipeline | List[Pipeline]] = None,
        merger: SFrameMerger = None,
        parallel: bool = False,
        max_workers: int = 16,
        group_keys=None,
        *args,
        **kwargs,
    ):
        super().__init__(group_keys, *args, **kwargs)

        self.pipe_map = pipe_map
        self.merger = merger
        self.parallel = parallel
        self.max_workers = max_workers

    def calculate_complexity(self):
        def max_complexity(pipe_val):
            if type(pipe_val) is Pipeline:
                return pipe_val.calculate_complexity()
            return max([pipe.calculate_complexity() for pipe in pipe_val])

        return max_complexity(self.pipe_map) * 0.2 + self.merger.calculate_complexity()

    def __call__(self, sf_input: SFrame, *args, **kwargs) -> SFrame:
        result = super().__call__(sf_input, *args, **kwargs)
        if self.merger:
            result = self.merger(result)
        return result

    def call_handler(self, sf: SFrame, *args, **kwargs) -> Dict[str, object]:
        return self.run(sf, *args, **kwargs)

    def run(self, sf: SFrame, *args, **kwargs):
        if isinstance(sf, GroupSFrame):
            if set(self.pipe_map.keys()).difference(set(sf.children.keys())):
                raise InvalidArgumentsError(
                    "Pipeline map keys must exist in passed SFrame"
                )
        else:
            sf = sf.make_group(DEFAULT_SF_KEY)
        result = (
            self.run_parallel_pipes(sf, *args, **kwargs)
            if self.parallel
            else self.run_pipes(sf, *args, **kwargs)
        )
        return result

    def run_pipes(self, sf: SFrame, *args, **kwargs):
        results = {}
        for sf_key, pipes in self.pipe_map.items():
            if isinstance(pipes, list):
                for i in range(len(pipes)):
                    results[sf_key + f"__{i}"] = pipes[i](
                        sf.get(sf_key), *args, **kwargs
                    )
            else:
                results[sf_key] = pipes(sf.get(sf_key), *args, **kwargs)
        return results

    def run_parallel_pipes(self, sf: SFrame, *args, **kwargs):
        results = {}

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for sf_key, pipes in self.pipe_map.items():
                if isinstance(pipes, list):
                    for i in range(len(pipes)):
                        futures.append(
                            executor.submit(
                                process_pipeline,
                                sf,
                                sf_key,
                                pipes[i],
                                i,
                                *args,
                                **kwargs,
                            )
                        )
                else:
                    futures.append(
                        executor.submit(
                            process_pipeline, sf, sf_key, pipes, None, *args, **kwargs
                        )
                    )

            for future in futures:
                key, result = future.result()
                results[key] = result

        return results
