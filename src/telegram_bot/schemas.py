from pydantic import BaseModel, UUID4, Field, HttpUrl, FileUrl


class Context(BaseModel):
    user_id: UUID4
    session_attributes: dict[str, str] = Field(default_factory=dict)
    active_contexts: list[dict] = Field(default_factory=list)


class MessageRequest(Context):
    input_text: str
    bot_name: str
    bot_alias: str
    request_attributes: dict[str, str] = Field(default_factory=dict)


class Button(BaseModel):
    text: str
    value: str


class Attachment(BaseModel):
    title: str
    sub_title: str
    link_url: HttpUrl
    image_url: FileUrl
    buttons: list[Button] = Field(default_factory=list)


class MessageResponse(Context):
    message: str
    session_id: str
    attachments: list[Attachment] = Field(default_factory=list)
