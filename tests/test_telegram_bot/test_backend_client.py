import pytest

from pytest_mock import MockFixture
from uuid import uuid4

from src.telegram_bot.backend_client import Client
from src.telegram_bot.schemas import MessageRequest, MessageResponse


class ResponseMock:

    def __init__(self, data: dict | None, status: int):
        self.__data = data
        self.__status = status

    def __call__(self, *args, **kwargs) -> "ResponseMock":
        return self

    async def __aenter__(self) -> "ResponseMock":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def status(self) -> int:
        return self.__status

    async def json(self) -> dict:
        return self.__data


class SessionMock:

    def __init__(self, **methods: ResponseMock):
        self.__methods = methods

    def __call__(self, *args, **kwargs) -> "SessionMock":
        return self

    def __getattr__(self, item: str) -> ResponseMock:
        return self.__methods[item]

    async def __aenter__(self) -> "SessionMock":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def client() -> Client:
    return Client("http://localhost")


@pytest.mark.asyncio
async def test_get_user_id(mocker: MockFixture, client: Client):
    expected_user_id = str(uuid4())
    session_mock = SessionMock(get=ResponseMock({"user_id": expected_user_id}, 200))
    mocker.patch('aiohttp.ClientSession', return_value=session_mock)

    user_id = await client.get_user_id(123)
    assert user_id == expected_user_id


@pytest.mark.parametrize(["log_level", "code", "message"], [
    ("INFO", 404, "Client '{telegram_id}' not found"),
    ("ERROR", 500, "Receiving user '{telegram_id}' was failed on the server side")
])
@pytest.mark.asyncio
async def test_get_user_id_failure(
        mocker: MockFixture,
        client: Client,
        caplog: pytest.LogCaptureFixture,
        log_level: str,
        code: int,
        message: str
):
    telegram_id = 123
    session_mock = SessionMock(get=ResponseMock(None, code))
    mocker.patch('aiohttp.ClientSession', return_value=session_mock)

    user_id = await client.get_user_id(telegram_id)
    assert user_id is None
    assert caplog.records[0].levelname == log_level
    assert caplog.records[0].message == message.format(telegram_id=telegram_id) in caplog.text


@pytest.mark.asyncio
async def test_create_user(mocker: MockFixture, client: Client):
    expected_user_id = str(uuid4())
    session_mock = SessionMock(post=ResponseMock({"user_id": expected_user_id}, 200))
    mocker.patch('aiohttp.ClientSession', return_value=session_mock)

    user_id = await client.create_user(123)
    assert user_id == expected_user_id


@pytest.mark.parametrize(["log_level", "code", "message"], [
    ("ERROR", 500, "Creating user '{telegram_id}' was failed on the server side")
])
@pytest.mark.asyncio
async def test_create_user_failure(
        mocker: MockFixture,
        client: Client,
        caplog: pytest.LogCaptureFixture,
        log_level: str,
        code: int,
        message: str
):
    telegram_id = 123
    session_mock = SessionMock(post=ResponseMock(None, code))
    mocker.patch('aiohttp.ClientSession', return_value=session_mock)

    user_id = await client.create_user(telegram_id)
    assert user_id is None
    assert caplog.records[0].levelname == log_level
    assert caplog.records[0].message == message.format(telegram_id=telegram_id)


@pytest.mark.asyncio
async def test_send_message(mocker: MockFixture, client: Client):
    expected_user_id = str(uuid4())
    message_request = MessageRequest(**{
        "input_text": "test",
        "bot_name": "test",
        "bot_alias": "test",
        "user_id": expected_user_id
    })
    expected_message_response = MessageResponse(**{
        "message": "test",
        "session_id": "test",
        "user_id": expected_user_id
    })
    session_mock = SessionMock(post=ResponseMock(expected_message_response.dict(), 200))
    mocker.patch('aiohttp.ClientSession', return_value=session_mock)

    message_response = await client.send_message(message_request)
    assert message_response == expected_message_response


@pytest.mark.parametrize(["log_level", "code", "message"], [
    ("ERROR", 500, "Server didn't response to user '{user_id}' on message '{input_text}'")
])
@pytest.mark.asyncio
async def test_send_message_failure(
        mocker: MockFixture,
        client: Client,
        caplog,
        log_level: str,
        code: int,
        message: str
):
    message_request = MessageRequest(**{
        "input_text": "test",
        "bot_name": "test",
        "bot_alias": "test",
        "user_id": str(uuid4())
    })
    session_mock = SessionMock(post=ResponseMock(None, code))
    mocker.patch('aiohttp.ClientSession', return_value=session_mock)

    message_response = await client.send_message(message_request)
    assert message_response is None
    assert caplog.records[0].levelname == log_level
    assert caplog.records[0].message == message.format(
        user_id=message_request.user_id,
        input_text=message_request.input_text
    )
