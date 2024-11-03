from vkbottle.bot import BotLabeler, Message, MessageEvent
from config import group_api, VK_GROUP_ID
from db.dataspace import ManageAntiSpam, ManageChats, Users, ManageUsers
from datetime import datetime
from handlers.capcha import *
from handlers.stock_market import stock_market
import logging
import re

bl = BotLabeler()
bl.vbml_ignore_case = True

@bl.raw_event(event="message_new")
async def on_new_message(event: MessageEvent):
    message = event["object"]["message"]
    if message["from_id"] == -VK_GROUP_ID:
        return
    if message["peer_id"] == message["from_id"]:
        if message["text"] == "капча":
            await capcha(message)
        if message["text"].split(" ")[0] == "биржа":
            await stock_market(message)
        return

    logging.info(f"New message from {message['from_id']} in {message['peer_id']} - {message['text']}")

    user = ManageChats().get_user(chat_id=message["peer_id"], user_id=message["from_id"])
    user_self = ManageUsers().get_user_by_id(message["from_id"])
    if user_self == None:
        user_info = await group_api.users.get(user_ids=message["from_id"])
        username = user_info[0].screen_name
        user_self = Users(user_id = message["from_id"],
                username = username,
                first_name = user_info[0].first_name,
                last_name = user_info[0].last_name,
                money = 0,
                coins = 0,
                reputation = 0,
                reputation_self = 0,
                chats = {message["peer_id"]: {"last_msg": None, "added": str(datetime.fromtimestamp(message["date"])), "msg_count": 0}},
                bans = {},
                stock_list = {},
                gold = 0
                )
        ManageUsers().add_user(user_self)


    if user[list(user.keys())[0]]["capcha"] == False:
        await group_api.messages.delete(cmids=message["conversation_message_id"],peer_id=message["peer_id"], delete_for_all=1)

    punished = ManageChats().get_punished(message["peer_id"])
    for punish in punished:
        if punish == str(message["from_id"]) and punished[punish]['punishment'] == "mute":
            await group_api.messages.delete(cmids=message["conversation_message_id"],peer_id=message["peer_id"], delete_for_all=1)
            logging.info(f"Delete message from {list(user.keys())[0]} in {message['peer_id']} by mute - {message['text']}")
            return
        
    chat_settings = ManageChats().get_settings(message["peer_id"])
        
    if chat_settings["site_link"] == True:
        text = message["text"]
        if re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text):
            await group_api.messages.delete(cmids=message["conversation_message_id"],peer_id=message["peer_id"], delete_for_all=1)
            logging.info(f"Delete message from {list(user.keys())[0]} in {message['peer_id']} by site link - {message['text']}")
            return
        
    if chat_settings["chat_link"] == True:
        if re.match(r"^https://vk\.me/join/", message.text):
            await group_api.messages.delete(cmids=message["conversation_message_id"],peer_id=message["peer_id"], delete_for_all=1)
            logging.info(f"Delete message from {list(user.keys())[0]} in {message['peer_id']} by chat link - {message['text']}")
            return
        
    
        
    if user != None:
        user[list(user.keys())[0]]["msgs"].append([str(datetime.fromtimestamp(message["date"])), message["text"]])
        user[list(user.keys())[0]]["msg_count"] += 1
        user[list(user.keys())[0]]["last_msg"] = str(datetime.fromtimestamp(message["date"]))
        ManageChats().update_user(message["peer_id"], user)

