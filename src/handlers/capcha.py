from vkbottle.bot import BotLabeler, Message, MessageEvent
from vkbottle import Keyboard, Text
from config import group_api, VK_GROUP_ID
from db.dataspace import ManageChats, Users, ManageUsers
from datetime import datetime, timedelta
from handlers.utils import kick
import random

bl = BotLabeler()
bl.vbml_ignore_case = True

check_capcha = []
capcha_items ={
    "Единорог":"🦄",
    "Пицца":"🍕",
    "Печенье":"🍪",
    "Мяч":"⚽",
    "Пазл":"🧩",
    "Игральные кости":"🎲",
    "Машина":"🚗",
    "Молоток":"🔨",
    "Таблетка":"💊",
    "Замок":"🔒",
    "Сыр":"🧀",
    "Морковь":"🥕",
    "Яблоко":"🍎",
    "Баклажан":"🍆",
    "Банан":"🍌",
    "Багет":"🥖",
    "Звезда":"⭐",
    "Призрак":"👻",
    "Клоун":"🤡",
    "Робот":"🤖"
}



async def capcha_verify(user, peer_id):
    global check_capcha
    random_items = []
    items = list(capcha_items.items())
    for i in range(6):
        r_item = random.choice(items)
        random_items.append(r_item)
            
    item = random.choice(random_items)

    check_capcha.append([user, peer_id, item, random_items, datetime.now() + timedelta(minutes=5)])


@bl.private_message(action="message_new")
async def capcha(message: Message):
    global check_capcha
    if message["text"] == "капча":
        for user, peer_id, item, items, time in check_capcha:
            print(user, user.keys(), message["from_id"], user.keys() == str(message["from_id"]))
            if list(user.keys())[0] == str(message["from_id"]):
                keyboard = (Keyboard(one_time=True, inline=False))
                for i in range(6):
                    if i == 3:
                        keyboard.row()
                    keyboard.add(Text(f"{items[i][1]}"))
                msg = f"Для присоединения к группе нажмите на {item[0]}"
                await group_api.messages.send(peer_id=message["from_id"], message=msg, keyboard=keyboard, random_id = 0)
                return

    for user, peer_id, item, items, time in check_capcha:
        if datetime.now() > time:
            check_capcha.remove([user, peer_id, item, items, time])
            kick(peer_id, list(user.keys())[0])
            return
        if list(user.keys())[0] == str(message["from_id"]):
            if message["text"] == item[1]:
                await group_api.messages.send(peer_id=message["from_id"], message="Теперь вы можете присоединиться к каналу", random_id = 0)
                user[list(user.keys())[0]]["capcha"] = True
                ManageChats().update_user(peer_id, user)
                check_capcha.remove([user, peer_id, item, items, time])
                return
            if message["text"] != item[1]:
                await group_api.messages.send(peer_id=message["from_id"], message="Неправильно", random_id = 0)
                check_capcha.remove([user, peer_id, item, items, time])
                kick(peer_id, list(user.keys())[0])
                print(item, item[1], message["text"], items)
                return


