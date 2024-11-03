import random
import re
import time
from datetime import datetime, timedelta
from config import DEFAULT_CHAT_SETTINGS, DEFAULT_COMMANDS_RANK, VK_GROUP_ID, group_api

import aiohttp
import msgspec
import logging
from vkbottle import API, VKAPIError
from vkbottle_types.objects import PhotosPhotoSizes
from db.dataspace import ManageChats, Chats, ManageUsers, Users


async def kick(chat_id, user_id):
    if chat_id > 2000000000:
            chat_id -= 2000000000
    try:
        await group_api.messages.remove_chat_user(chat_id=chat_id, user_id=user_id)
    except VKAPIError:
        await group_api.messages.send(chat_id=chat_id, message=f"Не удалось кикнуть {user_id}", random_id=0)
        
async def get_chat_members(group_api: API, chat_id: int):
    try:
        logging.info(f"Getting chat {chat_id} members")
        response = await group_api.messages.get_conversation_members(chat_id)
        logging.info(f"Got chat {chat_id} members")
        members = [i for i in response.items]
        admins = [i for i in response.items if i.is_admin]
        owner = [i.member_id for i in response.items if i.is_owner]
        profiles = [i for i in response.profiles]
        return [tuple(members), tuple(admins), tuple(owner), tuple(profiles)]
    except:
        return None
    
async def add_chat(chat_id, chat_members: list[tuple, tuple, tuple]):
    if ManageChats().get_chat(chat_id):
        logging.info(f"Chat {chat_id} already exists in database")
        return True
    logging.info(f"Adding chat {chat_id} to database")
    members = chat_members[0]
    admins = chat_members[1]
    owner = chat_members[2]
    profiles = chat_members[3]
    user_info = {}
    admin_info = {}
    for member in members:
        print(member)
        member_info = await group_api.users.get(user_ids=member.member_id, fields="screen_name,first_name,last_name")
        user_info.update({member.member_id: {"username": member_info[0].screen_name if member_info != [] else "group",
                                      "first_name": member_info[0].first_name if member_info != [] else "group",
                                      "last_name": member_info[0].last_name if member_info != [] else "group",
                                      "last_msg": None,
                                      "added": str(datetime.fromtimestamp(member.join_date)),
                                      "add_id": str(member.invited_by),
                                      "msg_count": 0,
                                      "msgs":[],
                                      "description": None,
                                      "nickname": None,
                                      "rewards": None,
                                      "rank": 0,
                                      "rep": 0,
                                      "bookmarks": {},
                                      "clan": None,
                                      "faction": [],
                                      "relationship_main": None,
                                      "relationship_cd": None,
                                      "inventory": {"banhammer": 0, "plusopad": 0, "minusit": 0, "anon": 0},
                                      "inventory_view": False,
                                      "active_effects": {},
                                      "married_with": None,
                                      "rep_given": 0,
                                      "capcha": True,}})
        if ManageUsers().get_user_by_id(member.member_id) is None and member_info != []:
            user = Users(user_id = member.member_id,
                username = member_info[0].screen_name,
                first_name = member_info[0].first_name,
                last_name = member_info[0].last_name,
                money = 0,
                coins = 0,
                reputation = 0,
                stars= 0,
                chats = {chat_id: {"last_msg": None, "added": str(datetime.fromtimestamp(member.join_date)), "msg_count": 0}},
                bans = {},
                stock_list = {}, gold = 0
                )
            ManageUsers().add_user(user)
        elif member_info != []:
            user = ManageUsers().get_user_by_id(member.member_id)
            user.chats.update({chat_id: {"last_msg": None, "added": str(datetime.fromtimestamp(member.join_date)), "msg_count": 0}})
            ManageUsers().update_user(user)
    
    for admin in admins:
        member_info = await group_api.users.get(user_ids=admin.member_id, fields="screen_name,first_name,last_name")
        if admin.member_id == owner[0]:
            admin_info.update({admin.member_id: {
                               "name": f"{member_info[0].first_name} {member_info[0].last_name}" if member_info != [] else "group",
                               "role": 5,
                               "added": str(datetime.now()),
                               "add_id": 0}})
            continue
        admin_info.update({admin.member_id: {
                           "name": f"{member_info[0].first_name} {member_info[0].last_name}" if member_info != [] else "group",
                           "role": 1,
                           "added": str(datetime.now()),
                           "add_id": 0}})
        
    settings = DEFAULT_CHAT_SETTINGS
    settings["domain"] = chat_id - 2000000000 
    
    ManageChats().add_chat(Chats(chat_id=chat_id,
                                 owner=owner[0],
                                 users=user_info,
                                 staff=admin_info,
                                 message_count=0,
                                 rp_command=None,
                                 punished={},
                                 info="",
                                 bookmarks={},
                                 clans={},
                                 factions={},
                                 commands=DEFAULT_COMMANDS_RANK,
                                 settings=DEFAULT_CHAT_SETTINGS,
                                 relationships={},
                                 coins = 0,
                                 money_group=0
                                 ))

async def promote_staff(message, user):
    settings = ManageChats().get_settings(message.peer_id)
    settings = settings["roles"]
    chat_id = message.peer_id
    add_id = message.from_id
    user = user.split("|")[0][3:] 
    user_id = await group_api.users.get(user_ids=user)
    user_id = str(user_id[0].id)
    logging.info(f"Promoting {user_id} in chat {chat_id}")
    staff = ManageChats().get_staff(message.peer_id)
    print(staff.keys(), user_id, user, message.peer_id, user_id in staff.keys())
    try:
        if int(staff[user_id]['role']) >= 4:
            return "Уже назначена максимальная роль"
    except:
        pass
    if user_id in staff.keys():
        promoted = {user_id: {
              "name": staff[user_id]['name'],
              "role": int(staff[user_id]["role"]) + 1,
              "added": str(datetime.now()),
              "add_id": add_id}}
        ManageChats().update_staff(message.peer_id, user_id, promoted)
        staff = ManageChats().get_staff(message.peer_id)
        return f"Повышен до {settings[str(staff[user_id]['role'])]}"


    promoted = {user_id:{
              "name": staff[user_id]['name'],
              "role": 1,
              "added": str(datetime.now()),
              "add_id": add_id}}
    
    ManageChats().add_staff(chat_id, promoted)
    staff = ManageChats().get_staff(message.peer_id)
    return f"Повышен до {settings[str(staff[user_id]['role'])]}"

async def demote_staff(message, user_link):
    chat_id = message.peer_id
    settings = ManageChats().get_settings(chat_id)
    settings = settings["roles"]
    add_id = message.from_id
    user = user_link.split("|")[0][3:] 
    user_id = await group_api.users.get(user_ids=user)
    user_id = str(user_id[0].id)
    logging.info(f"Demoting {user_id} in chat {chat_id}")
    staff = ManageChats().get_staff(chat_id)

    try:
        if int(staff[user_id]['role']) <= 1:
            return "Уже назначена минимальная роль, для снятия должности используйте команду 'исключить модера'"
    except:
        return "Пользователь не является модератором"
    
    if user_id in staff.keys():
        promoted = {user_id: {
              "name": staff[user_id]['name'],
              "role": int(staff[user_id]["role"]) - 1,
              "added": str(datetime.now()),
              "add_id": add_id}}
        ManageChats().update_staff(chat_id, user_id, promoted)

    staff = ManageChats().get_staff(chat_id)
    return "Понижен до " + settings[str(staff[user_id]['role'])]

async def remove_staff(message, user):
    user = user.split("|")[0][3:] 
    group_id = message.peer_id
    settings = ManageChats().get_settings(group_id)
    settings = settings["roles"]
    staff = ManageChats().get_staff(group_id)
    user_id = await group_api.users.get(user_ids=user)
    print(user_id)
    user_id = str(user_id[0].id)
    logging.info(f"Removing staff {user_id} in chat {group_id}")
    ManageChats().remove_staff(group_id, user_id)
    return f"Был разжалован с должности {settings[str(staff[user_id]['role'])]}"

async def get_admins(message):
    staff_list = []
    group_id = message.peer_id
    settings = ManageChats().get_settings(group_id)
    settings = settings["roles"]
    chat_id = message.peer_id
    staff = ManageChats().get_staff(chat_id)
    logging.info(f"Get admins in chat {group_id}")
    for user in staff:
        staff_list.append([staff[user]['name'], settings[str(staff[user]['role'])], user])
    return staff_list

#========================Warn========================

async def warn_user(message, user_link, reason):
    chat_id = message.peer_id
    settings = ManageChats().get_settings(chat_id)
    settings = settings["roles"]
    if message.reply_message:
        user = message.reply_message.from_id
    else:
        user = user_link.split("|")[0][3:] 
    add_id = str(message.from_id)
    user_id = await group_api.users.get(user_ids=user)
    user_name = str(user_id[0].first_name) + " " + str(user_id[0].last_name)
    user_id = str(user_id[0].id)
    logging.info(f"Warned {user_id} in chat {chat_id}")
    punished = ManageChats().get_punished(chat_id)
    staff = ManageChats().get_staff(chat_id)
    warn_count = 1

    for punish in punished:
        print(punish)
        if list(punish.keys())[0] == user_id and punish[list(punish.keys())[0]]['punishment'] == "warn":
            warn_count += 1

    if warn_count >= 3:
        if chat_id > 2000000000:
            chat_id -= 2000000000
        await group_api.messages.remove_chat_user(chat_id=chat_id, user_id=user_id)
        return f"[id{user_id}|{user_name}] получил больше 3 варнов и был забанен.\nОт модератора [id{add_id}|{staff[add_id]['name']}]"
        
    punish = {user_id:{
                "reason": reason,
                "added": str(datetime.now()),
                "from": add_id,
                "punish_rank": str(staff[add_id]['role']),
                "expired": str(datetime.now() + timedelta(days=1)),
                "punishment": "warn"
                }}

    ManageChats().add_punished(chat_id, punish)
    return f"[id{user_id}|{user_name}] получил предупреждение ({warn_count}/3).\nОт модератора [id{add_id}|{staff[add_id]['name']}]"
        
async def remove_warnings_user(message, user_link, count):
    chat_id = message.peer_id
    settings = ManageChats().get_settings(chat_id)
    settings = settings["roles"]
    if message.reply_message:
        user = message.reply_message.from_id
    else:
        user = user_link.split("|")[0][3:] 
    add_id = str(message.from_id)
    user_id = await group_api.users.get(user_ids=user)
    user_name = str(user_id[0].first_name) + " " + str(user_id[0].last_name)
    user_id = str(user_id[0].id)
    punished = ManageChats().get_punished(chat_id)
    staff = ManageChats().get_staff(chat_id)
    logging.info(f"Removed warnings from {user_id} in chat {chat_id}")

    lenght = ManageChats().delete_warn(chat_id, user_id, count)
    return f"С [id{user_id}|{user_name}] было удалено {lenght} предупреждений.\nОт модератора [id{add_id}|{staff[add_id]['name']}]"

async def get_warn(message, user_link):
    chat_id = message.peer_id
    settings = ManageChats().get_settings(chat_id)
    settings = settings["roles"]
    staff = ManageChats().get_staff(chat_id)
    if message.reply_message:
        user = message.reply_message.from_id
    else:
        user = user_link.split("|")[0][3:] 
    user_id = await group_api.users.get(user_ids=user)
    user_id = str(user_id[0].id)
    punished = ManageChats().get_punished(chat_id)
    logging.info(f"Get warnings from {user_id} in chat {chat_id}")
    warn = []
    for punish in punished:
        if punish == user_id and punished[punish]['punishment'] == "warn":
            warn.append([punished[punish]["added"], punished[punish]["expired"], punished[punish]['reason']])

    return warn

async def mute_user_func(message, user_link, time):
    chat_id = message.peer_id
    settings = ManageChats().get_settings(chat_id)
    settings = settings["roles"]
    if message.reply_message:
        user = message.reply_message.from_id
    else:
        user = user_link.split("|")[0][3:] 
    add_id = str(message.from_id)
    user_id = await group_api.users.get(user_ids=user)
    user_name = str(user_id[0].first_name) + " " + str(user_id[0].last_name)
    user_id = str(user_id[0].id)
    logging.info(f"Muted {user_id} in chat {chat_id}")
    staff = ManageChats().get_staff(chat_id)
    punish = {user_id:{
                "reason": "mute",
                "added": str(datetime.now()),
                "from": add_id,
                "punish_rank": str(staff[add_id]['role']),
                "expired": str(datetime.now() + timedelta(hours=int(time))),
                "punishment": "mute"
                }}

    ManageChats().add_punished(chat_id, punish)
    return f"{user_name} получил мут ({time} час).\nОт модератора {staff[add_id]['name']}"

#=========================Команды банов=========================

async def get_banlist(message):
    chat_id = message.peer_id
    settings = ManageChats().get_settings(chat_id)
    settings = settings["roles"]
    banlist = ManageChats().get_punished(chat_id)
    resp = []
    logging.info(f"Get banlist in chat {chat_id}")
    for ban in banlist:
        if banlist[ban]['punishment'] == "ban":
            user = await group_api.users.get(user_ids=ban)
            user_name = user[0].first_name + " " + user[0].last_name
            resp.append([user_name, banlist[ban]["added"].split(".")[0], banlist[ban]["expired"].split(".")[0], banlist[ban]['reason'], banlist[ban]["from"], banlist[ban]["punish_rank"]])

    return resp
        

async def get_amnistia(message):
    chat_id = message.peer_id
    owner = ManageChats().get_chat_owner(chat_id)
    logging.info(f"Remove all punished in chat {chat_id}")
    if message.from_id == owner:
        ManageChats().delete_all_punished(chat_id)
        return "Все баны сняты"
    
async def remove_power(message):
    chat_id = message.peer_id
    user_id = str(message.from_id)
    logging.info(f"Staff {user_id} removed his power in chat {chat_id}")
    ManageChats().remove_staff(chat_id, user_id)
    return "Все полномочия были сняты"
    
async def resotre_owner_rank(message):
    chat_id = message.peer_id
    user_id = str(message.from_id)
    owner = ManageChats().get_chat_owner(chat_id)
    member_info = await group_api.users.get(user_ids=owner)
    member_id = str(member_info[0].id)
    admin_info = {member_id: {
                    "name": f"{member_info[0].first_name} {member_info[0].last_name}" if member_info != [] else "group",
                    "role": 5,
                    "added": str(datetime.now()),
                    "add_id": 0}}
    logging.info(f"Staff {user_id} restored his power in chat {chat_id}")
    ManageChats().add_staff(chat_id, admin_info)
    return "Все полномочия были восстановлены"

async def ban_user_func(message, user_link, reason, time):
    chat_id = message.peer_id
    add_id = str(message.from_id)
    staff = ManageChats().get_staff(chat_id)
    user = user_link.split("|")[0][3:] 
    user_info = await group_api.users.get(user_ids=user)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    user_id = str(user_info[0].id)
    if time == None:
        time = 7
    punish = {user_id:{
            "reason": reason,
            "added": str(datetime.now()),
            "from": add_id,
            "punish_rank": str(staff[add_id]['role']),
            "expired": str(datetime.now() + timedelta(days=int(time))),
            "punishment": "ban"
            }}
    ManageChats().add_punished(chat_id, punish)
    await kick(chat_id, user_id)
    logging.info(f"Banned {user_id} in chat {chat_id}")
    return f"{user_name} был забанен на {time} дней.\nПричина: {reason}\nОт модератора: {staff[add_id]['name']}"

async def ban_user_permanent_func(message, user_link, reason, time):
    chat_id = message.peer_id
    add_id = str(message.from_id)
    staff = ManageChats().get_staff(chat_id)
    user = user_link.split("|")[0][3:] 
    user_info = await group_api.users.get(user_ids=user)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    user_id = str(user_info[0].id)
    if time == None:
        time = 7
    punish = {user_id:{
            "reason": reason,
            "added": str(datetime.now()),
            "from": add_id,
            "punish_rank": str(staff[add_id]['role']),
            "expired": None,
            "punishment": "ban"
            }}
    ManageChats().add_punished(chat_id, punish)
    await kick(chat_id, user_id)
    logging.info(f"Permanently banned {user_id} in chat {chat_id}")
    return f"{user_name} был забанен навсегда.\nПричина: {reason}\nОт модератора: {staff[add_id]['name']}"

async def banhammer_ban_func(message, user_link):
    chat_id = message.peer_id
    add_id = str(message.from_id)
    user = user_link.split("|")[0][3:] 
    user_info = await group_api.users.get(user_ids=user)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    user_id = str(user_info[0].id)
    time = 1 
    punish = {user_id:{
            "reason": "банхаммер",
            "added": str(datetime.now()),
            "from": add_id,
            "punish_rank": str(1),
            "expired": str(datetime.now() + timedelta(days=int(time))),
            "punishment": "ban"
            }}
    ManageChats().add_punished(chat_id, punish)
    await kick(chat_id, user_id)
    logging.info(f"Banhammer {user_id} in chat {chat_id}")
    return f"{user_name} был забанен на {time} день.\nПричина: Банхаммер"

async def ban_user_minutes_duel_func(chat_id, user, staff, time):
    staff_info = await group_api.users.get(user_ids=staff)
    staff_name = staff_info[0].first_name + " " + staff_info[0].last_name
    user_info = await group_api.users.get(user_ids=user)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    user_id = str(user_info[0].id)
    if time == None:
        time = 10
    punish = {user_id:{
            "reason": "Проиграл в дуэли",
            "added": str(datetime.now()),
            "from": staff_name,
            "punish_rank": 1,
            "expired": str(datetime.now() + timedelta(minutes=int(time))),
            "punishment": "ban"
            }}
    await kick(chat_id, user_id)
    ManageChats().add_punished(chat_id, punish)
    logging.info(f"Duel ban {user_id} in chat {chat_id}") 
    return f"{user_name} был забанен на {time} минут.\nПричина: Проиграл в дуэли"

async def ban_user_hours_duel_func(chat_id, user, staff, time):
    staff_info = await group_api.users.get(user_ids=staff)
    staff_name = staff_info[0].first_name + " " + staff_info[0].last_name
    user_info = await group_api.users.get(user_ids=user)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    user_id = str(user_info[0].id)
    if time == None:
        time = 10
    punish = {user_id:{
            "reason": "Проиграл в дуэли",
            "added": str(datetime.now()),
            "from": staff_name,
            "punish_rank": 1,
            "expired": str(datetime.now() + timedelta(hours=int(time))),
            "punishment": "ban"
            }}
    await kick(chat_id, user_id)
    ManageChats().add_punished(chat_id, punish)
    logging.info(f"Duel ban {user_id} in chat {chat_id}")
    return f"{user_name} был забанен на {time} часов.\nПричина: Проиграл в дуэли"

async def ban_user_days_duel_func(chat_id, user, staff, time):
    staff_info = await group_api.users.get(user_ids=staff)
    staff_name = staff_info[0].first_name + " " + staff_info[0].last_name
    user_info = await group_api.users.get(user_ids=user)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    user_id = str(user_info[0].id)
    if time == None:
        time = 10
    punish = {user_id:{
            "reason": "Проиграл в дуэли",
            "added": str(datetime.now()),
            "from": staff_name,
            "punish_rank": 1,
            "expired": str(datetime.now() + timedelta(days=int(time))),
            "punishment": "ban"
            }}
    await kick(chat_id, user_id)
    ManageChats().add_punished(chat_id, punish)
    logging.info(f"Duel ban {user_id} in chat {chat_id}")
    return f"{user_name} был забанен на {time} дней.\nПричина: Проиграл в дуэли"

async def ban_user_permanent_duel_func(chat_id, user, staff): 
    staff_info = await group_api.users.get(user_ids=staff)
    staff_name = staff_info[0].first_name + " " + staff_info[0].last_name
    user_info = await group_api.users.get(user_ids=user)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    user_id = str(user_info[0].id)
    punish = {user_id:{
            "reason": "Проиграл в дуэли",
            "added": str(datetime.now()),
            "from": staff_name,
            "punish_rank": 1,
            "expired": None,
            "punishment": "ban"
            }}
    await kick(chat_id, user_id)
    ManageChats().add_punished(chat_id, punish)
    logging.info(f"Duel ban {user_id} in chat {chat_id}")
    return f"{user_name} был забанен навсегда.\nПричина: Проиграл в дуэли"

async def unban_user_func(message, user_link):
    chat_id = message.peer_id
    user = user_link.split("|")[0][3:] 
    user_id = await group_api.users.get(user_ids=user)
    user_id = str(user_id[0].id)
    ManageChats().remove_punished(chat_id, user_id)
    logging.info(f"Unban {user_id} in chat {chat_id}")
    return "Пользователь разбанен"

async def get_reason_func(message, user_link):
    chat_id = message.peer_id
    user = user_link.split("|")[0][3:]
    user_info = await group_api.users.get(user_ids=user)
    user_id = str(user_info[0].id)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    punished = ManageChats().get_punished(chat_id)
    logging.info(f"Get reason {user_id} in chat {chat_id}")
    for punish in punished:
        if punish == user_id and punished[punish]['punishment'] == "ban":
            return "Причина: " + punished[punish]['reason']
        
async def kick_user_func(message, user_link):
    chat_id = message.peer_id
    if message.reply_message:
        user = message.reply_message.from_id
    else:
        user = user_link.split("|")[0][3:] 
    user_info = await group_api.users.get(user_ids=user)
    user_id = str(user_info[0].id)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    staff_info = await group_api.users.get(user_ids=message.from_id)
    staff_name = staff_info[0].first_name + " " + staff_info[0].last_name
    await kick(chat_id, user_id)
    logging.info(f"Kick {user_id} in chat {chat_id}")
    return f"{staff_name} кикнул пользователя {user_name} из чата"

#============================Чистка беседы=============================

async def kick_newcomers_func(message, time):
    chat_id = message.peer_id
    users = ManageChats().get_users(chat_id)
    for user in users:
        print(users[user]["added"], datetime.now() - timedelta(hours=int(time)))
        if datetime.strptime(users[user]["added"], "%Y-%m-%d %H:%M:%S") > datetime.now() - timedelta(hours=int(time)):
            await kick(chat_id, user)
    logging.info(f"Kick newcomers in chat {chat_id}")
    return "Новые пользователи были кикнуты"

async def kick_dogs_func(message):
    chat_id = message.peer_id
    users = ManageChats().get_users(chat_id)
    logging.info(f"Kick dogs in chat {chat_id}")
    for user in users:
        user_info = await group_api.users.get(user_ids=user)
        if user_info[0].deactivated:
            await kick(chat_id, user)

async def kick_by_user_func(message, user_link):
    chat_id = message.peer_id
    if message.reply_message:
        add_id = message.reply_message.from_id
    else:
        add_id = user_link.split("|")[0][3:] 
    users = ManageChats().get_users(chat_id)
    for user in users:
        if users[user]["add_id"] == add_id:
            await kick(chat_id, user)
    logging.info(f"Kick user if {add_id} was add_id in chat {chat_id}")

async def kick_molch_func(message, time):
    chat_id = message.peer_id
    users = ManageChats().get_users(chat_id)
    for user in users:
        if datetime.strptime(users[user]["added"], "%Y-%m-%d %H:%M:%S") > datetime.now() - timedelta(days=int(time)) and users[user]["last_msg"] == None:
            await kick(chat_id, user)

    logging.info(f"Kick silence in chat {chat_id}")
    return "Молчуны были кикнуты"

async def kick_by_messages_func(message, count, time):
    chat_id = message.peer_id
    if time == None:
        time = 7
    users = ManageChats().get_users(chat_id)
    for user in users:
        if users[user]["msg_count"] < count:
            await kick(chat_id, user)
    logging.info(f"Kick by messages in chat {chat_id}")

#============================Темы модераторов=============================

async def moder_name_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    logging.info(f"Get moder name in chat {chat_id}")
    return chat["roles"]

async def set_moder_name_func(message, roles):
    chat_id = message.peer_id
    text = message.text.split("\n")[1]
    if text == None:
        return "Поле не может быть пустым"
    text = text.split(" ")

    change = {"0": text[0].split("=")[1],
              "1": text[1].split("=")[1],
              "2": text[2].split("=")[1],
              "3": text[3].split("=")[1],
              "4": text[4].split("=")[1],
              "5": text[5].split("=")[1]}
    chat = ManageChats().get_settings(chat_id)
    chat["roles"] = change
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set moder name in chat {chat_id}")
    return "Названия модераторов изменены"

#============================Настройка беседы=============================

async def change_link_func(message, link):
    chat_id = message.peer_id
    try:
        await group_api.messages.get_invite_link(peer_id=chat_id)
        await message.answer(f"Пригласительная ссылка чата успешно изменена на: {link}")
    except Exception as e:
        await message.answer(f"Ошибка при изменении пригласительной ссылки чата: {str(e)}")

async def get_rules_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    logging.info(f"Get rules in chat {chat_id}")
    return chat["rules"]

async def set_rules_func(message, rules):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["rules"] = rules
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set rules in chat {chat_id}")
    return "Правила изменены"

async def delete_rules_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["rules"] = ""
    ManageChats().change_settings(chat_id, chat)
    return "Правила удалены"

async def set_welcome_func(message, welcome):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["greeting_msg"] = welcome
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set welcome in chat {chat_id}")
    return "Приветствие изменено"

async def delete_welcome_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["greeting_msg"] = ""
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Delete welcome in chat {chat_id}")
    return "Приветствие удалено"

async def set_invite_count_func(message, count):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["invite_count"] = count
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set invite count in chat {chat_id}")
    return "Ограничение число одновременно добавляемых пользователей изменено"

async def set_antiraid_func(message, count):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["antiraid_count"] = count
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set antiraid count in chat {chat_id}")
    return "Ограничение количества попыток приглашений забаненного пользователя изменено"

async def set_emergency_on_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["emergency"] = True
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set emergency on in chat {chat_id}")
    return "Антирейд включен"

async def set_emergency_off_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["emergency"] = False
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set emergency off in chat {chat_id}")
    return "Антирейд выключен"

async def set_chat_filter_on_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["chat_link"] = True
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set chat filter on in chat {chat_id}")
    return "Разрешает отправлять сообщения с ссылками на беседы"

async def set_chat_filter_off_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["chat_link"] = False
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set chat filter off in chat {chat_id}")
    return "Запрещает отправлять сообщения с ссылками на беседы"

async def set_site_filter_on_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["site_link"] = True
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set site filter on in chat {chat_id}")
    return "Разрешает отправлять сообщения с ссылками на сайты"

async def set_site_filter_off_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["site_link"] = False
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set site filter off in chat {chat_id}")
    return "Запрещает отправлять сообщения с ссылками на сайты"

async def set_group_filter_on_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["group_link"] = True
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set group filter on in chat {chat_id}")
    return "Разрешает отправлять сообщения с ссылками на группы"

async def set_group_filter_off_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["group_link"] = False
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set group filter off in chat {chat_id}")
    return "Запрещает отправлять сообщения с ссылками на группы"

async def set_invite_filter_on_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["invite_link"] = True
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set invite filter on in chat {chat_id}")
    return "Разрещает приглашать сообщества в группу"

async def set_invite_filter_off_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_settings(chat_id)
    chat["invite_link"] = False
    ManageChats().change_settings(chat_id, chat)
    logging.info(f"Set invite filter off in chat {chat_id}")
    return "Запрещает приглашать сообщества в группу"

#============================Развлекательные команды=============================

async def russian_roulette_func(message):
    chat_id = message.peer_id
    user_info = await group_api.users.get(user_ids=message.from_id)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    logging.info(f"User {user_name} use russian roulette in chat {chat_id}")
    if random.randint(0, 1) == 1:
        await kick(chat_id, message.from_id)
        return f"{user_name} проиграл и был кикнут."
    else:
        return f"{user_name} выйграл в рулетку."

async def duel_accept_func(message, first, second, outcome):
    chat_id = message.peer_id
    lost = random.choice([first, second])
    winner = [first, second]
    winner.remove(lost)
    print(lost, winner, [first, second], winner[0])
    lost_info = await group_api.users.get(user_ids=lost)
    lost_name = lost_info[0].first_name + " " + lost_info[0].last_name
    logging.info(f"User {lost_name} use duel in chat {chat_id}")
    if outcome == None:
        return f"{lost_name} проиграл дуэль."
    elif outcome == "kick":
        await kick(chat_id, lost)
        return f"{lost_name} проиграл дуэль и был кикнут."
    elif outcome == "ban_1_minute":
        return await ban_user_minutes_duel_func(chat_id, lost, winner[0], 1)
    elif outcome == "ban_10_minutes":
        return await ban_user_minutes_duel_func(chat_id, lost, winner[0], 10)
    elif outcome == "ban_1_hour":
        return await ban_user_hours_duel_func(chat_id, lost, winner[0], 1)   
    elif outcome == "ban_1_days":
        return await ban_user_days_duel_func(chat_id, lost, winner[0], 1)
    elif outcome == "ban_permanently":
        return await ban_user_permanent_duel_func(chat_id, lost, winner[0])
    
async def weather_func(message):
    chat_id = message.peer_id
    return "В разработке"

async def random_number_func(message, min, max):
    chat_id = message.peer_id
    if max == None:
       max = min 
       min = 0
    logging.info(f"User use random n0umber in chat {chat_id}")
    return random.randint(int(min), int(max)) 

async def choose_func(message, first, second):
    chat_id = message.peer_id
    logging.info(f"User use choose in chat {chat_id}")
    return random.choice([first, second])

async def choose_text_func(message, text):
    chat_id = message.peer_id
    logging.info(f"User use choose yes/no in chat {chat_id}")
    return random.choice(["Да", "Нет"])

#============================Команды для покупок=============================

async def anonymous_func(message):
    chat_id = message.peer_id
    chat_domen = ManageChats().get_domain(chat_id)
    logging.info(f"User use anonymous in chat {chat_id}")
    return chat_domen

async def anonymous_message_func(message, domain, text):
    chat_id = message.peer_id
    chat_domen = ManageChats().get_chat_by_domain(domain)
    logging.info(f"User {message.from_id} use anonymous message in chat {chat_id}")
    if chat_domen == None:
        return "Чата с таким доменом не существует"
    msg = "Пришло анонимное сообщенеие:\n" + text
    await group_api.messages.send(peer_id=chat_domen.chat_id, message=msg, random_id=0)
    return "Сообщение отправлено"

async def domain_func(message, text):
    user = ManageUsers().get_user_by_id(message.from_id)
    if user.money < 500:
        return "Недостаточно средств"
    ManageUsers().reduce_user_money(message.from_id, 500)
    chat_id = message.peer_id
    domain = ManageChats().change_domain(chat_id, text)
    logging.info(f"User {message.from_id} changed domain in chat {chat_id}")
    return domain

async def transfer_func(message, amount, user_link):
    chat_id = message.peer_id
    transfer_from = message.from_id
    transfer_from_info = await group_api.users.get(user_ids=transfer_from)
    transfer_from_name = transfer_from_info[0].first_name + " " + transfer_from_info[0].last_name
    if message.reply_message:
        user = message.reply_message.from_id
    else:
        user = user_link.split("|")[0][3:] 
    transfer_from_info = ManageUsers().get_user_by_id(transfer_from)
    if transfer_from_info.money < int(amount):
        logging.info(f"User {message.from_id} use transfer and failed in chat {chat_id}")
        return "Недостаточно средств"
    user_info = await group_api.users.get(user_ids=user)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    ManageUsers().reduce_user_money(transfer_from, amount)
    ManageUsers().add_user_money(user, amount)
    logging.info(f"User {message.from_id} use transfer in chat {chat_id}")
    return f"{transfer_from_name} перевёл {amount} пользователю {user}"

async def bag_func(message):
    chat_id = message.peer_id
    user = ManageChats().get_user(chat_id, message.from_id)
    print(user)
    msg = ""
    msg = msg + (f"Мешок: Банхаммер - {user[list(user.keys())[0]]['inventory']['banhammer']}\n"
                 f"Плюсопад - {user[list(user.keys())[0]]['inventory']['plusopad']}\n"
                 f"Минусит - {user[list(user.keys())[0]]['inventory']['minusit']}\n"
                 f"Анонимок - {user[list(user.keys())[0]]['inventory']['anon']}\n")
    logging.info(f"User {message.from_id} use bag in chat {chat_id}")
    return msg

async def bag_user_func(message, user_link):
    chat_id = message.peer_id
    user_id = user_link.split("|")[0][3:] 
    user_info = await group_api.users.get(user_ids=user_id)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    user = ManageChats().get_user(chat_id, user_id)
    msg = ""
    logging.info(f"User {message.from_id} use bag on {user_id} in chat {chat_id}")
    if user[list(user.keys())[0]]["inventory_view"]:
        msg = msg + (f"Мешок: Банхаммер - {user[list(user.keys())[0]]['inventory']['banhammer']}"
                     f"Плюсопад - {user[list(user.keys())[0]]['inventory']['plusopad']}"
                     f"Минусит - {user[list(user.keys())[0]]['inventory']['minusit']}"
                     f"Монет - {user[list(user.keys())[0]]['inventory']['coin']}"
                     f"Анонимок - {user[list(user.keys())[0]]['inventory']['anon']}")
        return msg
    else:
        return f"{user_name} закрыл свой мешок"
    
async def balance_func(message):
    chat_id = message.peer_id
    user_id = message.from_id
    balance = ManageUsers().get_user_balance(user_id)
    logging.info(f"User {message.from_id} use balance in chat {chat_id}")
    return balance

async def open_bag_func(message):
    chat_id = message.peer_id
    user_id = message.from_id
    ManageChats().change_user_inventory_view(chat_id, user_id, True)
    logging.info(f"User {message.from_id} use open bag in chat {chat_id}")
    return "Мешок открыт"

async def close_bag_func(message):
    chat_id = message.peer_id
    user_id = message.from_id
    ManageChats().change_user_inventory_view(chat_id,user_id, False)
    logging.info(f"User {message.from_id} use close bag in chat {chat_id}")
    return "Мешок закрыт"

async def plusopad_func(message):
    chat_id = message.peer_id
    user_id = message.from_id
    user = ManageChats().get_user(chat_id, user_id)
    
    if user[list(user.keys())[0]]["inventory"]["plusopad"] != 0:
        user[list(user.keys())[0]]["inventory"]["plusopad"] -= 1
        user[list(user.keys())[0]]["active_effects"].update({"plusopad": {"added": datetime.now(), "expires": datetime.now() + timedelta(days=7)}})
        ManageChats().update_user(chat_id, user)
        logging.info(f"User {message.from_id} use plusopad in chat {chat_id}")
        return "Плюсопад использован"
    else:
        logging.info(f"User {message.from_id} use plusopad and failed in chat {chat_id}")
        return "У вас нет плюсопада"
    
async def minusit_func(message):
    chat_id = message.peer_id
    user_id = message.from_id
    user = ManageChats().get_user(chat_id, user_id)
    if user[list(user.keys())[0]]["inventory"]["minusit"] != 0:
        user[list(user.keys())[0]]["inventory"]["minusit"] -= 1
        user[list(user.keys())[0]]["active_effects"].update({"minusit": {"added": datetime.now(), "expires": datetime.now() + timedelta(days=7)}})
        ManageChats().update_user(chat_id, user)
        logging.info(f"User {message.from_id} use minusit in chat {chat_id}")
        return "Минусит использован"
    else:
        logging.info(f"User {message.from_id} use minusit and failed in chat {chat_id}")
        return "У вас нет минусита"
    
#============================Анкета пользователя=============================

async def whoami_func(message):
    chat_id = message.peer_id
    user_id = message.from_id
    user = ManageChats().get_user(chat_id, user_id)
    user_self = ManageUsers().get_user_by_id(user_id)
    if user[list(user.keys())[0]]["nickname"]:
        nickname = user[list(user.keys())[0]]["nickname"]
    else:
        nickname = user[list(user.keys())[0]]["first_name"] + " " + user[list(user.keys())[0]]["last_name"]

    msg = (f"Это {nickname}\n"
           f"Ранг: {user[list(user.keys())[0]]['rank']}\n"
           f"Состоит в этой беседе с: {user[list(user.keys())[0]]['added']}\n"
           f"Всего сообщений: {user[list(user.keys())[0]]['msg_count']}\n"
           f"Репутация: звёздочек - {user_self.reputation} | плюсов - {user[list(user.keys())[0]]['rep']}\n"
           f"Актив в беседе: {'не написал ни одного сообщения' if user[list(user.keys())[0]]['last_msg'] == None else user[list(user.keys())[0]]['last_msg']}\n"
           f"Описание: {'нет описания' if user[list(user.keys())[0]]['description'] == None else user[list(user.keys())[0]]['description']} \n"
           f"Награды: {'нет наград' if user[list(user.keys())[0]]['rewards'] == None else user[list(user.keys())[0]]['rewards']}\n"
           f"Клан: {'нет клана' if user[list(user.keys())[0]]['clan'] == None else user[list(user.keys())[0]]['clan']}\n"
           f"Фракции: {', '.join(user[list(user.keys())[0]]['faction'])}\n"
           )
    logging.info(f"User {message.from_id} use whoami in chat {chat_id}")
    return msg          

async def whoami_user_func(message, user_link):
    chat_id = message.peer_id
    user_id = user_link.split("|")[0][3:] 
    user = ManageChats().get_user(chat_id, user_id)
    user_self = ManageUsers().get_user_by_id(user_id)
    if user[list(user.keys())[0]]["nickname"]:
        nickname = user[list(user.keys())[0]]["nickname"]
    else:
        nickname = user[list(user.keys())[0]]["first_name"] + " " + user[list(user.keys())[0]]["last_name"]

    msg = (f"Это {nickname}\n"
           f"Ранг: {user[list(user.keys())[0]]['rank']}\n"
           f"Состоит в этой беседе с: {user[list(user.keys())[0]]['added']}\n"
           f"Всего сообщений: {user[list(user.keys())[0]]['msg_count']}\n"  
           f"Репутация: звёздочек - {user_self.reputation} | плюсов - {user[list(user.keys())[0]]['rep']}\n"
           f"Актив в беседе: {user[list(user.keys())[0]]['last_msg']}\n"
           f"О себе: {user[list(user.keys())[0]]['description']}\n"
           f"Награды: {user[list(user.keys())[0]]['rewards']}\n"
           f"Клан: {user[list(user.keys())[0]]['clan']}\n"
           f"Фракция: {user[list(user.keys())[0]]['faction']}\n"
           )
    logging.info(f"User {message.from_id} use whoami on {user_id} in chat {chat_id}")
    return msg    

async def about_me_func(message, text):
    chat_id = message.peer_id
    user_id = message.from_id
    user = ManageChats().get_user(chat_id, user_id)
    user[list(user.keys())[0]]["description"] = text
    ManageChats().update_user(chat_id=chat_id, user=user)
    logging.info(f"User {message.from_id} use change about me in chat {chat_id}")
    return "О себе изменено"

async def about_me_user_func(message, user_link):
    chat_id = message.peer_id
    user_id = user_link.split("|")[0][3:] 
    user = ManageChats().get_user(chat_id, user_id)
    logging.info(f"User {message.from_id} use about me on {user_id} in chat {chat_id}")
    return user[list(user.keys())[0]]["description"]

async def user_rewards_func(message, user_link):
    chat_id = message.peer_id
    user_id = user_link.split("|")[0][3:] 
    user = ManageChats().get_user(chat_id, user_id)
    logging.info(f"User {message.from_id} use rewards on {user_id} in chat {chat_id}")
    return user[list(user.keys())[0]]["rewards"]

async def user_nickname_func(message, nick):
    chat_id = message.peer_id
    user_id = message.from_id
    user = ManageChats().get_user(chat_id, user_id)
    user[list(user.keys())[0]]["nickname"] = nick
    ManageChats().update_user(chat_id=chat_id, user=user)
    logging.info(f"User {message.from_id} use change nickname in chat {chat_id}")
    return "Никнейм изменен на " + nick

async def delete_nickname_func(message):
    chat_id = message.peer_id
    user_id = message.from_id
    user = ManageChats().get_user(chat_id, user_id)
    user[list(user.keys())[0]]["nickname"] = ""
    ManageChats().update_user(chat_id=chat_id, user=user)
    logging.info(f"User {message.from_id} use delete nickname in chat {chat_id}")
    return "Никнейм удален"

async def user_title_func(message, title):
    chat_id = message.peer_id
    user_id = message.from_id
    user = ManageChats().get_user(chat_id, user_id)
    user[list(user.keys())[0]]["rank"] = title
    ManageChats().update_user(chat_id=chat_id, user=user)
    logging.info(f"User {message.from_id} use change title in chat {chat_id}")
    return "Звание изменено на " + title

async def delete_title_func(message):
    chat_id = message.peer_id
    user_id = message.from_id
    user = ManageChats().get_user(chat_id, user_id)
    user[list(user.keys())[0]]["rank"] = ""
    ManageChats().update_user(chat_id=chat_id, user=user)
    logging.info(f"User {message.from_id} use delete title in chat {chat_id}")
    return "Звание удалено"

async def show_user_factions_func(message):
    chat_id = message.peer_id
    user = ManageChats().get_user(chat_id, message.from_id)
    logging.info(f"User {message.from_id} use show user factions in chat {chat_id}")
    return user[list(user.keys())[0]]["faction"]

async def show_user_clan_func(message):
    chat_id = message.peer_id
    user = ManageChats().get_user(chat_id, message.from_id)
    logging.info(f"User {message.from_id} use show user clan in chat {chat_id}")
    return user[list(user.keys())[0]]["clan"]

#============================Статистическая информация=============================

async def chat_info_func(message):
    chat_id = message.peer_id
    chat = ManageChats().get_chat(chat_id)
    return chat

async def chat_stats_func(message, time):
    chat_id = message.peer_id
    users = ManageChats().get_users(chat_id)
    stats = []
    if time == "сутки":
        time = 86400
    if time == "неделя":
        time = 604800
    if time == "месяц":
        time = 2592000
    if time == "вся":
        for user in users:
            stats.append([users[user]["first_name"] + " " + users[user]["last_name"], users[user]["msg_count"]])
        return stats

    for user in users:
        count = 0
        for i in range(len(users[user]["msgs"])):
            if datetime.strptime(users[user]["msgs"][i][0], "%Y-%m-%d %H:%M:%S") > datetime.now() - timedelta(seconds=int(time)):
                count += 1
        stats.append([users[user]["first_name"] + " " + users[user]["last_name"], count])
    logging.info(f"User {message.from_id} use chat stats in chat {chat_id}")
    return stats

async def old_members_func(message):
    chat_id = message.peer_id
    users = ManageChats().get_users(chat_id)
    stat = []
    for user in users:
        if users[user]["last_msg"] == None:
            continue
        if datetime.strptime(users[user]["last_msg"], "%Y-%m-%d %H:%M:%S") > datetime.now() - timedelta(days=30):
            stat.append([user, users[user]["first_name"] + " " + users[user]["last_name"]])
    logging.info(f"User {message.from_id} use old members in chat {chat_id}")
    return stat

async def new_members_func(message):
    chat_id = message.peer_id
    users = ManageChats().get_users(chat_id)
    stat = []
    for user in users:
        if  datetime.strptime(users[user]["added"], "%Y-%m-%d %H:%M:%S") > datetime.now() - timedelta(hours=24):
            stat.append([user, users[user]["first_name"] + " " + users[user]["last_name"]])
    logging.info(f"User {message.from_id} use new members in chat {chat_id}")
    return stat

async def online_members_func(message):
    chat_id = message.peer_id
    users = ManageChats().get_users(chat_id)
    stat = []
    for user in users:
        if int(user) < 0:
            continue
        user_online = await group_api.users.get(user_ids=user, fields="online")
        if user_online[0].online == True:
            stat.append([user, users[user]["first_name"] + " " + users[user]["last_name"]])
    logging.info(f"User {message.from_id} use online members in chat {chat_id}")
    return stat

async def my_bans_func(message):
    chat_id = message.peer_id
    user = ManageUsers.get_user_by_id(message.from_id)
    logging.info(f"User {message.from_id} use my bans in chat {chat_id}")
    return user[list(user.keys())[0]]["bans"]

async def who_added_me_func(message):
    chat_id = message.peer_id
    user = ManageChats().get_user(chat_id, message.from_id)
    logging.info(f"User {message.from_id} use who added me in chat {chat_id}")
    return user[list(user.keys())[0]]["add_id"]

async def who_added_user_func(message, user_link):
    chat_id = message.peer_id
    user_id = user_link.split("|")[0][3:]
    user = ManageChats().get_user(chat_id, user_id)
    logging.info(f"User {message.from_id} use who added user in chat {chat_id}")
    return user[list(user.keys())[0]]["add_id"]

#============================Модуль «Репутация»=============================

async def rating_func(message):
    chat_id = message.peer_id
    users = ManageChats().get_users(chat_id=chat_id)
    stats = []
    for user in users:
        stats.append([users[user]["first_name"] + " " + users[user]["last_name"], users[user]["rep"]])
    logging.info(f"User {message.from_id} use rating in chat {chat_id}")
    return stats

async def add_rating_func(message, amount):
    chat_id = message.peer_id
    chat_settings = ManageChats().get_settings(chat_id)
    from_id = message.from_id
    user_id = message.reply_message.from_id
    from_user = ManageChats().get_user(chat_id, from_id)
    if from_user[list(from_user.keys())[0]]["rep_given"] < 100000000:# NEED FIX
        user = ManageChats().get_user(chat_id, user_id)
        user[list(user.keys())[0]]["rep"] += int(amount)
        ManageChats().update_user(chat_id, user)
        from_user[list(from_user.keys())[0]]["rep_given"] += 1
        ManageChats().update_user(chat_id, from_user)
        logging.info(f"User {message.from_id} use add rating in chat {chat_id}")
        return "Репутация пользователя " + user[list(user.keys())[0]]["first_name"] + " " + user[list(user.keys())[0]]["last_name"] + " увеличена на " + str(amount)
    else:
        logging.info(f"User {message.from_id} use add rating and failed in chat {chat_id}")
        return "Вы исчерпали лимит на выдачу репутации. Для дальнейшей выдачи репутации купить предмет 'Плюсопад'"

async def reduce_rating_func(message, amount):
    chat_id = message.peer_id
    chat_settings = ManageChats().get_settings(chat_id)
    from_id = message.from_id
    user_id = message.reply_message.from_id
    from_user = ManageChats().get_user(chat_id, from_id)
    user = ManageChats().get_user(chat_id, user_id)
    if from_user[list(from_user.keys())[0]]["rep_given"] < 1000000000:# NEED FIX
        user = ManageChats().get_user(chat_id, user_id)
        user[list(user.keys())[0]]["rep"] -= int(amount)
        ManageChats().update_user(chat_id, user)
        from_user[list(from_user.keys())[0]]["rep_given"] += 1
        ManageChats().update_user(chat_id, from_user)
        logging.info(f"User {message.from_id} use reduce rating in chat {chat_id}")
        return "Репутация пользователя " + user[list(user.keys())[0]]["first_name"] + " " + user[list(user.keys())[0]]["last_name"] + " уменьшена на " + str(amount)
    else:
        logging.info(f"User {message.from_id} use reduce rating and failed in chat {chat_id}")
        return "Вы исчерпали лимит на выдачу репутации. Для дальнейшей выдачи репутации купить предмет 'Минусит'"


async def add_star_rating_func(message, amount):
    chat_id = message.peer_id
    from_id = message.from_id
    stars = ManageUsers().get_user_stars(from_id)
    if stars < int(amount):
        logging.info(f"User {message.from_id} use add star rating and failed in chat {chat_id}")
        return "У вас недостаточно звёздочек для увеличения репутации"
    
    user_id = message.reply_message.from_id
    ManageUsers().reduce_user_stars(from_id, int(amount))
    ManageUsers().add_user_reputation(user_id, int(amount))
    user = ManageUsers().get_user_by_id(user_id)
    logging.info(f"User {message.from_id} use add star rating in chat {chat_id}")
    return "Звёздная репутация пользователя " + user.first_name + " " + user.last_name + " увеличена на " + str(amount)

async def reset_rating_func(message):
    chat_id = message.peer_id
    users = ManageChats().get_users(chat_id)
    for key, value in users.items():
        value["rep"] = 0
        user = {key: value}
        ManageChats().update_user(chat_id, user)
    logging.info(f"User {message.from_id} use reset rating in chat {chat_id}")
    return "Репутация пользователей обнулена"

async def star_holders_func(message):
    chat_id = message.peer_id
    chat_users = ManageChats().get_users(chat_id=chat_id)
    stats = []
    for user in chat_users:
        if user == None:
            continue
        user_info = ManageUsers().get_user_by_id(user)
        if user_info.stars > 0 and chat_users[user]["inventory_view"] == True:
            stats.append([chat_users[user]["first_name"] + " " + chat_users[user]["last_name"], user_info.stars])
    logging.info(f"User {message.from_id} use star holders in chat {chat_id}")
    return stats

async def users_stars_func(message):
    chat_id = message.peer_id
    chat_users = ManageChats().get_users(chat_id=chat_id)
    stats = []
    for user in chat_users:
        if user == None:
            continue
        try:
            user_info = ManageUsers().get_user_by_id(user)
            stats.append([chat_users[user]["first_name"] + " " + chat_users[user]["last_name"], user_info.reputation])
        except:
            logging.exception(f"User {message.from_id} use users stars and failed in chat {chat_id}")
    logging.info(f"User {message.from_id} use users stars in chat {chat_id}")
    return stats

async def all_stars_func(message):
    chat_id = message.peer_id
    users = ManageUsers().get_all_users()
    stats = []
    users.sort(key=lambda x: x.reputation, reverse=True)
    i = 0 
    for user in users:
        if i < 10:
            stats.append([user.first_name + " " + user.last_name, user.reputation])
            i += 1
    logging.info(f"User {message.from_id} use all stars in chat {chat_id}")
    return stats


async def iris_forbs_func(message):
    chat_id = message.peer_id
    users = ManageUsers().get_all_users()
    users.sort(key=lambda x: x.money, reverse=True)
    stats = []
    i = 0
    for user in users:
        if i < 10:
            stats.append([user.first_name + " " + user.last_name, user.money])
            i += 1
    logging.info(f"User {message.from_id} use iris forbs in chat {chat_id}")
    return stats

#async def deviz_forbs_func(message):

async def b_coin_func(message, amount):
    chat_id = message.peer_id
    user_info = ManageUsers().get_user_by_id(message.from_id)
    if user_info.inventory["coin"] >= amount:
        user_info.inventory["coin"] -= amount
        ManageUsers().update_user(user_info)
        ManageChats().add_group_coins(chat_id, amount)
        logging.info(f"User {message.from_id} use b coin in chat {chat_id}")
        return f"{user_info.first_name} {user_info.last_name} передал группе {amount} монет"
    else:
        logging.info(f"User {message.from_id} use b coin and failed in chat {chat_id}")
        return "Недостаточно монет"
    
async def coins_func(message, amount, chat_link):
    return "в разработке " + chat_link + " " + str(amount)

async def b_top_func(message):
    chats = ManageChats().get_chats()
    chats.sort(key=lambda x: x["coins"], reverse=True)
    stats = []
    i = 0
    for chat in chats:
        if i < 10:
            stats.append([chat["title"], chat["coins"]])
            i += 1
    logging.info(f"User {message.from_id} use b top in chat {message.peer_id}")
    return stats

async def b_top_day_func(message):
    return "в разработке"

async def g_top_func(message):
    return "в разработке"

#============================Модуль «Закладки»=============================

async def bookmark_func(message, text):
    chat_id = message.peer_id
    from_id = message.from_id
    date = str(datetime.fromtimestamp(message.date))
    if message.reply_message is not None:
        bookmark_id = message.reply_message.conversation_message_id
    else:
        bookmark_id = message.conversation_message_id
    user = ManageChats().get_user(chat_id, from_id)
    count = ManageChats().get_bookmarks_count(chat_id)
    chat_settings = ManageChats().get_settings(chat_id)
    if user[list(user.keys())[0]]["rep"] < int(chat_settings['bookmarks_need_rep']):
        logging.info(f"User {message.from_id} use bookmark and failed by reputation in chat {chat_id}")
        return "Недостаточно репутации"
    bookmark = {count:{
                "from_id": from_id,
                "name": text,
                "date": date,
                "message_id": bookmark_id,
                "active": True}} 
    user[list(user.keys())[0]]["bookmarks"].update(bookmark)
    ManageChats().update_user(chat_id=chat_id, user=user)
    ManageChats().add_bookmark(chat_id, bookmark)
    logging.info(f"User {message.from_id} use bookmark in chat {chat_id}")
    return "Закладка добавлена"

async def bookmark_number_func(message, number):
    chat_id = message.peer_id
    bookmarks = ManageChats().get_bookmarks(chat_id)
    logging.info(f"User {message.from_id} use bookmark number {number} in chat {chat_id}")
    if bookmarks[number]["active"] == True:
        return {number: bookmarks[number]}
    elif bookmarks[number]["active"] == False and message.from_id == bookmarks[number]["from_id"]:
        return {number: bookmarks[number]}
    else:
        return "Такой закладки нет"

async def chatbook_func(message):
    chat_id = message.peer_id
    bookmarks = ManageChats().get_bookmarks(chat_id)
    logging.info(f"User {message.from_id} use chatbook in chat {chat_id}")
    return bookmarks

async def delete_bookmark_func(message, number):
    chat_id = message.peer_id
    bookmark = ManageChats().get_bookmark(chat_id, number)
    user = ManageChats().get_user(chat_id, bookmark[list(bookmark.keys())[0]]["from_id"])
    bookmark_id = str(list(bookmark.keys())[0])
    print(user[list(user.keys())[0]]["bookmarks"], bookmark_id, bookmark_id in user[list(user.keys())[0]]["bookmarks"])
    user[list(user.keys())[0]]["bookmarks"].pop(bookmark_id)
    ManageChats().update_user(chat_id=chat_id, user=user)
    ManageChats().remove_bookmark(chat_id, number)
    logging.info(f"User {message.from_id} use delete bookmark number {number} in chat {chat_id}")
    return "Закладка удалена"

async def exclude_bookmark_func(message, number):
    chat_id = message.peer_id
    bookmark = ManageChats().get_bookmark(chat_id, number)
    bookmark_id = str(list(bookmark.keys())[0])
    ManageChats().exclude_bookmark(chat_id, bookmark_id)
    logging.info(f"User {message.from_id} use exclude bookmark number {number} in chat {chat_id}")
    return "Закладка исключена"

async def my_bookmarks_func(message):
    chat_id = message.peer_id
    user = ManageChats().get_user(chat_id, message.from_id)
    bookmarks = user[list(user.keys())[0]]["bookmarks"]
    logging.info(f"User {message.from_id} use my bookmarks in chat {chat_id}")
    return bookmarks

async def cladman_add_func(message, user_link):
    chat_id = message.peer_id
    user_id = user_link.split("|")[0][3:] 
    ManageChats().return_all_bookmarks_from_user(chat_id, user_id)
    logging.info(f"User {message.from_id} use cladman add bookmark in chat {chat_id}")
    return "Закладки пользователя возвращены"

async def cladman_remove_func(message, user_link):
    chat_id = message.peer_id
    user_id = user_link.split("|")[0][3:] 
    ManageChats().exclude_all_bookmarks_from_user(chat_id, user_id)
    logging.info(f"User {message.from_id} use cladman remove bookmark in chat {chat_id}")
    return "Закладки пользователя исключены"

async def bookmarks_rating_func(message, number):
    chat_id = message.peer_id
    chat_settings = ManageChats().get_settings(chat_id)
    chat_settings["bookmarks_need_rep"] = number
    ManageChats().change_settings(chat_id, chat_settings)
    logging.info(f"User {message.from_id} use bookmarks rating in chat {chat_id}")
    return "Рейтинг закладок изменен"

#============================Модуль «Награды»=============================

async def reward_func(message, grade, user_link, text):
    chat_id = message.peer_id
    user_id = user_link.split("|")[0][3:] 
    user = ManageChats().get_user(chat_id, user_id)
    user_name = await group_api.users.get(user_ids=user_id)
    user_name = user_name[0].first_name + " " + user_name[0].last_name
    from_user = await group_api.users.get(user_ids=message.from_id)
    from_user = from_user[0].first_name + " " + from_user[0].last_name
    if grade == None:
        grade = 1
    if user[list(user.keys())[0]]["rewards"] == None:
        user[list(user.keys())[0]]["rewards"] = []
    user[list(user.keys())[0]]["rewards"].append([grade, text, str(datetime.fromtimestamp(message.date)), message.from_id])
    ManageChats().update_user(chat_id=chat_id, user=user)
    logging.info(f"User {message.from_id} give reward to {user_id} in chat {chat_id}")
    return f"{from_user} наградил {user_name} медалью {grade} степени - {text}."

async def remove_all_rewards_func(message, user_link):
    chat_id = message.peer_id
    user_id = user_link.split("|")[0][3:] 
    user = ManageChats().get_user(chat_id, user_id)
    user[list(user.keys())[0]]["rewards"] = []
    ManageChats().update_user(chat_id=chat_id, user=user)
    logging.info(f"User {message.from_id} remove all rewards from {user_id} in chat {chat_id}")
    return "Все награды удалены"

async def remove_rewards_from_user_func(message, user_link):
    chat_id = message.peer_id
    user_id = user_link.split("|")[0][3:] 
    user_name = await group_api.users.get(user_ids=user_id)
    user_name = user_name[0].first_name + " " + user_name[0].last_name
    users = ManageChats().get_users(chat_id=chat_id)
    delete = []
    for user in users:
        user["rewards"] = [i for i in user["rewards"] if i[3] != user_id]
        ManageChats().update_user(chat_id=chat_id, user=user)
    logging.info(f"User {message.from_id} remove all rewards given by {user_id} in chat {chat_id}")
    return f"Все награды от {user_name} удалены"

async def remove_reward_func(message, number, user_link):
    chat_id = message.peer_id
    user_id = user_link.split("|")[0][3:] 
    user = ManageChats().get_user(chat_id, user_id)
    reward = user[list(user.keys())[0]]["rewards"].pop(number)
    ManageChats().update_user(chat_id=chat_id, user=user)
    logging.info(f"User {message.from_id} remove reward {number} from {user_id} in chat {chat_id}")
    return f"Награда {reward[1]} удалена"

async def user_rewards_func(message, user_link):
    chat_id = message.peer_id
    user_id = user_link.split("|")[0][3:] 
    user = ManageChats().get_user(chat_id, user_id)
    rewards = user[list(user.keys())[0]]["rewards"]
    logging.info(f"User {message.from_id} use user rewards in chat {chat_id}")
    return rewards

#============================Модуль «Антиспам»=============================

async def antispam_add_func(message):
    chat_id = message.peer_id
    chat_settings = ManageChats().get_settings(chat_id)
    chat_settings["antispam_auto"] = True
    ManageChats().change_settings(chat_id, chat_settings)
    logging.info(f"User {message.from_id} use antispam in chat {chat_id}")
    return "Антиспам включен"

async def antispam_remove_func(message):
    chat_id = message.peer_id
    chat_settings = ManageChats().get_settings(chat_id)
    chat_settings["antispam_auto"] = False
    ManageChats().change_settings(chat_id, chat_settings)
    logging.info(f"User {message.from_id} use antispam in chat {chat_id}")
    return "Антиспам выключен"

#============================Модуль «Кланы»=============================

async def create_clan_func(message, name):
    chat_id = message.peer_id
    clan_name = name.split("\n")[0]
    description = name.split("\n")
    description.pop(0)
    description = "\n".join(description)
    clan = {
        clan_name: {
            "description": str(description),
            "owner": str(message.from_id),
            "members": [message.from_id],
        }
    }
    user = ManageChats().get_user(chat_id, message.from_id)
    logging.info(f"User {message.from_id} use create clan in chat {chat_id}")
    if user[list(user.keys())[0]]["clan"] != None:
        return "Вы уже состоите в клане"

    if ManageChats().get_clan(chat_id, clan_name):
        return "Клан с таким именем уже существует"
    
    if ManageChats().add_clan(chat_id, clan):
        user[list(user.keys())[0]]["clan"] = clan_name
        ManageChats().update_user(chat_id, user)
        return "Клан создан"
    else:
        return "Не удалось создать клан"

async def join_clan_func(message, name):
    chat_id = message.peer_id
    user_id = message.from_id
    user = ManageChats().get_user(chat_id, user_id)
    user[list(user.keys())[0]]["clan"] = name
    ManageChats().update_user(chat_id, user)
    ManageChats().join_clan(chat_id, name, user_id)
    logging.info(f"User {message.from_id} use join clan in chat {chat_id}")
    return "Вы вступили в клан"

async def delete_clan_func(message, name):
    chat_id = message.peer_id
    clan = ManageChats().get_clan(chat_id, name)
    clan_owner = clan[list(clan.keys())[0]]["owner"]
    if str(message.from_id) == clan_owner:
        for member in clan[list(clan.keys())[0]]["members"]:
            ManageChats().remove_user_clan(chat_id, member)
        ManageChats().remove_clan_member(chat_id, name)
        ManageChats().delete_clan(chat_id, name)
        logging.info(f"User {message.from_id} use delete clan in chat {chat_id}")
        return "Клан удален"
    else:
        logging.info(f"User {message.from_id} use delete clan and failed in chat {chat_id}")
        return "Не удалось удалить клан"
    
async def leave_clan_func(message, name):
    chat_id = message.peer_id
    user_id = message.from_id
    ManageChats().remove_user_clan(chat_id, user_id)
    ManageChats().leave_clan(chat_id, name, user_id)
    logging.info(f"User {message.from_id} use leave clan in chat {chat_id}")
    return "Вы покинули клан"

async def change_clan_name_func(message, new_name):
    chat_id = message.peer_id
    clan = ManageChats().get_clan_by_owner(chat_id, message.from_id)
    clan_owner = clan[list(clan.keys())[0]]["owner"]
    clan_name = list(clan.keys())[0]
    if message.from_id == clan_owner:
        ManageChats().change_clan_name(chat_id, clan_name, new_name)
        logging.info(f"User {message.from_id} use change clan name in chat {chat_id}")
        return "Имя клана изменено"
    else:
        logging.info(f"User {message.from_id} use change clan name and failed in chat {chat_id}")
        return "Не удалось изменить имя клана"
    
async def get_clans_func(message):
    chat_id = message.peer_id
    clans = ManageChats().get_clans(chat_id)
    logging.info(f"User {message.from_id} use get clans in chat {chat_id}")
    return clans

async def call_all_clans_members_func(message):
    chat_id = message.peer_id
    user_id = message.from_id
    user = ManageChats().get_user(chat_id, user_id)
    user_clan = user[list(user.keys())[0]]["clan"]
    clan = ManageChats().get_clan(chat_id, user_clan)
    members = clan[list(clan.keys())[0]]["members"]
    res = []
    for member in members:
        member_info = await group_api.users.get(user_ids=member)
        member_name = member_info[0].first_name + " " + member_info[0].last_name
        res.append([member,member_name])
    logging.info(f"User {message.from_id} use call all clans members in chat {chat_id}")
    return res

async def get_clan_members_func(message, name):
    chat_id = message.peer_id
    clan = ManageChats().get_clan(chat_id, name)
    members = clan[list(clan.keys())[0]]["members"]
    logging.info(f"User {message.from_id} use get clan members in chat {chat_id}")
    return members
    
async def kick_from_clan_func(message, name):
    chat_id = message.peer_id
    user_id = message.from_id
    kick_user_id = name.split("|")[0][3:] 
    kick_user_info = await group_api.users.get(user_ids=kick_user_id, fields="screen_name,first_name,last_name")
    kick_user_name = kick_user_info[0].first_name + " " + kick_user_info[0].last_name
    user = ManageChats().get_user(chat_id, user_id)
    user_clan = user[list(user.keys())[0]]["clan"]
    clan = ManageChats().get_clan(chat_id, user_clan)
    clan_owner = clan[list(clan.keys())[0]]["owner"]
    members = clan[list(clan.keys())[0]]["members"]
    if user_id == clan_owner and kick_user_id in members:
        ManageChats().remove_user_clan(chat_id, user_id)
        ManageChats().leave_clan(chat_id, clan, user_id)
        ManageChats().remove_clan_member(chat_id, clan, kick_user_id)
        logging.info(f"User {message.from_id} use kick from clan in chat {chat_id}")
        return f"{kick_user_name} был исключен из клана"
    else:
        logging.info(f"User {message.from_id} use kick from clan and failed in chat {chat_id}")
        return f"Не удалось исключить {kick_user_name} из клана"
    
#============================Модуль «Кружки»=============================

async def create_faction_func(message, name):
    chat_id = message.peer_id
    user_id = message.from_id
    faction_name = name.split("\n")[0]
    description = name.split("\n")
    description.pop(0)
    description = "\n".join(description)
    faction = {
        faction_name: {
            "description": description,
            "owner": user_id,
            "members": [user_id],
        }
    }
    user = ManageChats().get_user(chat_id, user_id)
    logging.info(f"User {message.from_id} use create faction in chat {chat_id}")
    if ManageChats().get_faction(chat_id, faction_name):
        return "Кружок с таким именем уже существует"
    if ManageChats().add_faction(chat_id, faction):
        user[list(user.keys())[0]]["faction"].append(faction_name)
        ManageChats().update_user(chat_id, user)
        return "Кружок создан"
    else:
        return "Не удалось создать кружок"

async def join_faction_func(message, name):
    chat_id = message.peer_id
    user_id = message.from_id
    user = ManageChats().get_user(chat_id, user_id)
    user_faction = user[list(user.keys())[0]]["faction"]
    logging.info(f"User {message.from_id} use join faction in chat {chat_id}")
    if name in user_faction:
        return "Вы уже состоите в этом кружке"
    else:
        ManageChats().add_faction_member(chat_id, name, user_id)
        ManageChats().join_faction(chat_id, name, user_id)
        return "Вы присоединились к кружку"

async def leave_faction_func(message, name):
    chat_id = message.peer_id
    user_id = message.from_id
    ManageChats().remove_faction_member(chat_id, name, user_id)
    ManageChats().leave_faction(chat_id, name, user_id)
    logging.info(f"User {message.from_id} use leave faction in chat {chat_id}")
    return "Вы покинули кружок"

async def call_all_faction_members_func(message, name):
    chat_id = message.peer_id
    user_id = message.from_id
    user = ManageChats().get_user(chat_id, user_id)
    user_faction = user[list(user.keys())[0]]["faction"]
    faction_info = ManageChats().get_faction(chat_id, name)
    members = faction_info[list(faction_info.keys())[0]]["members"]
    logging.info(f"User {message.from_id} use call all faction members in chat {chat_id}")
    return members

async def get_faction_members_func(message, name):
    chat_id = message.peer_id
    faction = ManageChats().get_faction(chat_id, name)
    members = faction[list(faction.keys())[0]]["members"]
    logging.info(f"User {message.from_id} use get faction members in chat {chat_id}")
    return members

async def delete_faction_func(message, name):
    chat_id = message.peer_id
    user_id = message.from_id
    faction = ManageChats().get_faction(chat_id, name)
    ManageChats().delete_faction(chat_id, faction)
    logging.info(f"User {message.from_id} use delete faction in chat {chat_id}")
    return "Кружок удален"

async def kick_from_faction_func(message, name):
    chat_id = message.peer_id
    user_id = message.from_id
    kick_user_id = name.split("|")[0][3:] 
    kick_user_info = await group_api.users.get(user_ids=kick_user_id, fields="screen_name,first_name,last_name")
    kick_user_name = kick_user_info[0].first_name + " " + kick_user_info[0].last_name
    user = ManageChats().get_user(chat_id, user_id)
    user_faction = user[list(user.keys())[0]]["faction"]
    logging.info(f"User {message.from_id} use kick from faction in chat {chat_id}")
    if user_id in user_faction:
        ManageChats().remove_faction_member(chat_id, name, kick_user_id)
        return f"{kick_user_name} был исключен из кружка"
    else:
        return f"Не удалось исключить {kick_user_name} из кружка"
    
async def change_faction_name_func(message,old_name, new_name):
    chat_id = message.peer_id
    faction = ManageChats().get_faction(chat_id, old_name)
    faction_owner = faction[list(faction.keys())[0]]["owner"]
    faction_name = list(faction.keys())[0]
    logging.info(f"User {message.from_id} use change faction name in chat {chat_id}")
    if message.from_id == faction_owner:
        ManageChats().change_faction_name(chat_id, faction_name, new_name)
        return "Имя кружка изменено"
    else:
        return "Не удалось изменить имя кружка"
    
async def get_factions_func(message):
    chat_id = message.peer_id
    factions = ManageChats().get_factions(chat_id)
    logging.info(f"User {message.from_id} use get factions in chat {chat_id}")
    return factions

#============================Модуль «Отношения и Браки»=============================

async def add_relationship_func(message, user_link):
    chat_id = message.peer_id
    from_id = message.from_id
    user_id = user_link.split("|")[0][3:] 
    user_info = await group_api.users.get(user_ids=user_id)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    from_info = await group_api.users.get(user_ids=from_id)
    from_name = from_info[0].first_name + " " + from_info[0].last_name
    count = ManageChats().get_relationship_count(chat_id)
    relationship = {count:{"user": str(from_id),
                     "with_user": str(user_id),
                     "status": 0,
                     "hp": 0,
                     "start_date": str(datetime.now()),
                     "history": {},
                     "married": False,
                     "proposal": False}}
    ManageChats().add_relationships(chat_id, relationship)
    logging.info(f"User {message.from_id} use add relationship in chat {chat_id}")
    return f"{from_name} хочет познакомиться с {user_name}"

async def accept_relationship_func(message, relationship,i):
    chat_id = message.peer_id
    from_id = message.from_id
    if relationship["with_user"] == from_id:
        user_name = relationship["user"]
    else:
        user_name = relationship["with_user"]
    user_info = await group_api.users.get(user_ids=user_name)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    from_info = await group_api.users.get(user_ids=from_id)
    from_name = from_info[0].first_name + " " + from_info[0].last_name
    relationship["status"] = 1
    relationship["start_date"] = str(datetime.now())
    relationship["history"].update({str(datetime.now()):{ "action": "Отношения повышены до 1 уровня", "from": from_id}})
    rel = {i:relationship}
    ManageChats().change_relationships(chat_id, rel)
    logging.info(f"User {message.from_id} use accept relationship in chat {chat_id}")
    return f"Отношения между {from_name} и {user_name} были повышены до 1 уровня"

async def remove_relationship_func(message, user_link):
    chat_id = message.peer_id
    from_id = message.from_id
    user_id = user_link.split("|")[0][3:] 
    user_info = await group_api.users.get(user_ids=user_id)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    from_info = await group_api.users.get(user_ids=from_id)
    from_name = from_info[0].first_name + " " + from_info[0].last_name
    relationships = ManageChats().get_relationships(chat_id)
    for i in relationships:
        if relationships[i]["user"] == from_id or relationships[i]["with_user"] == from_id:
            logging.info(f"User {message.from_id} use remove relationship in chat {chat_id}")
            ManageChats().delete_relationships(chat_id, i)
            return f"Отношения между {from_name} и {user_name} были расторгнуты"
        
async def set_relationship_base_func(message, user_link):
    chat_id = message.peer_id
    from_id = message.from_id
    user_id = user_link.split("|")[0][3:] 
    ManageChats().set_relationship_main(chat_id, from_id, user_id)
    logging.info(f"User {message.from_id} use set relationship base in chat {chat_id}")
    return "Основа для отношений установлена"

async def get_relationship_status_func(message, user_link):
    chat_id = message.peer_id
    from_id = message.from_id
    user_id = user_link.split("|")[0][3:]
    user_info = await group_api.users.get(user_ids=user_id)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    from_info = await group_api.users.get(user_ids=from_id)
    from_name = from_info[0].first_name + " " + from_info[0].last_name
    relationships = ManageChats().get_relationships(chat_id)
    logging.info(f"User {message.from_id} use get relationship status in chat {chat_id}")
    for i in relationships:
        print(relationships[i], i)
        if relationships[i]["user"] == str(from_id) or relationships[i]["with_user"] == str(from_id):
            return relationships[i], user_name, from_name

async def get_relationship_history_func(message):
    chat_id = message.peer_id
    relationships = ManageChats().get_relationships(chat_id)
    for i in relationships:
        if relationships[i]["user"] == message.from_id or relationships[i]["with_user"] == message.from_id:
            return relationships[i]["history"]
    logging.info(f"User {message.from_id} use get relationship history in chat {chat_id}")
    return "Не удалось найти историю действий"

async def get_my_relationships_func(message):
    chat_id = message.peer_id
    relationships = ManageChats().get_relationships(chat_id)
    roster = []
    for i in relationships:
        print(relationships[i])
        if relationships[i]["user"] == str(message.from_id) or relationships[i]["with_user"] == str(message.from_id):
            roster.append([relationships[i]["user"], relationships[i]["with_user"], relationships[i]["status"]])
    logging.info(f"User {message.from_id} use get my relationships in chat {chat_id}")
    return roster

async def get_all_main_relationships_func(message):
    chat_id = message.peer_id
    users = ManageChats().get_users(chat_id)
    roster = []
    for user in users:
        if users[user]["relationship_main"] != None:
            roster.append([user, users[user]["relationship_main"]])
    logging.info(f"User {message.from_id} use get all main relationships in chat {chat_id}")
    return roster

async def create_marriage_func(message, user_link):
    chat_id = message.peer_id
    from_id = message.from_id
    from_info = ManageUsers().get_user_by_id(from_id)
    from_name = from_info.first_name + " " + from_info.last_name
    user = ManageChats().get_user(chat_id, from_id)
    if user[list(user.keys())[0]]["married_with"] != None:
        return "Вы уже женаты"
    user_id = user_link.split("|")[0][3:]
    logging.info(f"User {message.from_id} use create marriage with {user_id} in chat {chat_id}")
    user_info = ManageUsers().get_user_by_id(user_id)
    user_name = user_info.first_name + " " + user_info.last_name
    user = ManageChats().get_user(chat_id, user_id)
    if user[list(user.keys())[0]]["married_with"] != None:
        return f"{user_name} уже женат(a)"
    relationships = ManageChats().get_relationships(chat_id)
    for i in relationships:
        if relationships[i]["user"] == str(from_id) or relationships[i]["with_user"] == str(from_id) and relationships[i]["user"] == str(user_id) or relationships[i]["with_user"] == str(user_id):
            relationships[i]["proposal"] = True
            rel = {i:relationships[i]}
            ManageChats().change_relationships(chat_id, rel)
            return f"{from_name} сделал преложение {user_name}"
        
    return "Не удалось создать брак"

async def accept_marriage_func(message):
    chat_id = message.peer_id
    from_id = str(message.from_id)
    from_info = ManageUsers().get_user_by_id(from_id)
    from_name = from_info.first_name + " " + from_info.last_name
    relationships = ManageChats().get_relationships(chat_id)
    logging.info(f"User {message.from_id} use accept marriage in chat {chat_id}")
    for i in relationships:
        if relationships[i]["user"] == from_id or relationships[i]["with_user"] == from_id and relationships[i]["proposal"] == True:
            relationships[i]["proposal"] = False
            relationships[i]["married"] = True
            relationships[i]["history"].update({str(datetime.now()):{ "action": "Брак был подтвержден", "from": from_id}})
            rel = {i:relationships[i]}
            ManageChats().change_relationships(chat_id, rel)
            user = ManageChats().get_user(chat_id, relationships[i]["with_user"])
            user[list(user.keys())[0]]["married_with"] = relationships[i]["user"]
            ManageChats().update_user(chat_id, user)
            user = ManageChats().get_user(chat_id, relationships[i]["user"])
            user[list(user.keys())[0]]["married_with"] = relationships[i]["with_user"]
            ManageChats().update_user(chat_id, user)
            return f"{relationships[i]['with_user']} и {relationships[i]['user']} теперь женаты"

    return "Не удалось подтвердить брак"

async def decline_marriage_func(message):
    chat_id = message.peer_id
    from_id = message.from_id
    from_info = ManageUsers().get_user_by_id(from_id)
    from_name = from_info.first_name + " " + from_info.last_name
    relationships = ManageChats().get_relationships(chat_id)
    logging.info(f"User {message.from_id} use decline marriage in chat {chat_id}")
    for i in relationships:
        if relationships[i]["user"] == from_id or relationships[i]["with_user"] == from_id and relationships[i]["proposal"] == True:
            relationships[i]["proposal"] = False
            rel = {i:relationships[i]}
            ManageChats().change_relationships(chat_id, rel)
            if relationships[i]["user"] == from_id:
                return f"{from_name} отказался подтвердить брак с {relationships[i]['with_user']}"
            else:
                return f"{from_name} отказался подтвердить брак с {relationships[i]['user']}"
            

async def delete_marriage_func(message):
    chat_id = message.peer_id
    from_id = str(message.from_id)
    from_info = ManageUsers().get_user_by_id(from_id)
    from_name = from_info.first_name + " " + from_info.last_name
    from_chat_info = ManageChats().get_user(chat_id, from_id)
    married_with = from_chat_info[list(from_chat_info.keys())[0]]["married_with"]
    logging.info(f"User {message.from_id} use delete marriage in chat {chat_id}")
    if married_with == None:
        return "Вы не женаты"
    relationships = ManageChats().get_relationships(chat_id)
    for i in relationships:
        if relationships[i]["user"] == from_id or relationships[i]["with_user"] == from_id and relationships[i]["user"] == married_with or relationships[i]["with_user"] == married_with and relationships[i]["married"] == True:
            relationships[i]["proposal"] = False
            relationships[i]["married"] = False
            relationships[i]["history"].update({str(datetime.now()):{ "action": "Брак был отменен", "from": from_id}})
            rel = {i:relationships[i]}
            ManageChats().change_relationships(chat_id, rel)
            user = ManageChats().get_user(chat_id, relationships[i]["with_user"])
            user[list(user.keys())[0]]["married_with"] = None
            ManageChats().update_user(chat_id, user)
            user = ManageChats().get_user(chat_id, relationships[i]["user"])
            user[list(user.keys())[0]]["married_with"] = None
            ManageChats().update_user(chat_id, user)
            return f"Брак между {relationships[i]['with_user']} и {relationships[i]['user']} был расторгнут"


async def make_marriage_func(message, user_link, with_user_link):
    chat_id = message.peer_id
    from_id = message.from_id
    from_info = ManageUsers().get_user_by_id(from_id)
    from_name = from_info.first_name + " " + from_info.last_name
    user_info = ManageUsers().get_user_by_id(user_link.split("|")[0][3:])
    user_name = user_info.first_name + " " + user_info.last_name
    with_user_info = ManageUsers().get_user_by_id(with_user_link.split("|")[0][3:])
    with_user_name = with_user_info.first_name + " " + with_user_info.last_name
    user = ManageChats().get_user(chat_id, user_link.split("|")[0][3:])
    with_user = ManageChats().get_user(chat_id, with_user_link.split("|")[0][3:])
    logging.info(f"User {message.from_id} use make marriage in chat {chat_id}")
    if user[list(user.keys())[0]]["married_with"] != None:
        return f"{user_name} уже женат(a)"
    if with_user[list(with_user.keys())[0]]["married_with"] != None:
        return f"{with_user_name} уже женат(a)"
    relationships = ManageChats().get_relationships(chat_id)
    for i in relationships:
        if relationships[i]["user"] == user_info.user_id or relationships[i]["with_user"] == user_info.user_id and relationships[i]['user'] == with_user_info.user_id or relationships[i]["with_user"] == with_user_info.user_id:
            relationships[i]["proposal"] = False
            relationships[i]["married"] = True
            relationships[i]["history"].update({str(datetime.now()):{ "action": "Брак был подтвержден", "from": from_name}})
            rel = {i:relationships[i]}
            ManageChats().change_relationships(chat_id, rel)
            user = ManageChats().get_user(chat_id, relationships[i]["with_user"])
            user[list(user.keys())[0]]["married_with"] = relationships[i]["user"]
            ManageChats().update_user(chat_id, user)
            user = ManageChats().get_user(chat_id, relationships[i]["user"])
            user[list(user.keys())[0]]["married_with"] = relationships[i]["with_user"]
            ManageChats().update_user(chat_id, user)
            return f"{with_user_name} и {user_name} теперь женаты"
        
    count = ManageChats().get_relationship_count(chat_id)
    rel = {count:{"user": str(user_info.user_id),
                     "with_user": str(with_user_info.user_id),
                     "status": 1,
                     "hp": 0,
                     "start_date": str(datetime.now()),
                     "history": {str(datetime.now()):{ "action": "Брак был подтвержден", "from": from_name}},
                     "married": True,
                     "proposal": False}}
    ManageChats().add_relationships(chat_id, rel)
    return f"{with_user_name} и {user_name} теперь женаты"

async def divorce_marriage_func(message, user_link, with_user_link):
    chat_id = message.peer_id
    from_id = message.from_id
    from_info = ManageUsers().get_user_by_id(from_id)
    from_name = from_info.first_name + " " + from_info.last_name
    user_info = ManageUsers().get_user_by_id(user_link.split("|")[0][3:])
    user_name = user_info.first_name + " " + user_info.last_name
    with_user_info = ManageUsers().get_user_by_id(with_user_link.split("|")[0][3:])
    with_user_name = with_user_info.first_name + " " + with_user_info.last_name
    user = ManageChats().get_user(chat_id, user_link.split("|")[0][3:])
    with_user = ManageChats().get_user(chat_id, with_user_link.split("|")[0][3:])
    logging.info(f"User {message.from_id} use divorce marriage in chat {chat_id}")
    if user[list(user.keys())[0]]["married_with"] == None:
        return f"{user_name} не женат(a)"
    if with_user[list(with_user.keys())[0]]["married_with"] == None:
        return f"{with_user_name} не женат(a)"
    relationships = ManageChats().get_relationships(chat_id)
    for i in relationships:
        if relationships[i]["user"] == user_info["user_id"] or relationships[i]["with_user"] == user_info["user_id"] and relationships[i]['user'] == with_user_info["user_id"] or relationships[i]["with_user"] == with_user_info["user_id"]:
            relationships[i]["proposal"] = False
            relationships[i]["married"] = False
            relationships[i]["history"].update({str(datetime.now()):{ "action": "Брак был отменен", "from": from_name}})
            rel = {i:relationships[i]}
            ManageChats().change_relationships(chat_id, rel)
            user = ManageChats().get_user(chat_id, relationships[i]["with_user"])
            user[list(user.keys())[0]]["married_with"] = None
            ManageChats().update_user(chat_id, user)
            user = ManageChats().get_user(chat_id, relationships[i]["user"])
            user[list(user.keys())[0]]["married_with"] = None
            ManageChats().update_user(chat_id, user)
            return f"{with_user_name} и {user_name} теперь не женаты"
        
async def reset_marriages_func(message):
    chat_id = message.peer_id
    from_id = message.from_id
    from_info = ManageUsers().get_user_by_id(from_id)
    from_name = from_info.first_name + " " + from_info.last_name
    relationships = ManageChats().get_relationships(chat_id)
    for i in relationships:
        relationships[i]["proposal"] = False
        relationships[i]["married"] = False
        relationships[i]["history"].update({str(datetime.now()):{ "action": "Брак был отменен", "from": from_name}})
        rel = {i:relationships[i]}
        ManageChats().change_relationships(chat_id, rel)
    users = ManageChats().get_users(chat_id)
    for i in users:
        users[i]["married_with"] = None
        ManageChats().update_user(chat_id, users)
    logging.info(f"User {message.from_id} use reset marriages in chat {chat_id}")
    return "Список браков обнулён"

async def make_breakfast_func(message, text):
    chat_id = message.peer_id
    from_id = message.from_id
    with_id = message.text.split(" ")[3][3:]
    from_info = ManageUsers().get_user_by_id(from_id)
    from_name = from_info.first_name + " " + from_info.last_name
    with_info = ManageUsers().get_user_by_id(with_id)
    with_name = with_info.first_name + " " + with_info.last_name
    logging.info(f"User {message.from_id} use make breakfast in chat {chat_id}")
    relationship = ManageChats().get_relationships(chat_id)
    for i in relationship:
        if (relationship[i]["user"] == from_id or relationship[i]["with_user"] == from_id) and (relationship[i]['user'] == with_id or relationship[i]["with_user"] == with_id):
            user = ManageChats().get_user(chat_id, from_id)
            if user[list(user.keys())[0]]["relationship_cd"] > datetime.now() or user[list(user.keys())[0]]["relationship_cd"] == None:
                relationship[i]["hp"] += 100
                relationship[i]["history"].update({str(datetime.now()):{ "action": "Сделал завтрак", "from": from_name}})
                rel = {i:relationship[i]}
                ManageChats().change_relationships(chat_id, rel)
                user = ManageChats().get_user(chat_id, from_id)
                user[list(user.keys())[0]]["relationship_cd"] = str(datetime.now() + timedelta(minutes=120))
                return f"{from_name} сделали завтрак для {with_name} (+100 hp)"
            else:
                return f"{from_name} не может сделать завтрак, т.к. необходимо сделать отдых"
            
    
async def relationship_action_func(message, action_text, hp_increase, cooldown_duration, cost=None):
    chat_id = message.peer_id
    initiator_id = message.from_id
    target_id = extract_target_id(message.text)
    
    initiator_info = ManageUsers().get_user_by_id(initiator_id)
    initiator_name = f"{initiator_info.first_name} {initiator_info.last_name}"
    
    target_info = ManageUsers().get_user_by_id(target_id)
    target_name = f"{target_info.first_name} {target_info.last_name}"
    
    logging.info(f"User {initiator_id} initiated action '{action_text}' in chat {chat_id}")
    relationships = ManageChats().get_relationships(chat_id)

    if cost is not None and initiator_info.money > cost:
        ManageUsers().reduce_user_coins(initiator_id, cost)
    
    for relationship_id, relationship_data in relationships.items():
        if (relationship_data["user"] == str(initiator_id) or relationship_data["with_user"] == str(initiator_id)) and \
           (relationship_data['user'] == str(target_id) or relationship_data["with_user"] == str(target_id)):
            user_data = ManageChats().get_user(chat_id, initiator_id)
            cooldown_time = user_data[list(user_data.keys())[0]]["relationship_cd"]
            
            if cost is not None or cooldown_time is None or datetime.strptime(cooldown_time, "%Y-%m-%d %H:%M:%S.%f") < datetime.now():
                relationship_data["hp"] += hp_increase
                relationship_data["history"].update({str(datetime.now()): {"action": action_text, "from": initiator_name}})
                ManageChats().change_relationships(chat_id, {relationship_id: relationship_data})
                
                user_data[list(user_data.keys())[0]]["relationship_cd"] = str(datetime.now() + timedelta(minutes=cooldown_duration))
                ManageChats().update_user(chat_id, user_data)
                
                return f"{initiator_name} performed action '{action_text}' for {target_name} (+{hp_increase} hp)"
            else:
                return f"{initiator_name} cannot perform action due to cooldown requirements"

def extract_target_id(message_text):
    parts = message_text.split(" ")
    if len(parts) == 4:
        return parts[3].split("|")[0][3:]
    elif len(parts) == 5:
        return parts[4].split("|")[0][3:]
    else:
        return parts[2].split("|")[0][3:]

