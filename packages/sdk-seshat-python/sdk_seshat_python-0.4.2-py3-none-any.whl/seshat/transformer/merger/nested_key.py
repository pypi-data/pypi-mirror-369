from typing import Optional

import pandas as pd

from seshat.data_class import SFrame, GroupSFrame, DFrame
from seshat.transformer.merger.base import SFrameMerger


class NestedKeyMerger(SFrameMerger):
    """
    A merger that searches for a specific key in a nested GroupSFrame structure
    and concatenates the DFrames found with this key.

    This merger is designed to work with the output of a Branch transformer where:
    - The input is a GroupSFrame
    - The children of the input are also GroupSFrames
    - The children of the children are dictionaries mapping strings to DFrames

    Parameters
    ----------
    group_key : str
        The key to search for in the nested structure
    result_key : str, optional
        The key to use for the result in the output GroupSFrame.
        If not provided, the group_key will be used.

    Examples
    --------
    >>> branch = Branch(pipe_map=pipe_map)
    >>> result = branch(sf_input)  # result is a GroupSFrame with GroupSFrame children
    >>> merger = NestedKeyMerger(group_key="user_data")
    >>> merged_result = merger(result)  # merged_result is a GroupSFrame with a single DFrame
    """

    def __init__(
        self, group_key: str, result_key: Optional[str] = None, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.group_key = group_key
        self.result_key = result_key or group_key

    def __call__(self, sf_input: SFrame, *args, **kwargs) -> SFrame:
        """
        Search for the group_key in the nested structure and concatenate the DFrames.

        Parameters
        ----------
        sf_input : SFrame
            The input SFrame, expected to be a GroupSFrame with GroupSFrame children

        Returns
        -------
        SFrame
            A GroupSFrame with a single DFrame containing the concatenated data
        """
        if not isinstance(sf_input, GroupSFrame):
            return sf_input

        # Collect all DFrames with the group_key
        dframes = []

        for child_key, child_sf in sf_input.children.items():
            if isinstance(child_sf, GroupSFrame):
                # Look for the group_key in the children of the child
                if self.group_key in child_sf.children:
                    target_frame = child_sf.children[self.group_key]
                    if isinstance(target_frame, DFrame):
                        dframes.append(target_frame.data)

        # If no DFrames found, return the original input
        if not dframes:
            return sf_input

        # Concatenate the DFrames
        concatenated_df = pd.concat(dframes, axis=0, ignore_index=True)

        # Create a new GroupSFrame with the concatenated DFrame
        result = GroupSFrame()
        result[self.result_key] = DFrame(concatenated_df)

        return result

    def calculate_complexity(self):
        return 15
