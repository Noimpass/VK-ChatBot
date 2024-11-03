import datetime

from db.db import Base
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy_json import mutable_json_type
from sqlalchemy import PickleType

class Chats(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(BigInteger)
    owner = Column(Integer)
    users = Column(mutable_json_type(dbtype=JSONB, nested=True))
    staff = Column(mutable_json_type(dbtype=JSONB, nested=True))
    message_count = Column(Integer)
    rp_command = Column(mutable_json_type(dbtype=JSONB, nested=True))
    punished = Column(mutable_json_type(dbtype=JSONB, nested=True))
    info = Column(String)
    bookmarks = Column(mutable_json_type(dbtype=JSONB, nested=True))
    clans = Column(mutable_json_type(dbtype=JSONB, nested=True))
    factions = Column(mutable_json_type(dbtype=JSONB, nested=True))
    commands = Column(mutable_json_type(dbtype=JSONB, nested=True))
    settings = Column(mutable_json_type(dbtype=JSONB, nested=True))
    relationships = Column(mutable_json_type(dbtype=JSONB, nested=True))
    coins = Column(BigInteger)
    money_group = Column(BigInteger)

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    money = Column(Float)
    coins = Column(Integer)
    reputation = Column(Integer)
    stars = Column(Integer)
    chats = Column(mutable_json_type(dbtype=JSONB, nested=True))
    bans = Column(mutable_json_type(dbtype=JSONB, nested=True))
    stock_list = Column(mutable_json_type(dbtype=JSONB, nested=True))
    gold = Column(Integer)

class Antispam(Base):
    __tablename__ = "antispam_list"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger)

class StockMarket(Base):
    __tablename__ = "stockmarket_list"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger)
    price = Column(Float)
    count = Column(Integer)
    type = Column(String)

class User_info(dict):
    username: str
    first_name: str
    last_name: str
    last_msg: datetime.datetime
    added: datetime.datetime
    add_id: int
    msg_count: int
    msgs: list
    description: str
    nickname: str
    rewards: list
    rank: str
    rep: int
    bookmarks: list
    clan: int
    faction: list
    relationship_main: int
    relationship_cd: int
    inventory: dict
    inventory_view: bool
    active_effects: dict
    married_with: int
    rep_given: int
    capcha: bool

class Staff(dict):
    id: int
    name: str
    role: int
    added: datetime.datetime
    add_id: int

class Punished(dict):
    id: int
    reason: str
    added: datetime.datetime
    add_id: int
    punish_rank: int

class Clans(dict):
    id: int
    name: str
    members: list

class Factions(dict):
    id: int
    name: str
    members: list

class Commands(dict):
    id: int
    name: str
    description: str
    active: bool

class Bookmarks(dict):
    bookmark_id: int
    name: str
    date: datetime.datetime
    message_id: int
    from_id: int

class ChatSettings(dict):
    representive_group: str
    rules: str
    greeting_msg: str
    invite_count: int
    antiraid_count: int
    warn_count: int
    warn_time: datetime.timedelta
    emergency: bool
    chat_link: bool
    site_link: bool
    group_link: bool
    invite_link: bool
    chat_grid: list
    auto_kick_of_leaves: bool
    roles: dict
    domen: str
    bookmarks_need_rep: int
    antispam_auto: bool
    stock: bool
    items_price: dict
    plusopad_count: int
    minusit_count: int
    rep_give_count: int

class Relationships(dict):
    user = Column(BigInteger)
    with_user = Column(BigInteger)
    status = Column(Integer)
    hp = Column(Integer)
    start_date = Column(Integer)
    history = Column(mutable_json_type(dbtype=JSONB, nested=True))

class Relationships(dict):
    date: datetime.datetime
    action: str
    from_: int

