import torch as _torch
import torch.nn as _nn

from tamm.ao import layers as _ao_layers
from tamm.ao.arch_optimizers import common as _common
from tamm.utils import OptionalBool as _OptionalBool


class KVQuantArchOptimizer(_common.ArchOptimizer):
    """
    An :class:`.ArchOptimizer` that applies "fake" activation quantization to the keys
    and values of attention layers.  This helps simulate the impact of KV-cache
    quantization.

    Specifically, the :meth:`.optimize` method of this class inserts :obj:`.KVQuantizer`
    layers immediately prior to the ``kv_cacher`` in :obj:`.TransformerAttention`
    layers.  The quantization uses :class:`.FakeQuantize` layers and
    :obj:`.SimpleEMAMinMaxObserver` observers with default arguments.

    Args:
        freeze_qparams (:obj:`bool`, optional): A flag for freezing the quantization
            parameters (such as scales and zero points).  If ``False`` (the default),
            then observers from the key and value quantizers are enabled, meaning that
            they update the qparams during each forward pass in training mode (the
            params remain frozen when in eval mode).
        cast_dtype (:obj:`torch.dtype`, optional): A ``cast_dtype`` argument for
            the key and value :class:`.FakeQuantize` layers.  Defaults to ``float32``.
        skip_quantize_for_first_token(:obj:`bool`, optional): Set to ``True`` to quantize
            kv cacher while skipping the quantization for first token logit calculation
            but still writing quantized values to the cache.
            Defaults to ``False``.
    """

    freeze_qparams: bool = False
    cast_dtype: _torch.dtype = _torch.float32
    skip_quantize_for_first_token: bool = False

    def _optimize_impl(
        self,
        model: _nn.Module,
        *,
        pretrained: "_OptionalBool" = _OptionalBool.NOTSET,
    ) -> None:
        """
        Modifies ``TransformerAttention`` module based on if ``skip_quantize_for_first_token`` is:
        - ``True``: Wraps the kv_cacher layer to include special quantization: skipping the
            quantization for first token logit calculation but still writing quantized values to the cache.
        - ``False``: Inserts kv_quantizer layer above kv_cacher layer.
        """
        # pylint: disable-next=import-outside-toplevel
        from tamm import layers

        for layer in model.modules():
            if not isinstance(layer, layers.TransformerAttention):
                continue

            if self.skip_quantize_for_first_token:
                layer["kv_cacher"] = self._create_quantizing_kv_cacher_layer(
                    layer["kv_cacher"]
                )
            else:
                kv_cacher_idx = list(layer).index(layer["kv_cacher"])
                quantizer = self._create_quantizer_layer()
                layer.insert(kv_cacher_idx, quantizer, name="kv_quantizer")

    def _create_quantizer_layer(self):
        key_quantizer = self._create_fake_quantizer()
        value_quantizer = self._create_fake_quantizer()
        return _ao_layers.KVQuantizer(
            key_quantizer=key_quantizer, value_quantizer=value_quantizer
        )

    def _create_fake_quantizer(self):
        """Creates a FakeQuantize layer."""
        enable_observer = "disabled" if self.freeze_qparams else "only_training"
        return _ao_layers.FakeQuantize(
            _ao_layers.SimpleEMAMinMaxObserver(),
            enable_observer=enable_observer,
            cast_dtype=self.cast_dtype,
        )

    def _create_quantizing_kv_cacher_layer(self, kv_cacher):
        """Wraps the kv_cacher layer to include quantization, skipping the quantization for first
        token logit calculation but still writes quantized values to the cache."""
        key_quantizer = self._create_fake_quantizer()
        value_quantizer = self._create_fake_quantizer()
        return _ao_layers.QuantizingKVCacher(key_quantizer, value_quantizer, kv_cacher)
