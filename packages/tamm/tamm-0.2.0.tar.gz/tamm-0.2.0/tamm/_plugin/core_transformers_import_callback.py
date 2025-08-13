from tamm._plugin import utils as plugin_utils
from tamm.runtime_configuration import rc


def execute_core_transformers_import_callbacks() -> None:
    entrypoints = plugin_utils.discover_plugin_extras(
        rc.PLUGINS_EXTRAS_ENTRYPOINT_NAMES.core_transformers_import_callback
    )
    for entrypoint in entrypoints:
        plugin_utils.execute_plugin_object_reference(entrypoint.value, call_obj=True)
