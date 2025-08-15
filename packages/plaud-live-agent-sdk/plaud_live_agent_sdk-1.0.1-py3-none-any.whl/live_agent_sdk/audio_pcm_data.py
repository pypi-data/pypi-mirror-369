from dataclasses import dataclass
import numpy as np

@dataclass
class AudioPCMData:
    """PCM audio data wrapper"""
    data: np.ndarray      # PCM audio data (int16 format) 