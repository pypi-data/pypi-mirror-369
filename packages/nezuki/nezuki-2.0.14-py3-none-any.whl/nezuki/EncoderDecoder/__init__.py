__version__ = "1.0.0"

from .EncoderDecoder import EncoderDecoder
from .qrCode import QRCodeHandler as QRCode
from .hashGenerator import HashGenerator as Hash
from .aesManager import CipherHandler as AES

__all__ = ["EncoderDecoder", "QRCode", "Hash", "AES"]