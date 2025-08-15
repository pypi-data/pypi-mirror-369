from typing import Callable, Dict, List, Literal, Optional, Tuple, Union


def ch_output_dict_to_sorted_lists(ch_output_dict: Dict[Literal["red", "green", "blue", "amber", "cyan", "lime"], float],  sort_order: Literal["lbrgca", "rgbacl"] = "lbrgca") -> Tuple[List[str],List[float]]:
    """Convert a channel output dict to a sorted list of channel names and a sorted list of channel outputs

    Args:
        ch_output_dict (Dict[Literal["red", "green", "blue", "amber", "cyan", "lime"], float]): 
        sort_order (Literal["lbrgca", "rgbacl"], optional): Defaults to "lbrgca".

    Returns:
        Tuple[List[str],List[float]]: 
    """
    sorted_output_s = sorted(ch_output_dict.items(), key=lambda x: sort_order.index(x[0][0]))
    sorted_colors = [color for color, _ in sorted_output_s]
    sorted_values = [value for _, value in sorted_output_s]
    return sorted_colors, sorted_values
