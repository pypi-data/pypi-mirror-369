from nezuki.EncoderDecoder import EncoderDecoder
import hashlib

# ----------------------------------------
# 📌 2. GENERATORE DI HASH
# ----------------------------------------

class HashGenerator(EncoderDecoder):
    """Genera hash utilizzando diversi algoritmi (SHA256, SHA512, MD5, ecc.)."""

    def encode(self, data: str, algorithm: str = "sha256") -> str:
        """
        Genera un hash del dato fornito.
        
        Args:
            data (str): Il dato da codificare in hash.
            algorithm (str): Algoritmo di hashing (default: sha256).
            
        Returns:
            str: L'hash del dato fornito.
        """
        if not data:
            raise ValueError("Errore: 'data' non può essere vuoto.")

        algorithms = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512,
        }

        if algorithm not in algorithms:
            raise ValueError(f"Errore: Algoritmo '{algorithm}' non supportato.")

        hash_object = algorithms[algorithm]()
        hash_object.update(data.encode("utf-8"))
        hash_value = hash_object.hexdigest()

        self.logger.info(f"Hash {algorithm} generato con successo.", extra={'internal': True})
        return hash_value

    def decode(self, encoded_data: str) -> str:
        """Gli hash non sono decodificabili, quindi il metodo genera un'eccezione."""
        raise NotImplementedError("Gli hash non possono essere decodificati.")
