import os


DB_CONN_STRING = os.getenv('DB_CONN_STRING')

BOT_TOKEN = os.getenv('BOT_TOKEN')

DATABASE = os.getenv('DATABASE')

RSS_MEMBER = os.getenv('RSS_MEMBER')
RSS_KEY = os.getenv('RSS_KEY')

MAIN_FORUM_NAME = os.getenv('MAIN_FORUM_NAME')
MAIN_FORUM_PASS = os.getenv('MAIN_FORUM_PASS')

JUDGE_ROLE = os.getenv('JUDGE_ROLE')
ADMIN_COMMANDS_CHANNEL = os.getenv('ADMIN_COMMANDS_CHANNEL')

GUILD_ID = int(os.getenv('GUILD_ID'))

DISABLED_COGS = []
