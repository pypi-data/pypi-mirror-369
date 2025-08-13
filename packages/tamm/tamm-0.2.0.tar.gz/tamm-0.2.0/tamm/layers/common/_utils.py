from tamm.layers.common.config import ModuleConfig as _ModuleConfig


def map_configs_to_builders(*objs):
    """
    A helper function for converting one of more :obj:`ModuleConfig` objects
    to :obj:`.LayerBuilder` objects.  This function recognizes configs in
    any collection of tuples, lists, and dicts.

    Args:
       *objs: One or more objects, possibly containing config(s).

    Returns:
        The objects with configs mapped to builders by calling the
        :meth:`~.ModuleConfig.create_builder` method of each config.
    """

    if len(objs) == 0:
        raise ValueError(
            "map_configs_to_builders() requires at least one argument but "
            "received none"
        )

    if len(objs) > 1:
        return tuple(map_configs_to_builders(obj) for obj in objs)

    obj = objs[0]
    if isinstance(obj, dict):
        return {key: map_configs_to_builders(val) for key, val in obj.items()}
    if isinstance(obj, list):
        return [map_configs_to_builders(val) for val in obj]
    if isinstance(obj, tuple):
        return tuple(map_configs_to_builders(val) for val in obj)
    if isinstance(obj, _ModuleConfig):
        return obj.create_builder()
    return obj
