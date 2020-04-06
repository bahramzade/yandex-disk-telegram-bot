from flask import g

from .....api import telegram, yandex
from ..decorators import (
    yd_access_token_required,
    get_db_data
)
from ..responses import (
    cancel_command
)


class YandexAPIRequestError(Exception):
    """
    Some error during Yandex.Disk API request occured.
    """
    pass


class YandexAPIError(Exception):
    """
    Error response from Yandex.Disk API.
    """
    pass


@yd_access_token_required
@get_db_data
def handle():
    """
    Handles `/create_folder` command.
    """
    message = g.incoming_message
    user = g.db_user
    chat = g.db_incoming_chat
    access_token = user.yandex_disk_token.get_access_token()
    message_text = get_text(message)
    message_folder_name = message_text.replace("/create_folder", "").strip()
    last_status_code = None

    try:
        last_status_code = create_folder(
            access_token=access_token,
            folder_name=message_folder_name
        )
    except YandexAPIRequestError as e:
        print(e)
        return cancel_command(chat.telegram_id)
    except YandexAPIError as e:
        error_text = "Yandex.Disk Error"

        if hasattr(e, "message"):
            error_text = e.message

        return telegram.send_message(
            chat_id=chat.telegram_id,
            text=error_text
        )

    text = None

    if (last_status_code == 201):
        text = "Created"
    elif (last_status_code == 409):
        text = "Already exists"
    else:
        text = f"Unknown status code: {last_status_code}"

    telegram.send_message(
        chat_id=chat.telegram_id,
        text=text
    )


def get_text(message: dict) -> str:
    """
    Extracts text from a message.
    """
    return (
        message.get("text") or
        message.get("caption") or
        ""
    )


def is_error_response(data: dict) -> bool:
    """
    :returns: Yandex response contains error or not.
    """
    return ("error" in data)


def create_error_text(data: dict) -> str:
    """
    Constructs error text from Yandex error response.
    """
    error_name = data["error"]
    error_description = (
        data.get("message") or
        data.get("description") or
        "?"
    )

    return (
        "Yandex.Disk Error: "
        f"{error_name} ({error_description})"
    )


def create_folder(access_token: str, folder_name: str) -> int:
    """
    Creates folder using Yandex API.

    Yandex not able to create folder if some of
    middle folders not exists. This method will try to create
    each folder one by one, and ignore safe errors (if
    already exists, for example) from all folder names
    except last one.

    :returns: Last (for last folder name) HTTP Status code.

    :raises: YandexAPIRequestError
    :raises: YandexAPIError
    """
    folders = [x for x in folder_name.split("/") if x]
    folder_path = ""
    last_status_code = 201  # root always created
    allowed_errors = [409]

    for folder in folders:
        response = None
        folder_path = f"{folder_path}/{folder}"

        try:
            response = yandex.create_folder(
                access_token,
                path=folder_path
            )
        except Exception as e:
            raise YandexAPIRequestError(e)

        last_status_code = response["HTTP_STATUS_CODE"]

        if (
            (last_status_code == 201) or
            (not is_error_response(response)) or
            (last_status_code in allowed_errors)
        ):
            continue

        raise YandexAPIError(
            create_error_text(response)
        )

    return last_status_code
