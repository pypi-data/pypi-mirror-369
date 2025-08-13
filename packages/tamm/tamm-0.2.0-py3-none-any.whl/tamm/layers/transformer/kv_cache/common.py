import abc as _abc
from typing import List as _List
from typing import Protocol as _Protocol
from typing import Tuple as _Tuple
from typing import Union as _Union

import torch as _torch


class BaseKVCache(_Protocol):
    """
    A :obj:`Protocol` that defines an abstract interface between the inference runner
    and its key-value cache.
    """

    @property
    @_abc.abstractmethod
    def length(self) -> int:
        """The sequence length that the cache is initialized for."""

    @_abc.abstractmethod
    def up_to_index(self, index: int) -> "BaseKVCacheView":
        """
        Returns a :obj:`.BaseKVCacheView` that exposes the first ``index`` tokens
        of the cache.  This enables pre-allocation of the cache with a large sequence
        length and then efficient incremental writes while filling the cache.

        Args:
            index (:obj:`int`): The length of the resulting cache view.  This must not
                exceed the length of the cache.

        Returns:
            A cache view of the first ``index`` tokens in the cache.
        """

    @_abc.abstractmethod
    def resize(self, new_length: int):
        """
        Updates the underlying sequence length of the cache while keeping previously
        cached values.

        Args:
            new_length (:obj:`int`): The new sequence length.
        """

    @_abc.abstractmethod
    def to(self, *args, **kwargs) -> "BaseKVCache":  # pylint: disable=invalid-name
        """
        Change the device and/or dtype of the cache, similar to :func:`torch.Tensor.to`.

        Returns:
            The :obj:`BaseKVCache` instance (``self``).
        """


class BaseKVCacheView(_Protocol):
    """
    A :obj:`Protocol` that defines an abstract interface between a
    :obj:`.TransformerStack` and its key-value cache.
    """

    @property
    @_abc.abstractmethod
    def length(self) -> int:
        """The sequence length of the cache view."""

    @property
    @_abc.abstractmethod
    def num_layers(self) -> int:
        """The number of layers in the cache view."""

    @property
    @_abc.abstractmethod
    def dtype(self) -> _Union[_torch.dtype, None]:
        """
        The :obj:`torch.dtype` of the cached values.  May return ``None`` if the
        cache is still empty.
        """

    @property
    @_abc.abstractmethod
    def device(self) -> _torch.device:
        """The :obj:`torch.device` of the cached values."""

    def at_layer(self, layer_idx: int) -> "KVCacheLayerView":
        """
        Exposes the cache for a specific layer of the model.

        Args:
            layer_idx (:obj:`int`): The layer index.  This must be less than
                ``num_layers``.

        Returns:
            A :obj:`KVCacheLayerView` for layer ``layer_idx`` of the model/cache.
        """
        return KVCacheLayerView(kv_cache_view=self, layer_idx=layer_idx)

    def at_layers(self, layer_indices: _List[int]) -> "KVCacheLayersView":
        return KVCacheLayersView(kv_cache_view=self, layer_indices=layer_indices)

    @_abc.abstractmethod
    def write_to_tail(
        self, key: _torch.Tensor, value: _torch.Tensor, *, layer_idx: int
    ) -> None:
        """
        Writes new key and value tensors to the cache for a specific layer, overwriting
        the trailing ``num_new_tokens`` cached keys and values for this layer.

        Args:
            key (:obj:`torch.Tensor`): A newly computed key tensor with shape
                ``(batch_size, num_new_tokens, num_kv_heads * dim_per_head)``.
            value (:obj:`torch.Tensor`): A newly computed value tensor with shape
                ``(batch_size, num_new_tokens, num_kv_heads * dim_per_head)``.
            layer_idx (:obj:`int`): The index of the layer in the model/cache.
        """

    def write_to_tail_vectorized(
        self, keys: _torch.Tensor, values: _torch.Tensor, *, layer_indices: _List[int]
    ) -> None:
        # Note: It's up to the specific KVCacheView to provide efficient vectorized implementation
        # Note that dimension after batch (0th indx) is the vectorize dimension
        for idx, layer_idx in enumerate(layer_indices):
            self.write_to_tail(
                _torch.select(keys, 1, idx),
                _torch.select(values, 1, idx),
                layer_idx=layer_idx,
            )

    @_abc.abstractmethod
    def write_segment_ids_to_tail(self, segment_ids: _torch.Tensor) -> None:
        """
        Writes new segment IDs to the cache, overwriting the trailing ``num_new_tokens``
        cached segment IDs.

        Args:
            segment_ids (:obj:`torch.Tensor`): An integer tensor of segment IDs with
                shape ``(batch_size, num_new_tokens)``.
        """

    @_abc.abstractmethod
    def write_positions_to_tail(self, positions: _torch.Tensor) -> None:
        """
        Writes new positions to the cache, overwriting the trailing ``num_new_tokens``
        cached positions.

        Args:
            positions (:obj:`torch.Tensor`): An integer tensor of positions with
                shape ``(batch_size, num_new_tokens)``.
        """

    def write_token_types_to_tail(
        self, token_types: _torch.Tensor
    ) -> None:  # no @abstractmethod since most models don't call it
        """
        Writes new token types to the cache, overwriting the trailing ``num_new_tokens``
        cached positions.

        Args:
            positions (:obj:`torch.Tensor`): An integer tensor of positions with
                shape ``(batch_size, num_new_tokens)``.
        """
        raise NotImplementedError(
            f"{self.__class__} has not implemented write_token_types_to_tail()"
        )

    @_abc.abstractmethod
    def read(self, layer_idx: int) -> _Tuple[_torch.Tensor, _torch.Tensor]:
        """
        Reads keys and values from the cache for a specific layer.

        Args:
            layer_idx (:obj:`int`): The index of the layer in the model/cache.

        Returns:
            A :obj:`tuple` of two tensors, each with shape
            ``(batch_size, length, num_kv_heads * dim_per_head)``.  The first
            element is the keys and the second is the values.  The ``length`` is the
            full sequence length of the cache view.
        """

    def read_batched(
        self, layer_indices: _List[int]
    ) -> _Tuple[_torch.Tensor, _torch.Tensor]:
        """
        Reads keys and values from the caches.

        Returns:
            A :obj:`tuple` of lists, each tensor within the list has shape
            ``(batch_size, length, num_kv_heads * dim_per_head)``.  The first
            set of elements are the keys and the second are the values.  The ``length`` is the
            full sequence length of the cache view.
        """
        qs, vs = [], []
        for layer_idx in layer_indices:
            q, v = self.read(layer_idx)
            qs.append(q)
            vs.append(v)
        return _torch.stack(qs, dim=1), _torch.stack(vs, dim=1)

    @_abc.abstractmethod
    def read_segment_ids(self) -> _torch.Tensor:
        """
        Reads segment IDs from the cache.

        Returns:
            An integer tensor of segment IDs with shape ``(batch_size, length)``, where
            ``length`` is the full sequence length of the cache view.
        """

    @_abc.abstractmethod
    def read_positions(self) -> _torch.Tensor:
        """
        Reads positions from the cache.

        Returns:
            An integer tensor of positions with shape ``(batch_size, length)``, where
            ``length`` is the full sequence length of the cache view.
        """

    def read_token_types(
        self,
    ) -> _torch.Tensor:  # no @abstractmethod since most models don't call it
        """
        Reads token types from the cache.

        Returns:
            An integer tensor of token types with shape ``(batch_size, length)``, where
            ``length`` is the full sequence length of the cache view.
        """
        raise NotImplementedError(
            f"{self.__class__} has not implemented read_token_types()"
        )


class KVCacheLayerView:
    """
    A class for reading and writing keys and values for a specific layer of a
    :class:`.BaseKVCacheView`.
    """

    def __init__(self, *, kv_cache_view: BaseKVCacheView, layer_idx: int) -> None:
        self.kv_cache_view = kv_cache_view
        self.layer_idx = layer_idx

    @property
    def dtype(self) -> _torch.dtype:
        """The :obj:`torch.dtype` of the cached values."""
        return self.kv_cache_view.dtype

    @property
    def device(self) -> _torch.device:
        """The :obj:`torch.device` of the cached values."""
        return self.kv_cache_view.device

    def write_to_tail(self, key: _torch.Tensor, value: _torch.Tensor) -> None:
        """
        Writes new key and value tensors to the cache, overwriting the trailing
        ``num_new_tokens`` cached keys and values for this layer.

        Args:
            key (:obj:`torch.Tensor`): A newly computed key tensor with shape
                ``(batch_size, num_new_tokens, num_kv_heads * dim_per_head)``.
            value (:obj:`torch.Tensor`): A newly computed value tensor with shape
                ``(batch_size, num_new_tokens, num_kv_heads * dim_per_head)``.
        """
        if self.dtype is not None:
            are_dtypes_matching = self.dtype == key.dtype == value.dtype
            if not are_dtypes_matching:
                raise TypeError(
                    "dtype mismatch in kv cache "
                    f"(key: {key.dtype}, value: {value.dtype}, cache: {self.dtype})"
                )

        self.kv_cache_view.write_to_tail(key, value, layer_idx=self.layer_idx)

    def read(self) -> _Tuple[_torch.Tensor, _torch.Tensor]:
        """
        Reads keys and values from the cache.

        Returns:
            A :obj:`tuple` of two tensors, each with shape
            ``(batch_size, length, num_kv_heads * dim_per_head)``.  The first
            element is the keys and the second is the values.  The ``length`` is the
            full sequence length of the cache view.
        """
        return self.kv_cache_view.read(self.layer_idx)


class KVCacheLayersView:
    """
    A class for reading and writing keys and values for a _multiple_ layers of a
    :class:`.BaseKVCacheView`.
    """

    def __init__(
        self, *, kv_cache_view: BaseKVCacheView, layer_indices: _List[int]
    ) -> None:
        self.kv_cache_view = kv_cache_view
        self.layer_indices = layer_indices

    @property
    def dtype(self) -> _torch.dtype:
        """The :obj:`torch.dtype` of the cached values."""
        return self.kv_cache_view.dtype

    @property
    def device(self) -> _torch.device:
        """The :obj:`torch.device` of the cached values."""
        return self.kv_cache_view.device

    def write_to_tail(self, keys: _torch.Tensor, values: _torch.Tensor) -> None:
        """
        Writes new key and value tensors to the caches, overwriting the trailing
        ``num_new_tokens`` cached keys and values for this layer.

        Args:
            keys (:obj: `torch.Tensor`): A newly computed stacked list of key tensors with shape
                ``(batch_size, vec_dim, num_new_tokens, num_kv_heads * dim_per_head)``.
            values (:obj: `torch.Tensor`): A newly computed stacked list of value tensor with shape
                ``(batch_size, vec_dim, num_new_tokens, num_kv_heads * dim_per_head)``.
        """
        if self.dtype is not None:
            are_dtypes_matching = self.dtype == keys.dtype == values.dtype
            if not are_dtypes_matching:
                raise TypeError(
                    "dtype mismatch in kv cache "
                    f"(keys: {keys.dtype}, values: {values.dtype}, cache: {self.dtype})"
                )

        self.kv_cache_view.write_to_tail_vectorized(
            keys, values, layer_indices=self.layer_indices
        )

    def read(self) -> _Tuple[_torch.Tensor, _torch.Tensor]:
        """
        Reads keys and values from the caches.

        Returns:
            A :obj:`tuple` of lists, each tensor within the list has shape
            ``(batch_size, length, num_kv_heads * dim_per_head)``.  The first
            set of elements are the keys and the second are the values.  The ``length`` is the
            full sequence length of the cache view.
        """
        return self.kv_cache_view.read_batched(layer_indices=self.layer_indices)
