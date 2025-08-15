from JsonManager import JsonManager
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from Common import *
from commonLogId import *

current_version = "1.0.0"

@versione("1.0.0")
@dataclass
class _User:
    """ Oggetto che rappresenta l'utente o il bot """
    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    added_to_attachment_menu: Optional[bool] = None
    can_join_groups: Optional[bool] = None
    can_read_all_group_messages: Optional[bool] = None
    supports_inline_queries: Optional[bool] = None
    can_connect_to_business: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_User':
        """Converte l'input in un oggetto _User"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _Chat:
    """ Rappresenta la chat """
    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_forum: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_Chat':
        """Converte l'input in un oggetto _Chat"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _MessageEntity:
    """ Rappresenta una speciale entità nel messaggio di testo """
    type: str
    offset: int
    length: int
    url: Optional[str] = None
    user: Optional[_User] = None
    language: Optional[str] = None
    custom_emoji_id: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_MessageEntity':
        """Converte l'input in un oggetto _MessageEntity"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _LinkPreviewOptions:
    """ Rappresenta le imppstazioni usate per la generazione dell'anteprima del link """
    is_disabled: Optional[bool] = None
    url: Optional[str] = None
    prefer_small_media: Optional[bool] = None
    prefer_large_media: Optional[bool] = None
    show_above_text: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_LinkPreviewOptions':
        """Converte l'input in un oggetto _LinkPreviewOptions"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _PhotoSize:
    """ Informazioni sulle foto o un'anteprima degli sticker o dei file"""
    file_id: str
    file_unique_id: str
    width: int
    height: int
    file_size: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_PhotoSize':
        """Converte l'input in un oggetto _PhotoSize"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _Audio:
    """ Oggetto che rappresenza un audio che deve essere trattato come musica dai client Telegram """
    file_id: str
    file_unique_id: str
    duration: int
    performer: Optional[str] = None
    title: Optional[str] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    thumbnail: Optional[_PhotoSize] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_Audio':
        """Converte l'input in un oggetto _Audio"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _Document:
    """ Oggetto che rappresenta un file generico, tutto ciò che non rientra in altre tipologie di file """
    file_id: str
    file_unique_id: str
    thumbnail: Optional[_PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_Document':
        """Converte l'input in un oggetto _Document"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _Animation:
    """ Rappresenza il file animato come GIF o H.264/MPEG-4 AVC senza audio """
    file_id: str
    file_unique_id: str
    width: int
    height: int
    duration: int
    thumbnail: Optional[_PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_Animation':
        """Converte l'input in un oggetto _Animation"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _TextQuote:
    """ Oggetto che contiene la citazione alla parte di messaggio alla quale è stata fatta una risposta """
    text: str
    entities: Optional[List[_MessageEntity]] = None
    position: Optional[int] = None
    is_manual: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_TextQuote':
        """Converte l'input in un oggetto _TextQuote"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _Story:
    """ Rappresenta una storia Telegram """
    chat: _Chat
    id: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_Story':
        """Converte l'input in un oggetto _Story"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _File:
    """ Informazioni relative ad un File che è pronto per essere scaricato, può essere scaricato dal link dell'API Bot con il file_path messo in coda."""
    file_id: str
    file_unique_id: str
    file_size: Optional[int] = None
    file_path: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_File':
        """Converte l'input in un oggetto _File"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _MaskPosition:
    """ La maschera in che posizione deve essere posizionata"""
    point: str
    x_shift: float
    y_shift: float
    scale: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_MaskPosition':
        """Converte l'input in un oggetto _MaskPosition"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _Sticker:
    """ Informazioni sullo sticker """
    file_id: str
    file_unique_id: str
    type: str
    width: int
    height: int
    is_animated: bool
    is_video: bool
    thumbnail: Optional[_PhotoSize] = None
    emoji: Optional[str] = None
    set_name: Optional[str] = None
    premium_animation: Optional[_File] = None
    mask_position: Optional[_MaskPosition] = None
    custom_emoji_id: Optional[str] = None
    needs_repainting: Optional[bool] = None
    file_size: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_Sticker':
        """Converte l'input in un oggetto _Sticker"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _MessageOrigin:
    """ Il messaggio in che modo è stato inviato """
    original_message: '_Message'
    origin_type: str  # "sent", "forwarded_from_user", "forwarded_from_chat", etc.
    original_sender: Optional[_User] = None
    original_chat: Optional[_Chat] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_MessageOrigin':
        """Converte l'input in un oggetto _MessageOrigin"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _ExternalReplyInfo:
    """ Indica il messaggio al quale è stato risposto da dove proviene """
    origin: _MessageOrigin
    chat: Optional[_Chat] = None
    message_id: Optional[int] = None
    link_preview_options: Optional[_LinkPreviewOptions] = None
    animation: Optional[_Animation] = None
    audio: Optional[_Audio] = None
    document: Optional[_Document] = None
    photo: Optional[_PhotoSize] = None
    sticker: Optional[_Sticker] = None
    story: Optional[_Story] = None
    # video: Optional[_Video] = None
    # video_note: Optional[_VideoNote] = None
    # voice: Optional[_Voice] = None
    # has_media_spoiler: Optional[bool] = None
    # contact: Optional[_Contact] = None
    # dice: Optional[_Dice] = None
    # game: Optional[_Game] = None
    # giveaway: Optional[_Giveaway] = None
    # giveaway_winners: Optional[_GiveawayWinners] = None
    # invoice: Optional[_Invoice] = None
    # location: Optional[_Location] = None
    # poll: Optional[_Poll] = None
    # venue: Optional[_Venue] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_ExternalReplyInfo':
        """Converte l'input in un oggetto _ExternalReplyInfo"""
        return cls(**data)

@versione("1.0.0")
@dataclass
class _Message:
    """ Rappresenta il messaggio su Telegram"""
    message_id: int
    date: int
    chat: _Chat
    message_thread_id: Optional[int] = None
    from_user: Optional[_User] = None
    sender_chat: Optional[_Chat] = None
    sender_boost_count: Optional[int] = None
    sender_business_bot: Optional[_User] = None
    business_connection_id: Optional[str] = None
    forward_origin: Optional[_MessageOrigin] = None
    is_topic_message: Optional[bool] = None
    is_automatic_forward: Optional[bool] = None
    reply_to_message: Optional['_Message'] = None
    external_reply: Optional[_ExternalReplyInfo] = None
    quote: Optional[_TextQuote] = None
    reply_to_story: Optional[_Story] = None
    via_bot: Optional[_User] = None
    edit_date: Optional[int] = None
    has_protected_content: Optional[bool] = None
    is_from_offline: Optional[bool] = None
    media_group_id: Optional[str] = None
    author_signature: Optional[str] = None
    text: Optional[str] = None
    entities: Optional[List[_MessageEntity]] = None
    link_preview_options: Optional[_LinkPreviewOptions] = None
    animation: Optional[_Animation] = None
    audio: Optional[_Audio] = None
    document: Optional[_Document] = None
    photo: Optional[List[_PhotoSize]] = None
    sticker: Optional[_Sticker] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '_Message':
        """Converte l'input in un oggetto _Message"""
        data['chat'] = _Chat.from_dict(data['chat'])
        if 'reply_to_message' in data:
            data['reply_to_message'] = _Message.from_dict(data['reply_to_message'])
        if 'from' in data:
            data['from_user'] = _User.from_dict(data.pop('from'))
        return cls(**data)

@versione("1.0.0")
class TelegramParser:
    """ Classe che si occupa di fare il parsing dell'input """
    def __init__(self, inputTelegram: dict)->None:
        """ Inizializza l'oggetto Parser"""
        self.logger = get_logger()
        # super().__init__(botToken)
        self.input: dict = inputTelegram
        self.json = JsonManager(self.input)
        self.inputName()
    
    def inputName(self)->None:
        """ Fornisce il nome dell'input ricevuto e le informazioni nel formato oggetto """
        if "message" in self.input:
            self.inputType = "message"
            self.info = _Message.from_dict(self.json.retrieveKey(self.inputType))
        elif "edited_message" in self.input:
            self.inputType = "edited_message"
            self.info = _Message.from_dict(self.json.retrieveKey(self.inputType))
        elif "edited_channel_post" in self.input:
            self.inputType = "edited_channel_post"
            self.info = _Message.from_dict(self.json.retrieveKey(self.inputType))
        # elif "inline_query" in self.input:
        #     self.inputType = "inline_query"
        # elif "callback_query" in self.input:
        #     self.inputType = "callback_query"

# input_example: dict = {"update_id":99758500, "message":{"message_id":11,"from":{"id":23326587,"is_bot":False,"first_name":"\u2060","last_name":"\u2060","username":"KingKaitoKid","language_code":"it","is_premium":True},"chat":{"id":23326587,"first_name":"\u2060","last_name":"\u2060","username":"KingKaitoKid","type":"private"},"date":1717811389,"text":"/start","entities":[{"offset":0,"length":6,"type":"bot_command"}]}}

# test = TelegramParser(input_example)

# # print(test.inputType)
# print(test.info.from_user.id)
# print(test.info.chat.id)
# # print(test.info.reply_to_message.from_user.id)
# print(test.info.date)