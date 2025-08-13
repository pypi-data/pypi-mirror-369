from tamm._plugin import utils as plugin_utils
from tamm.runtime_configuration import rc


def register_cli_commands() -> None:
    entrypoints = plugin_utils.discover_plugin_extras(
        rc.PLUGINS_EXTRAS_ENTRYPOINT_NAMES.cli
    )
    for entrypoint in entrypoints:
        plugin_utils.execute_plugin_object_reference(entrypoint.value, call_obj=True)
