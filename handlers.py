from security import get_public_save_private_key
from telegram import Update
from telegram.ext import CallbackContext, ApplicationHandlerStop
from client import Client
from ai import Ai
import logging
from functools import partial

log = logging.getLogger()

clients: dict[str, Client] = {}
ais: dict[str, dict[str, Ai]] = {}

async def check_user(update: Update, context: CallbackContext, username: str):
    if update.message.from_user.username != username:
        raise ApplicationHandlerStop

async def start(update: Update, context: CallbackContext):
    log.info('Received start command')
    text = "Hello. If you are new here or want to change your ssh key pair, run /newkey. " \
           "Please note that this command will overwrite old private key."
    await update.message.reply_text(text=text)


async def new_key(update: Update, context: CallbackContext, path_to_keys: str):
    log.info('Received newkey command')
    public = get_public_save_private_key(path_to_keys)
    await update.message.reply_text(text=public.decode('utf-8'))
    text = "You have just received the public key. " \
           "Private key was stored in the directory from which the bot is running. " \
           "Please, add it to the authorized keys on the server. " \
           "This can be done, by appending public key to server's authorized_keys file (~/.ssh/authorized_keys)."
    await update.message.reply_text(text=text)

messages_to_thread = {}

def get_thread_id(message):
    if message.reply_to_message is None:
        messages_to_thread[message.message_id] = message.message_id
    else:
        messages_to_thread[message.message_id] = messages_to_thread[message.reply_to_message.message_id]
    return messages_to_thread[message.message_id]

async def shell(update: Update, context: CallbackContext, connection_info):
    log.info(f'Received chat: {update.message.text}')

    chat_id = update.message.chat_id

    thread_id = get_thread_id(update.message)

    log.info(f'Thread id: %s' % thread_id)

    if chat_id not in ais:
        ais[chat_id] = {}

    if thread_id not in ais[chat_id]:
        ais[chat_id][thread_id] = Ai(Client(connection_info))
        ais[chat_id][thread_id].callback = partial(send_message, chat_id = chat_id, bot = context.bot)

    response = await ais[chat_id][thread_id].turn_into_command(update.message.text)
    if response:
        await send_message(response, chat_id, context.bot, update.message.message_id)

async def send_message(message, chat_id, bot, reply_to_message_id):
    print(f'sending ${message}')
    try:
        msgs = [message[i:i + 4096] for i in range(0, len(message), 4096)]
        for text in msgs:
            msg = await bot.send_message(
                chat_id = chat_id,
                text = text,
                reply_to_message_id = reply_to_message_id,
            )
            get_thread_id(msg)
    except Exception as e:
        print(f'Exception {e}')
