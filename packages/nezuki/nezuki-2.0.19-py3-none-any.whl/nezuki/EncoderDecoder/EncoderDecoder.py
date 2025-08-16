from nezuki.Logger import get_nezuki_logger

class EncoderDecoder:
    """Classe base per gestire encoding, decoding, hashing e crittografia."""

    def __init__(self):
        self.logger = get_nezuki_logger()

    def encode(self, data: str) -> str:
        """Metodo generico per la codifica. Da implementare nelle sottoclassi."""
        raise NotImplementedError("Il metodo encode() deve essere implementato nelle sottoclassi.")

    def decode(self, encoded_data: str) -> str:
        """Metodo generico per la decodifica. Da implementare nelle sottoclassi."""
        raise NotImplementedError("Il metodo decode() deve essere implementato nelle sottoclassi.")