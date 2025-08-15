from nezuki.EncoderDecoder import EncoderDecoder
import qrcode
from io import BytesIO
import base64


# ----------------------------------------
# 📌 1. GENERATORE DI QR CODE
# ----------------------------------------

class QRCodeHandler(EncoderDecoder):
    """Gestisce la creazione e la lettura di QR Code."""

    def __init__(self):
        """Inizializza il gestore di QR Code con il logger ereditato da EncoderDecoder."""
        super().__init__()

    def encode(self, data: str, formato: str = "PNG", versione: int = 2, box_side: int = 10, border: int = 4) -> str:
        """
        Genera un QR Code e lo restituisce in base64.
        
        Args:
            data (str): Il dato da codificare nel QR Code.
            formato (str): Formato dell'immagine (default: PNG).
            versione (int): Versione del QR Code (default: 2).
            box_side (int): Dimensione delle celle (default: 10).
            border (int): Dimensione del bordo (default: 4).

        Returns:
            str: Il QR Code in formato base64.
        """
        if not data:
            raise ValueError("Errore: 'data' non può essere vuoto.")

        qr = qrcode.QRCode(
            version=versione,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=box_side,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format=formato)

        qr_code_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        self.logger.info("QR Code generato con successo.", extra={'internal': True})

        return qr_code_base64

    def decode(self, encoded_data: str) -> str:
        """Placeholder per decodificare un QR Code da un'immagine (da implementare in futuro)."""
        raise NotImplementedError("Decodifica QR Code non ancora supportata.")
