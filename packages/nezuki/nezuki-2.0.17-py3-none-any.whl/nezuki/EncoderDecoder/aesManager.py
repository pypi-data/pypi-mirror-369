from nezuki.EncoderDecoder import EncoderDecoder
from cryptography.fernet import Fernet
import base64

# ----------------------------------------
# 📌 3. CRITTOGRAFIA SIMMETRICA (AES)
# ----------------------------------------

class CipherHandler(EncoderDecoder):
    """Classe per crittografare e decrittografare dati con chiave segreta (Fernet - AES)."""

    def __init__(self, key: bytes = None):
        """
        Inizializza il gestore di crittografia con una chiave segreta.

        Args:
            key (bytes, opzionale): Chiave per crittografia/decrittografia. Se non fornita, ne genera una nuova.
        """
        super().__init__()
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def encode(self, data: str) -> str:
        """
        Cifra un testo con l'algoritmo AES (Fernet).

        Args:
            data (str): Il testo da cifrare.

        Returns:
            str: Il testo cifrato in base64.
        """
        if not data:
            raise ValueError("Errore: 'data' non può essere vuoto.")

        encrypted_data = self.cipher.encrypt(data.encode())
        encrypted_base64 = base64.b64encode(encrypted_data).decode()

        self.logger.info("Dato crittografato con successo.", extra={'internal': True})
        return encrypted_base64

    def decode(self, encoded_data: str) -> str:
        """
        Decifra un testo crittografato con AES (Fernet).

        Args:
            encoded_data (str): Il testo crittografato in base64.

        Returns:
            str: Il testo decifrato.
        """
        try:
            decoded_bytes = base64.b64decode(encoded_data)
            decrypted_data = self.cipher.decrypt(decoded_bytes).decode()
            self.logger.info("Dato decrittografato con successo.", extra={'internal': True})
            return decrypted_data
        except Exception:
            self.logger.error("Errore durante la decrittografia.", extra={'internal': True})
            raise ValueError("Errore: Impossibile decifrare il dato.")

    def get_key(self) -> str:
        """Restituisce la chiave di crittografia in formato base64."""
        return self.key.decode()