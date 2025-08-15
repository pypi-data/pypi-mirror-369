from typing import List

from seshat.transformer import Transformer


class Pipeline(Transformer):
    """
    A data processing pipeline that sequentially applies a list of transformers to input data.
    Each transformer in the `pipes` list processes the data and passes the output to the next transformer
    in the sequence. The result from the last transformer in the list is the final output of the pipeline.

    The transformers in the `pipes` list must be capable of applying a transformation and
    producing an output that can be handled by the next transformer in the list, if there is one.
    This allows for a flexible and modular design where different transformations can be chained
    together to achieve complex data processing workflows.

    Parameters
    ----------
    pipes : list of Transformer instances
        A list of transformer objects through which the data will be passed in sequence.
        The output of one transformer becomes the input to the next.

    Examples
    --------
    >>> pipeline = Pipeline(pipes=[transformer1, transformer2]
    >>> pipeline(input_data)

    Notes
    -----
    This pipeline design is particularly useful for data transformations where multiple
    discrete processing steps are required. Each transformer should be designed to handle
    the output from the previous transformer in the sequence, ensuring compatibility between transformations.
    """

    pipes: List[Transformer]

    def __init__(self, pipes: List[Transformer]):
        self.pipes = pipes

    def __call__(self, data, *args, **kwargs):
        result = data
        for pipe in self.pipes:
            result = pipe(result, *args, **kwargs)
        return result

    def replace(self, transformer: Transformer, index: int):
        self.pipes[index] = transformer
        return self

    def append(self, transformer: Transformer):
        self.pipes.append(transformer)
        return self

    def insert(self, transformer: Transformer, index: int):
        self.pipes.insert(index, transformer)
        return self

    def remove(self, index: int):
        self.pipes.pop(index)
        return self

    def calculate_complexity(self):
        return sum([pipe.calculate_complexity() for pipe in self.pipes])
