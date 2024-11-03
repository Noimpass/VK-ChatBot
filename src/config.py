from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from vkbottle import API

load_dotenv()

class Settings(BaseSettings):
    DEBUG: bool = False
    BOT_TOKEN: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    TDB_HOST: str
    DB_PORT: str
    TDB_PORT: str
    DATA_STORAGE: str



DEFAULT_COMMANDS_RANK = {
    "kick": 2,
    "ban": 3,
    "warn": 1,
    "mute": 1,
    "ping": 0,
    "rank_change": 5,
    "custom_rp": 1,    
    "amnistia": 5,
    "ban_list": 3,
}

DEFAULT_RANK_NAME = {
    0: "Участник",
    1: "Младший модератор",
    2: "Старший модератор",
    3: "Младший админ",
    4: "Старший админ",
    5: "Создатель"
}

DEFAULT_ITEM_PRICE = {
    "banhammer":1000,
    "plusopad":1000,
    "minusit":1000,
    "anon":100,
}

DEFAULT_CHAT_SETTINGS = {
    "represented_group": None,
    "rules": "",
    "greeting_msg": "",
    "invite_count": 3,
    "antiraid_count": 0,
    "warn_count": 3,
    "emergency": False,
    "chat_link": False,
    "site_link": False,
    "group_link": False,
    "invite_link": False,
    "chat_grid": None,
    "roles": DEFAULT_RANK_NAME,
    "domain": None,
    "bookmarks_need_rep": 10,
    "antispam_auto": False,
    "stock": False,
    "item_price": DEFAULT_ITEM_PRICE
}

DEFAULT_INVENTORY = {
    "banhammer": 0,
    "plusopad": 0,
    "minusit": 0,
    "coin": 0,
    "anon": 0
}
DEFAULT_CHAT = {
    "chat_id": None,
    "owner": None,
    "users": None,
    "staff": None,
    "message_count": 0,
    "rp_command": None,
    "punished": None,
    "info": "Нет описания беседы",
    "bookmarks": None,
    "clans": None,
    "factions": None,
    "commands": DEFAULT_COMMANDS_RANK,
    "settings": DEFAULT_CHAT_SETTINGS,
    "relationships": None,
    "money_group": 0
}

DEFAULT_SELF_USER_DATA = {
    "user_id": None,
    "username": None,
    "first_name": None,
    "last_name": None,
    "money": 0,
    "reputation": 0,
    "reputation_self": 0,
    "chats": None,
    "inventory": DEFAULT_INVENTORY,
    "inventory_view": False,
    "banned": None,
    "stock_list": None
}

settings = Settings()
group_api = API(token=settings.BOT_TOKEN)
VK_GROUP_ID = 227601122