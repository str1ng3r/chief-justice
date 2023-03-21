import os

from dotenv import load_dotenv

APP_ENV = os.getenv('APP_ENV')

if APP_ENV != 'docker':
    load_dotenv()


DB_CONN_STRING = os.getenv('DB_CONN_STRING')

BOT_TOKEN = os.getenv('BOT_TOKEN')

DATABASE = os.getenv('DATABASE')

MAIN_FORUM_NAME = os.getenv('MAIN_FORUM_NAME')
MAIN_FORUM_PASS = os.getenv('MAIN_FORUM_PASS')

GUILD_ID = os.getenv('GUILD_ID')

DISABLED_COGS = ['cases', 'renewals', 'reminders']
