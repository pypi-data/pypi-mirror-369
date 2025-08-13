from .format_sequences import format_long_sequence
from .poly_data_utils import set_polydata_colors, set_polydata_property, read_obj_file, read_stl_file, transform_polydata
from .tree_info import TreeInfo


from collections import defaultdict
def nested_dict() -> defaultdict:
    return defaultdict(nested_dict)
