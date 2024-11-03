from vkbottle.bot import BotLabeler, Message
from config import group_api, VK_GROUP_ID
from handlers.utils import kick
from datetime import datetime
from handlers.capcha import *

import logging

from db.dataspace import ManageChats, ManageAntiSpam, ManageUsers, Users

bl = BotLabeler()
bl.vbml_ignore_case = True


@bl.message(action="chat_invite_user")
async def on_invite(message: Message):
    print(message)
    if message.action is None:
        return
    
    chat_id = message.peer_id

    if message.action.member_id == -VK_GROUP_ID:
        await message.answer(
            "👋🏻 Привет! Спасибо, что добавил меня!\n"
            "Теперь мне необходимо дать права на чтение сообщений "
            "и админку для корректной работы!"
            "После этого введите команду /start"
            )

    chat_settings = ManageChats().get_settings(chat_id)
    if chat_settings["antispam_auto"] == True:
        if ManageAntiSpam().get_user_by_id(message.action.member_id) is not None:
            await kick(message.peer_id, message.action.member_id)
            user_info = await group_api.users.get(user_ids=message.action.member_id)
            user_name = user_info[0].first_name + " " + user_info[0].last_name
            await message.answer(f"{user_name} находится в списке antispam.")
            logging.info(f"User {message.from_id} tried to invite banned user {message.action.member_id} in chat {chat_id}")
            return    

    if chat_settings["invite_link"] == True:
        if message.action.member_id < 0:
            await kick(message.peer_id, message.action.member_id)
            user_info = await group_api.users.get(user_ids=message.action.member_id)
            await message.answer(f"Бот не может быть добавлен в группу.")
            logging.info(f"User {message.from_id} tried to invite bot in chat {chat_id}")

    punished = ManageChats().get_punished(chat_id)
    for punish in punished:
        if punish == str(message.action.member_id) and punished[punish]['punishment'] == "ban" and chat_settings["emergency"] == True:
            await kick(message.peer_id, message.action.member_id)
            await kick(message.peer_id, message.from_id)
            who_added = {message.from_id: {
                        "reason": "Пригласил забаненого пользователя во время antiraid",
                        "added": str(datetime.now()),
                        "from": "antiraid system",
                        "punish_rank": 3,
                        "expired": None,
                        "punishment": "ban"
                        }}
            ManageChats().add_punished(chat_id, who_added)
            logging.info(f"User {message.from_id} tried to invite banned user {message.action.member_id} in chat {chat_id}")
        if punish == str(message.action.member_id) and punished[punish]['punishment'] == "ban":
            if datetime.strptime(punished[punish]['expired'], "%Y-%m-%d %H:%M:%S.%f") < datetime.now():
                ManageChats().remove_punished(chat_id, punish)
                break
            user_info = await group_api.users.get(user_ids=message.action.member_id)
            user_name = user_info[0].first_name + " " + user_info[0].last_name
            await kick(message.peer_id, message.action.member_id)
            # await message.answer(f"{user_name} был забанен до {punished[punish]['expired']}.\nПричина: {punished[punish]['reason']}\nВыдал бан:{punished[punish]['from']}")
            logging.info(f"User {message.from_id} tried to invite banned user {message.action.member_id} in chat {chat_id}")
            break

    user_info = await group_api.users.get(user_ids=message.action.member_id)

    if ManageUsers().get_user_by_id(message.action.member_id) is None and user_info != []:
        username = user_info[0].screen_name
        user = Users(user_id = message.action.member_id,
                username = username,
                first_name = user_info[0].first_name,
                last_name = user_info[0].last_name,
                money = 0,
                coins = 0,
                reputation = 0,
                stars = 0,
                chats = {chat_id: {"last_msg": None, "added": str(datetime.fromtimestamp(message.date)), "msg_count": 0}},
                bans = {},
                stock_list = {},
                gold = 0
                )
        ManageUsers().add_user(user)
    else:
        user = ManageUsers().get_user_by_id(message.action.member_id)
        user.chats.update({chat_id: {"last_msg": None, "added": str(datetime.fromtimestamp(message.date)), "msg_count": 0}})
        ManageUsers().update_user(user)

    if ManageChats().get_user(chat_id, message.action.member_id) is None:
        user ={message.action.member_id: {"username": user_info[0].screen_name if user_info != [] else "group",
                                      "first_name": user_info[0].first_name if user_info != [] else "group",
                                      "last_name": user_info[0].last_name if user_info != [] else "group",
                                      "last_msg": None,
                                      "added": str(datetime.fromtimestamp(message.date)),
                                      "add_id": str(message.from_id),
                                      "msg_count": 0,
                                      "msgs":[],
                                      "description": None,
                                      "nickname": None,
                                      "rewards": None,
                                      "rank": 0,
                                      "rep": 0,
                                      "bookmarks": {},
                                      "clan": None,
                                      "faction": {},
                                      "relationship_main": None,
                                      "relationship_cd": None,
                                      "inventory": {"banhammer": 0, "plusopad": 0, "minusit": 0, "anon": 0},
                                      "inventory_view": False,
                                      "active_effects": {},
                                      "married_with": None,
                                      "rep_given": 0,
                                      "capcha": False}}

        ManageChats().add_user(chat_id, user)

    user_capcha = ManageChats().get_user(chat_id, message.action.member_id)

    if user_capcha[list(user_capcha.keys())[0]]["capcha"] == False:
        await message.answer(f"{user_capcha[list(user_capcha.keys())[0]]['first_name']} {user_capcha[list(user_capcha.keys())[0]]['last_name']} напишите в личные сообщения боту 'капча' и пройдите её для получения возможности отправлять сообщения в группу")
        await capcha_verify(user_capcha, message.peer_id)
        logging.info(f"User {message.from_id} tried to add user {message.action.member_id} in chat {chat_id}")
        return     

    if chat_settings["greeting_msg"] != "":
        await message.answer(chat_settings["greeting_msg"])
        logging.info(f"User {message.from_id} added user {message.action.member_id} in chat {chat_id}")
