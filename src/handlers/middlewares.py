from vkbottle import BaseMiddleware
from vkbottle.bot import Message
from db.dataspace import ManageChats
from vkbottle import API
from .utils import get_chat_members, add_chat
from config import group_api

import logging


# class RegisterChatMiddleware(BaseMiddleware[Message]):
#     async def pre(self):
#         logging.info(f"middleware pre check for chat {self.event.peer_id}")
#         if self.event.peer_id == self.event.from_id:
#             return

#         logging.info(f"Checking chat {self.event.peer_id}")
#         is_chat_exists = ManageChats().get_chat(self.event.from_id)
#         if is_chat_exists:
#             logging.info(f"Chat {self.event.peer_id} exists in database")
#             return

#         logging.info(f"Check chat {self.event.peer_id} members")
#         chat_members = await get_chat_members(group_api, self.event.peer_id)
#         logging.info(f"Chat {self.event.peer_id} doesn't exist in database, updating")
#         await add_chat(chat_id=self.event.peer_id, chat_members=chat_members)