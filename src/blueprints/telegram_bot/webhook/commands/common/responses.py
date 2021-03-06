from src.api import telegram


def abort_command(
    chat_telegram_id: int,
    edit_message: int = None,
    reply_to_message: int = None
) -> None:
    """
    Aborts command execution due to invalid message data.

    - don't confuse with `cancel_command()`.
    - if `edit_message` Telegram ID specified, then
    that message will be edited.
    - if `reply_to_message` Telegram ID specified, then
    that message will be used for reply message.
    """
    text = (
        "I can't handle this because "
        "you didn't send any suitable data "
        "for that command."
    )

    if (edit_message is not None):
        telegram.edit_message_text(
            chat_id=chat_telegram_id,
            message_id=edit_message,
            text=text
        )
    elif (reply_to_message is not None):
        telegram.send_message(
            chat_id=chat_telegram_id,
            reply_to_message_id=reply_to_message,
            text=text
        )
    else:
        telegram.send_message(
            chat_id=chat_telegram_id,
            text=text
        )


def cancel_command(
    chat_telegram_id: int,
    edit_message: int = None,
    reply_to_message: int = None
) -> None:
    """
    Cancels command execution due to internal server error.

    - don't confuse with `abort_command()`.
    - if `edit_message` Telegram ID specified, then
    that message will be edited.
    - if `reply_to_message` Telegram ID specified, then
    that message will be used for reply message.
    """
    text = (
        "At the moment i can't process this "
        "because of my internal error. "
        "Try later please."
    )

    if (edit_message is not None):
        telegram.edit_message_text(
            chat_id=chat_telegram_id,
            message_id=edit_message,
            text=text
        )
    elif (reply_to_message is not None):
        telegram.send_message(
            chat_id=chat_telegram_id,
            reply_to_message_id=reply_to_message,
            text=text
        )
    else:
        telegram.send_message(
            chat_id=chat_telegram_id,
            text=text
        )


def request_private_chat(chat_telegram_id: int) -> None:
    """
    Aborts command execution due to lack of private chat with user.
    """
    telegram.send_message(
        chat_id=chat_telegram_id,
        text=(
            "I need to send you your secret information, "
            "but i don't know any private chat with you. "
            "First, contact me through private chat (direct message). "
            "After that repeat your request."
        )
    )
