from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Type, Union, TypeVar, Literal, Optional, get_origin, get_args
import rubigram


T = TypeVar("T", bound="Dict")

@dataclass
class Dict:
    def to_dict(self) -> dict[str, Any]:
        data = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if is_dataclass(value):
                data[field.name] = value.to_dict()
            elif isinstance(value, list):
                data[field.name] = [i.to_dict() if is_dataclass(i) else i for i in value]
            else:
                data[field.name] = value
        return data

    @classmethod
    def from_dict(cls: Type[T], data: dict[str, Any]) -> Optional[T]:
        if data is None:
           return cls()
        init_data = {}
        for field in fields(cls):
            value = data.get(field.name)
            field_type = field.type
            origin = get_origin(field_type)
            if isinstance(value, dict) and isinstance(field_type, type) and issubclass(field_type, Dict):
                init_data[field.name] = field_type.from_dict(value)
            elif origin == list:
                inner_type = get_args(field_type)[0]
                if isinstance(inner_type, type) and issubclass(inner_type, Dict):
                    init_data[field.name] = [inner_type.from_dict(v) if isinstance(v, dict) else v for v in (value or [])]
                else:
                    init_data[field.name] = value or []
            elif get_origin(field_type) is Union:
                args = get_args(field_type)
                dict_type = next((a for a in args if isinstance(a, type) and issubclass(a, Dict)), None)
                if dict_type and isinstance(value, dict):
                    init_data[field.name] = dict_type.from_dict(value)
                else:
                    init_data[field.name] = value
            else:
                init_data[field.name] = value
        return cls(**init_data)


@dataclass
class Location(Dict):
    longitude: Optional[str] = None
    latitude: Optional[str] = None


@dataclass
class OpenChatData(Dict):
    object_guid: Optional[str] = None
    object_type: Optional[Literal["User", "Bot", "Group", "Channel"]] = None


@dataclass
class JoinChannelData(Dict):
    username: Optional[str] = None
    ask_join: Optional[bool] = False

@dataclass
class ButtonLink(Dict):
    type: Optional[Literal["joinchannel", "url"]] = None
    link_url: Optional[str] = None
    joinchannel_data: Optional[JoinChannelData] = None
    open_chat_data: Optional[OpenChatData] = None


@dataclass
class ButtonSelectionItem(Dict):
    text: Optional[str] = None
    image_url: Optional[str] = None
    type: Optional[Literal["TextOnly", "TextImgThu", "TextImgBig"]] = None


@dataclass
class ButtonTextbox(Dict):
    type_line: Optional[Literal["SingleLine", "MultiLine"]] = None
    type_keypad: Optional[Literal["String", "Number"]] = None
    place_holder: Optional[str] = None
    title: Optional[str] = None
    default_value: Optional[str] = None


@dataclass
class ButtonLocation(Dict):
    default_pointer_location: Optional[Location] = None
    default_map_location: Optional[Location] = None
    type: Optional[Literal["Picker", "View"]] = None
    title: Optional[str] = None
    location_image_url: Optional[str] = None


@dataclass
class ButtonStringPicker(Dict):
    items: Optional[list[str]] = None
    default_value: Optional[str] = None
    title: Optional[str] = None


@dataclass
class ButtonNumberPicker(Dict):
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    default_value: Optional[str] = None
    title: Optional[str] = None


@dataclass
class ButtonCalendar(Dict):
    default_value: Optional[str] = None
    type: Optional[Literal["DatePersian", "DateGregorian"]] = None
    min_year: Optional[str] = None
    max_year: Optional[str] = None
    title: Optional[str] = None


@dataclass
class ButtonSelection(Dict):
    selection_id: Optional[str] = None
    search_type: Optional[str] = None
    get_type: Optional[str] = None
    items: Optional[list[ButtonSelectionItem]] = None
    is_multi_selection: Optional[bool] = None
    columns_count: Optional[str] = None
    title: Optional[str] = None


@dataclass
class Button(Dict):
    id: Optional[str] = None
    button_text: Optional[str] = None
    type: Literal[
        "Simple", "Selection", "Calendar", "NumberPicker", "StringPicker", "Location", "Payment",
        "CameraImage", "CameraVideo", "GalleryImage", "GalleryVideo", "File", "Audio", "RecordAudio",
        "MyPhoneNumber", "MyLocation", "Textbox", "Link", "AskMyPhoneNumber", "AskLocation", "Barcode"
    ] = "Simple"
    button_selection: Optional[ButtonSelection] = None
    button_calendar: Optional[ButtonCalendar] = None
    button_number_picker: Optional[ButtonNumberPicker] = None
    button_string_picker: Optional[ButtonStringPicker] = None
    button_location: Optional[ButtonLocation] = None
    button_textbox: Optional[ButtonTextbox] = None
    button_link: Optional[ButtonLink] = None


@dataclass
class KeypadRow(Dict):
    buttons: list[Button]


@dataclass
class Keypad(Dict):
    rows: list[KeypadRow]
    resize_keyboard: bool = True
    on_time_keyboard: bool = False


@dataclass
class PollStatus(Dict):
    state: Optional[Literal["Open", "Closed"]] = None
    selection_index: Optional[int] = None
    percent_vote_options: Optional[list[int]] = None
    total_vote: Optional[int] = None
    show_total_votes: Optional[bool] = None


@dataclass
class File(Dict):
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    size: Optional[str] = None


@dataclass
class LiveLocation(Dict):
    start_time: Optional[str] = None
    live_period: Optional[int] = None
    current_location: Optional[Location] = None
    user_id: Optional[str] = None
    status: Optional[Literal["Stopped", "Live"]] = None
    last_update_time: Optional[str] = None


@dataclass
class Poll(Dict):
    question: Optional[str] = None
    options: Optional[list[str]] = None
    poll_status: Optional[PollStatus] = None


@dataclass
class ContactMessage(Dict):
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@dataclass
class Sticker(Dict):
    sticker_id: Optional[str] = None
    file: Optional[File] = None
    emoji_character: Optional[str] = None


@dataclass
class ForwardedFrom(Dict):
    type_from: Optional[Literal["User", "Channel", "Bot"]] = None
    message_id: Optional[str] = None
    from_chat_id: Optional[str] = None
    from_sender_id: Optional[str] = None


@dataclass
class AuxData(Dict):
    start_id: Optional[str] = None
    button_id: Optional[str] = None


@dataclass
class PaymentStatus(Dict):
    payment_id: Optional[str] = None
    status: Optional[Literal["Paid", "NotPaid"]] = None


@dataclass
class Message(Dict):
    message_id: Optional[str] = None
    text: Optional[str] = None
    time: Optional[str] = None
    is_edited: Optional[bool] = None
    sender_type: Optional[Literal["User", "Bot"]] = None
    sender_id: Optional[str] = None
    aux_data: Optional[AuxData] = None
    file: Optional[File] = None
    reply_to_message_id: Optional[str] = None
    forwarded_from: Optional[ForwardedFrom] = None
    forwarded_no_link: Optional[str] = None
    location: Optional[Location] = None
    sticker: Optional[Sticker] = None
    contact_message: Optional[ContactMessage] = None
    poll: Optional[Poll] = None
    live_location: Optional[LiveLocation] = None


@dataclass
class InlineMessage(Dict):
    sender_id: Optional[str] = None
    text: Optional[str] = None
    message_id: Optional[str] = None
    chat_id: Optional[str] = None
    file: Optional[File] = None
    location: Optional[Location] = None
    aux_data: Optional[AuxData] = None


@dataclass
class Bot(Dict):
    bot_id: Optional[str] = None
    bot_title: Optional[str] = None
    avatar: Optional[File] = None
    description: Optional[str] = None
    username: Optional[str] = None
    start_message: Optional[str] = None
    share_url: Optional[str] = None


@dataclass
class Chat(Dict):
    chat_id: Optional[str] = None
    chat_type: Optional[Literal["User", "Bot", "Group", "Channel"]] = None
    user_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    username: Optional[str] = None


@dataclass
class MessageId(Dict):
    message_id: Optional[str] = None
    file_id: Optional[str] = None


@dataclass
class Update(Dict):
    client: Optional["rubigram.Client"] = None
    type: Optional[Literal["NewMessage", "UpdatedMessage", "RemovedMessage", "StartedBot", "StoppedBot", "UpdatedPayment"]] = None
    chat_id: Optional[str] = None
    removed_message_id: Optional[str] = None
    new_message: Optional[Message] = None
    updated_message: Optional[Message] = None
    updated_payment: Optional[PaymentStatus] = None
    
    async def send_text(
        self,
        text: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad= None,
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = None,
        reply_to_message_id = None
    ) -> "MessageId":
        return await self.client.send_message(self.chat_id, text, chat_keypad, inline_keypad, chat_keypad_type, disable_notification, reply_to_message_id)
    
    async def reply(
        self,
        text: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad= None,
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = None,
    ) -> "MessageId":
        return await self.client.send_message(self.chat_id, text, chat_keypad, inline_keypad, chat_keypad_type, disable_notification, self.new_message.message_id)
    
    async def reply_file(
        self,
        file: str,
        file_name: str,
        type: Literal["File", "Image", "Voice", "Music", "Gif", "Video"] = "File",
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_file(
            self.chat_id,
            file,
            file_name,
            type,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id
        )
        
    async def reply_document(
        self,
        document: str,
        name: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_document(
            self.chat_id,
            document,
            name,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id
        )
        
    async def reply_photo(
        self,
        photo: str,
        name: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_photo(
            self.chat_id,
            photo,
            name,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id
        )
        
    async def reply_video(
        self,
        video: str,
        name: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_video(
            self.chat_id,
            video,
            name,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id
        )
        
    async def reply_gif(
        self,
        gif: str,
        name: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_gif(
            self.chat_id,
            gif,
            name,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id
        )
        
    async def reply_music(
        self,
        music: str,
        name: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_music(
            self.chat_id,
            music,
            name,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id
        )
        
    async def replyvoice(
        self,
        voice: str,
        name: str,
        chat_keypad: Keypad = None,
        inline_keypad: Keypad = None,
        chat_keypad_type: Literal["New", "Remove"] = None,
        disable_notification: bool = False,
    ) -> "MessageId":
        return await self.client.send_voice(
            self.chat_id,
            voice,
            name,
            chat_keypad,
            inline_keypad,
            chat_keypad_type,
            disable_notification,
            self.new_message.message_id
        )