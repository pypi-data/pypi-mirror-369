from tamm.runtime_configuration import rc as _rc

if _rc.adapters_implementation == "v1":
    from tamm._adapters_v1 import *  # noqa: F403
else:
    raise RuntimeError(
        f"rc.adapters_implementation '{_rc.adapters_implementation}' not recognized"
    )
