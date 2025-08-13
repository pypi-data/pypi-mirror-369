import logging as _logging

import torch

_logger = _logging.getLogger(__name__)

TORCH_AUDIO_IMPORT_FAIL_MESSAGE = (
    "tamm tried to import torchaudio but failed"
    "tamm could not import this.  Please install torchaudio or check "
    "your installation of this package."
)


def load_audio(
    audio_path: str, normalized: bool = False, dtype: torch.dtype = torch.float32
):
    """
    Load an audio file and return the waveform and sample rate.

    Args:
        audio_path (:obj:`str`): Path to the audio file.
        normalized (:obj:`bool`, optional): Whether to normalize the waveform to the range
            [-1.0, 1.0]. Defaults to ``False``.
        dtype (:obj:`torch.dtype`, optional): An optional dtype for casting the
        waveform. Defaults to ``torch.float32``.

    Returns:
        tuple: A tuple containing the waveform tensor and the sample rate.
            - waveform: Tensor of shape (num_channels, num_samples)
                        - num_channels: 1 for mono audio, 2 for stereo audio
                        - num_samples: The number of audio samples in the waveform
            - sample_rate: Integer representing the sample rate of the audio in Hz
    """
    try:
        # pylint: disable-next=import-outside-toplevel
        import torchaudio
    except (ModuleNotFoundError, ImportError):
        _logger.error(TORCH_AUDIO_IMPORT_FAIL_MESSAGE)
        raise

    waveform, sample_rate = torchaudio.load(audio_path, normalize=normalized)
    return waveform.to(dtype), sample_rate


def resample_audio(waveform: torch.Tensor, sample_rate: int, target_sample_rate: int):
    """
    Resample the audio waveform to the target sample rate.

    Args:
        waveform (:obj:`torch.Tensor`): The audio waveform to resample.
        sample_rate (:obj:`int`): The current sample rate of the waveform.
        target_sample_rate (:obj:`int`): Target sample rate of the waveform.

    Returns:
        torch.Tensor: The resampled audio waveform.
    """
    try:
        # pylint: disable-next=import-outside-toplevel
        import torchaudio
    except (ModuleNotFoundError, ImportError):
        _logger.error(TORCH_AUDIO_IMPORT_FAIL_MESSAGE)
        raise
    resampled_waveform = torchaudio.functional.resample(
        waveform, orig_freq=sample_rate, new_freq=target_sample_rate
    )
    return resampled_waveform
