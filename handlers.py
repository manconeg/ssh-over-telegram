from security import get_public_save_private_key
from telegram import Update
from telegram.ext import CallbackContext, ApplicationHandlerStop
from client import Client
from ai import Ai
import logging
from functools import partial

logger = logging.getLogger()

clients: dict[str, Client] = {}
ais: dict[str, Ai] = {}

async def check_user(update: Update, context: CallbackContext, username: str):
    if update.message.from_user.username != username:
        raise ApplicationHandlerStop

async def start(update: Update, context: CallbackContext):
    logger.info('Received start command')
    text = "Hello. If you are new here or want to change your ssh key pair, run /newkey. " \
           "Please note that this command will overwrite old private key."
    await update.message.reply_text(text=text)


async def new_key(update: Update, context: CallbackContext, path_to_keys: str):
    logger.info('Received newkey command')
    public = get_public_save_private_key(path_to_keys)
    await update.message.reply_text(text=public.decode('utf-8'))
    text = "You have just received the public key. " \
           "Private key was stored in the directory from which the bot is running. " \
           "Please, add it to the authorized keys on the server. " \
           "This can be done, by appending public key to server's authorized_keys file (~/.ssh/authorized_keys)."
    await update.message.reply_text(text=text)

async def shell(update: Update, context: CallbackContext, connection_info):
    logger.info(f'Received chat: {update.message.text}')

    chat_id = update.message.chat_id
    if chat_id not in ais:
        ais[chat_id] = Ai()

    command = ais[chat_id].turn_into_command(update.message.text)

    logger.info(f'Running command: {command}')

    if chat_id not in clients:
        clients[chat_id] = Client(connection_info, partial(send_message, chat_id = chat_id, bot = context.bot))
    
    clients[chat_id].send(command)

async def send_message(text, chat_id, bot):
    ais[chat_id].add_result(text)
    await bot.send_message(chat_id, text)