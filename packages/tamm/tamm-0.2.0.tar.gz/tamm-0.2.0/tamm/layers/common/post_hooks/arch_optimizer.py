from typing import TYPE_CHECKING
from typing import Dict as _Dict
from typing import Optional as _Optional

from tamm.layers.common.post_hooks.common import CompositePostHook, IdentityPostHook

if TYPE_CHECKING:
    from tamm.ao import ArchOptimizer


def ArchOptimizersPostHook(  # pylint: disable=invalid-name
    arch_optimizers: _Optional[_Dict[str, "ArchOptimizer"]] = None,
):
    if arch_optimizers is None:
        return IdentityPostHook()

    hooks = [ao.optimize for ao in arch_optimizers.values()]
    return CompositePostHook(*hooks)
