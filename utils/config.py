import os
import configparser
import shutil


class Config:
    def __init__(self):
        self.config_file = 'config/config.ini'

        if not os.path.isfile(self.config_file):
            print('ERROR: YOU HAVE NOT CONFIGURED THE BOT. EDIT THE config.ini file in the config folder to run this bot.')
            os._exit(1)


        config = configparser.ConfigParser(interpolation=None)
        config.read(self.config_file, encoding="utf-8")


        self.token = config.get('Bot', 'Token', fallback=None)
        self.heroku_api_key = config.get('Heroku', 'heroku_api_key', fallback=None)
        self.heroku_app_name = config.get('Heroku', 'heroku_app_name', fallback=None)
        self.owner_id = config.get('Credentials', 'owner_id', fallback=None)
        self.owner_user_name = config.get('Credentials', 'owner_user_name', fallback=None)
        self.command_prefix = config.get('Bot', 'command_prefix', fallback='!')
        self.success = ':white_check_mark:'
        self.fail = ':no_entry_sign:'
        self.mute_role_id = config.get('Credentials', 'mute_role_id', fallback=None)
        self.default_server_role_id = config.get('Credentials', 'default_server_role_id', fallback=None)
        self.mod_role_ids = config.get('Credentials', 'mod_role_ids', fallback=None).split(', ')
        self.invite = config.get('Bot', 'invite', fallback=None)

        if not self.token:
            print('ERROR: THE BOT HAS NOT BEEN SUPPLIED WITH A BOT TOKEN.')
            os._exit(1)





