import base64 as _base64
import enum as _enum
import io as _io
import logging as _logging
import re as _re
from typing import Optional as _Optional
from typing import Union as _Union

import torch as _torch

from tamm import _helpers
from tamm.typing import PathLike as _PathLike
from tamm.utils.uri import _is_uri, _URIHandler

# pylint: disable=import-outside-toplevel


_logger = _logging.getLogger(__name__)


class LoadingModule(_enum.Enum):
    """
    An enum for specifying the Python module that loads images in
    :func:`load_image`.
    """

    #: Use ``torchvision`` but fall back to ``PIL`` if ``PIL`` is
    #: available and ``torchvision`` is not.
    AUTO = 1

    #: Use ``torchvision``.
    TORCHVISION = 2

    #: Use ``PIL``.
    PIL = 3


def load_image(
    uri: _Union[str, _PathLike],
    mode: _Optional[str] = "RGB",
    loading_module: _Union[LoadingModule, str] = LoadingModule.AUTO,
) -> _torch.Tensor:
    """
    Loads and returns an image as a :obj:`torch.Tensor` in channels-first format.

    Args:
        uri (:obj:`str`): A string representation of the image.  This can
            be a local filepath, a URI, or a base64-encoded image string.
        mode (:obj:`str`): The image mode for the result.  Defaults to RGB.
        loading_module (:obj:`LoadingModule` or :obj:`str`): Specification of
            the Python module for loading the image.  Defaults to ``AUTO``.

    Returns:
        A :obj:`torch.Tensor` of pixel values in channels-first format.
    """

    if isinstance(uri, str):
        is_base64_encoded = _re.match("data:image/.*;base64,", uri)
        if is_base64_encoded is not None:
            data = uri[is_base64_encoded.end() :]
            return _load_base64_encoded_image(
                data, mode=mode, loading_module=loading_module
            )

    if _is_uri(uri):
        local_path = _URIHandler().map_to_local(uri)
    else:
        local_path = uri

    return _load_image_from_local_file(
        local_path, mode=mode, loading_module=loading_module
    )


def _load_image_from_local_file(
    filepath: _Union[str, _PathLike],
    *,
    mode: _Optional[str],
    loading_module: _Union[str, LoadingModule],
) -> _torch.Tensor:
    loading_module = _helpers.get_enum_member_from_name(LoadingModule, loading_module)

    if loading_module is LoadingModule.TORCHVISION:
        return _decode_image_torchvision(filepath, mode=mode)

    if loading_module is LoadingModule.PIL:
        return _decode_image_pil(filepath, mode=mode)

    return _decode_image_auto(filepath, mode=mode)


def _decode_image_auto(filepath, *, mode):
    try:
        return _decode_image_torchvision(filepath, mode=mode)
    except Exception as e:
        _logger.debug(f"Caught exception when loading image with torchvision: {e}")
        try:
            return _decode_image_pil(filepath, mode=mode)
        except Exception as e2:
            raise e2 from e


def _decode_image_torchvision(filepath, *, mode):
    import torchvision.io

    filepath = str(filepath)  # important older torch versions

    if mode is None:
        mode = "UNCHANGED"
    mode = _helpers.get_enum_member_from_name(torchvision.io.ImageReadMode, mode)

    return torchvision.io.read_image(filepath, mode=mode)


def _decode_image_pil(filepath, *, mode):
    import PIL.Image

    image = PIL.Image.open(filepath)
    if mode is not None:
        image = image.convert(mode)
    return _convert_pil_to_torch(image)


def _load_base64_encoded_image(
    data: str,
    mode: _Optional[str],
    loading_module: _Union[LoadingModule, str] = LoadingModule.AUTO,
) -> _torch.Tensor:
    """Loads an image from a base64-encoded string."""

    loading_module = _helpers.get_enum_member_from_name(LoadingModule, loading_module)

    decoded_bytes = _base64.b64decode(data)

    if loading_module is LoadingModule.TORCHVISION:
        return _load_base64_encoded_image_torchvision(decoded_bytes, mode=mode)

    if loading_module is LoadingModule.PIL:
        return _load_base64_encoded_image_pil(decoded_bytes, mode=mode)

    return _load_base64_encoded_image_auto(decoded_bytes, mode=mode)


def _load_base64_encoded_image_auto(data: bytes, *, mode) -> _torch.Tensor:
    try:
        return _load_base64_encoded_image_torchvision(data, mode=mode)
    except Exception as e:
        _logger.debug(f"Caught exception when loading image with torchvision: {e}")

        try:
            return _load_base64_encoded_image_pil(data, mode=mode)
        except Exception as e2:
            raise e2 from e


def _load_base64_encoded_image_torchvision(data: bytes, *, mode) -> _torch.Tensor:
    import torchvision.io

    if mode is None:
        mode = "UNCHANGED"
    mode = _helpers.get_enum_member_from_name(torchvision.io.ImageReadMode, mode)

    data = _torch.frombuffer(data, dtype=_torch.uint8)
    return torchvision.io.decode_image(data, mode=mode)


def _load_base64_encoded_image_pil(data: bytes, *, mode) -> _torch.Tensor:
    import PIL.Image

    bytes_io = _io.BytesIO(data)
    image = PIL.Image.open(bytes_io)
    if mode is not None:
        image = image.convert(mode)
    return _convert_pil_to_torch(image)


def _convert_pil_to_torch(image) -> _torch.Tensor:
    """
    Converts a PIL Image to a torch Tensor (without assuming a torchvision dependency)
    """
    import numpy as np

    is_binary = image.mode == "1"

    image = np.array(image)
    if image.ndim == 2:
        image = image[..., None]
    image = np.moveaxis(image, -1, 0)  # make channels-first

    if is_binary or image.dtype == np.uint8:
        dtype = _torch.uint8
    else:
        dtype = None
    image = _torch.tensor(image, dtype=dtype)

    if is_binary:
        image *= 255

    return image
