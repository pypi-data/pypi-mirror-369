import smtplib
import os
import argparse
import json
from email.message import EmailMessage
from nezuki.Logger import get_nezuki_logger

logger = get_nezuki_logger()

class Mail:
    """
    Classe per l'invio di email con supporto a SMTP.

    Può leggere i parametri di connessione da:
    - Argomenti passati alla classe
    - Un file JSON specificato nella variabile d'ambiente NEZUKIMAIL

    Se nessun parametro è specificato, la variabile d'ambiente è obbligatoria.
    """

    def __init__(self, smtp_config: dict = None):
        """
        Inizializza la configurazione SMTP.

        Args:
            smtp_config (dict, opzionale): Dizionario con i parametri SMTP (host, port, user, pass, root_email).
                                           Se non fornito, tenta di leggere la variabile d'ambiente `NEZUKIMAIL`.
        """
        self.logger = get_nezuki_logger()

        if smtp_config is None:
            json_path = os.getenv("NEZUKIMAIL")
            if json_path and os.path.isfile(json_path):
                with open(json_path, "r") as file:
                    smtp_config = json.load(file)
                self.logger.info(f"Lettura configurazione SMTP da variabile d'ambiente NEZUKIMAIL ({json_path})", extra={"internal": True})
            else:
                raise ValueError("Errore: Né i parametri SMTP né la variabile d'ambiente NEZUKIMAIL sono forniti!")

        self.root_mail = smtp_config.get("root_email")
        self.smtp_host = smtp_config.get("host")
        self.smtp_port = smtp_config.get("port")
        self.user = smtp_config.get("user")
        self.password = smtp_config.get("pass")

    def build_sender_mail(self, sender_name: str = "Nezuki Mail") -> str:
        """
        Genera il formato corretto per il mittente.

        Args:
            sender_name (str): Nome visualizzato del mittente. Default: "Nezuki Mail".

        Returns:
            str: Stringa formattata "<Nome> <email>"
        """
        return f"{sender_name} <{self.root_mail}>"

    def send_mail(self, sender_name: str, dest: list | str, subject: str, body: str, cc: list | str | None = None):
        """
        Invia un'email utilizzando SMTP.

        Args:
            sender_name (str): Nome del mittente visualizzato.
            dest (list|str): Destinatario (stringa singola o lista di email).
            subject (str): Oggetto dell'email.
            body (str): Contenuto del messaggio.
            cc (list|str|None): Destinatari in copia (opzionale, stringa o lista).
        """
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg["Subject"] = subject
            msg["From"] = self.build_sender_mail(sender_name)
            msg["To"] = ", ".join(dest) if isinstance(dest, list) else dest
            if cc:
                msg["Cc"] = ", ".join(cc) if isinstance(cc, list) else cc

            msg.add_alternative(body, subtype="html")

            self.logger.debug(f"Email pronta all'invio", extra={"internal": True, "details": str(msg)})

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as smtp_server:
                smtp_server.starttls()
                smtp_server.login(self.user, self.password)
                smtp_server.send_message(msg)

            self.logger.info(f"Email inviata con successo", extra={"internal": True, "details": str(msg)})

        except smtplib.SMTPException as e:
            self.logger.error(f"Errore SMTP durante l'invio", extra={"internal": True, "details": str(e)})


# --- CLI COMMAND ---
def main():
    """
    Interfaccia a riga di comando per inviare email.

    Se non vengono forniti parametri SMTP, utilizza la configurazione dalla variabile d'ambiente `NEZUKIMAIL`.
    """
    parser = argparse.ArgumentParser(description="Modulo per inviare email con SMTP.")

    # Parametri per il server SMTP (opzionali, si può usare NEZUKIMAIL)
    parser.add_argument("--smtp-host", type=str, help="Hostname del server SMTP")
    parser.add_argument("--smtp-port", type=int, help="Porta SMTP")
    parser.add_argument("--smtp-user", type=str, help="Username SMTP")
    parser.add_argument("--smtp-pass", type=str, help="Password SMTP")
    parser.add_argument("--root-email", type=str, help="Email principale per il mittente")

    # Parametri per il messaggio
    parser.add_argument("--from", dest="sender_name", type=str, required=True, help="Nome del mittente")
    parser.add_argument("--to", type=str, required=True, help="Destinatario (singolo o multiplo, separati da virgole)")
    parser.add_argument("--subject", type=str, required=True, help="Oggetto dell'email")
    parser.add_argument("--body", type=str, required=True, help="Corpo dell'email")
    parser.add_argument("--cc", type=str, default=None, help="Destinatari in copia (opzionale, separati da virgola)")

    args = parser.parse_args()

    # Se i parametri SMTP sono passati, usiamo quelli, altrimenti leggiamo NEZUKIMAIL
    # Se i parametri SMTP sono passati, usiamo quelli, altrimenti leggiamo NEZUKIMAIL
    smtp_config = None

    if args.smtp_host and args.smtp_port and args.smtp_user and args.smtp_pass and args.root_email:
        smtp_config = {
            "host": args.smtp_host,
            "port": args.smtp_port,
            "user": args.smtp_user,
            "pass": args.smtp_pass,
            "root_email": args.root_email
        }
    else:
        # Leggiamo la variabile d'ambiente NEZUKIMAIL
        json_path = os.getenv("NEZUKIMAIL")
        if json_path and os.path.isfile(json_path):
            with open(json_path, "r") as file:
                smtp_config = json.load(file)
            logger.info(f"Lettura configurazione SMTP da variabile d'ambiente NEZUKIMAIL ({json_path})", extra={"internal": True})
        else:
            raise ValueError("Errore: Né i parametri SMTP né la variabile d'ambiente NEZUKIMAIL sono forniti!")

        # Creazione client email
        mail_client = Mail(smtp_config)
        recipients = args.to.split(",")
        cc_recipients = args.cc.split(",") if args.cc else None


    # Invio mail
    mail_client.send_mail(
        sender_name=args.sender_name,
        dest=recipients,
        subject=args.subject,
        body=args.body,
        cc=cc_recipients
    )


if __name__ == "__main__":
    main()
