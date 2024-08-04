import argparse
import configparser
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import new_key, start, shell, check_user
from functools import partial

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_path',
                        help='Path to the bot config',
                        default='config',
                        nargs='?',
                        type=str)

    config_path = parser.parse_args().config_path

    with open(config_path, 'r') as f:
        config_string = '[dummy_section]\n' + f.read()  # configparser requires to have sections
    config = configparser.ConfigParser()
    config.read_string(config_string)

    cs = config['dummy_section']  # config section
    to_return = [
        cs['tg_username'],
        cs['tg_bot_token'],
        cs.get('username', None),
        cs['hostname'],
        cs.get('port', 22),
        cs.get('path_to_keys', './')
    ]
    return to_return


if __name__ == '__main__':
    tg_username, tg_secret, username, hostname, port, path_to_keys = parse_args()
    connection_info = (username, hostname, port, path_to_keys)
    log.info('Connection info: %s', connection_info)

    application: Application = Application.builder().token(tg_secret).build()

    application.add_handler(MessageHandler(filters.ALL, partial(check_user, username=tg_username)), group=-1)

    application.add_handler(CommandHandler('start', start))

    application.add_handler(CommandHandler('newkey', partial(new_key, path_to_keys=path_to_keys)))

    application.add_handler(MessageHandler(filters.TEXT, partial(shell, connection_info=connection_info)))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
