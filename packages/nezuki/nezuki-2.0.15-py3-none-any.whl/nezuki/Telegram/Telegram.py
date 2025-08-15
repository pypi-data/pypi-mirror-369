from Common import *

@versione("1.0.0")
class TelegramParser_OLD:
    def __init__(self, telegramInput: dict) -> None:
        """ Elabora l'input di Telegram creando gli oggett"""
        self.input: dict = telegramInput
        self.inputName: str = ""
        self._input_name()

    def _input_name(self) -> None:
        """ Ritorna il nome dell'input che è stato ricevuto da Telegram """
        if "message" in self.input:
            self.inputName = "message"
            self.info = _Message(self.input.get(self.inputName))
        elif "edited_message" in self.input:
            self.inputName = "edited_message"
        elif "edited_channel_post" in self.input:
            self.inputName = "edited_channel_post"
        elif "inline_query" in self.input:
            self.inputName = "inline_query"
        elif "callback_query" in self.input:
            self.inputName = "callback_query"
    
    def getInputName(self) -> str:
        return self.inputName
    
@versione("1.0.0")
class _Message:
    def __init__(self, input: dict):
        self.jsonTelegram:dict = input
        print(self.jsonTelegram)
        self.startParse()

    def startParse(self):
        self.message_id = self.jsonTelegram.get("message_id", None)
        self.message_thread_id = self.jsonTelegram.get("message_thread_id", None)
        self.fromm = _User(self.jsonTelegram.get("from", None))
        self.sender_chat = _Chat(self.jsonTelegram.get("sender_chat", None))
        self.chat = _Chat(self.jsonTelegram.get("chat", None))
        self.via_bot = _User(self.jsonTelegram.get("via_bot", None))

class _User:
    def __init__(self, input: dict):
        self.jsonTelegram: dict = input
        print(self.jsonTelegram)
        self.startParse()

    def startParse(self):
        self.id = self.jsonTelegram.get("id", None)
        self.is_bot = self.jsonTelegram.get("is_bot", None)
        self.first_name = self.jsonTelegram.get("first_name", None)
        self.last_name = self.jsonTelegram.get("last_name", None)
        self.username = self.jsonTelegram.get("username", None)
        self.language_code = self.jsonTelegram.get("language_code", None)
        self.is_premium = self.jsonTelegram.get("is_premium", None)
        self.added_to_attachment_menu = self.jsonTelegram.get("added_to_attachment_menu", None)
        self.can_join_groups = self.jsonTelegram.get("can_join_groups", None)
        self.can_read_all_group_messages = self.jsonTelegram.get("can_read_all_group_messages", None)
        self.supports_inline_queries = self.jsonTelegram.get("supports_inline_queries", None)
        self.can_connect_to_business = self.jsonTelegram.get("can_connect_to_business", None)

class _Chat:
    def __init__(self, input: dict):
        self.jsonTelegram: dict = input
        print(self.jsonTelegram)
        self.startParse()

    def startParse(self):
        self.id = self.jsonTelegram.get("id", None)
        self.type = self.jsonTelegram.get("type", None)
        self.title = self.jsonTelegram.get("title", None)
        self.username = self.jsonTelegram.get("username", None)
        self.first_name = self.jsonTelegram.get("first_name", None)
        self.last_name = self.jsonTelegram.get("last_name", None)
        self.is_forum = self.jsonTelegram.get("is_forum", None)












# input_example: dict = {
#   "update_id": 123456789,
#   "message": {
#     "message_id": 1,
#     "from": {
#       "id": 12345678,
#       "is_bot": False,
#       "first_name": "John",
#       "last_name": "Doe",
#       "username": "johndoe",
#       "language_code": "en"
#     },
#     "chat": {
#       "id": 12345678,
#       "first_name": "John",
#       "last_name": "Doe",
#       "username": "johndoe",
#       "type": "private"
#     },
#     "date": 1655412345,
#     "text": "/start"
#   }
# }

# test = TelegramParser(input_example)
# print(test.info.fromm.id)