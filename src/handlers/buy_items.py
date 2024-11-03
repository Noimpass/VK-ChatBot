from vkbottle.bot import BotLabeler, Message, rules
from vkbottle_types.objects import MessagesConversation
from handlers.rule import RankRule
from db.dataspace import ManageUsers, ManageChats
from config import group_api

chat_labeler = BotLabeler()
chat_labeler.vbml_ignore_case = True

@chat_labeler.message(text=["купить банхаммер"])
async def buy_banhammer(message: Message):
    chat_id = message.peer_id
    chat_settings = ManageChats().get_settings(chat_id)
    price = chat_settings["item_price"]["banhammer"]
    user = ManageUsers().get_user(message.from_id)
    if user is None:
        return
    if user.money < float(price):
        await message.answer("Недостаточно средств" )
        return
    ManageUsers().reduce_user_money(message.from_id, price)
    inventory = ManageChats().get_user_inventory(chat_id, message.from_id)
    inventory["banhammer"] += 1
    ManageChats().add_inventory_item(chat_id, message.from_id, "banhammer", 1)
    ManageChats().add_money_group(chat_id, int(price) * 0.4)
    await message.answer("Вы купили банхаммер" )

@chat_labeler.message(text=["купить плюсопад"])
async def buy_pluspad(message: Message):
    chat_id = message.peer_id
    chat_settings = ManageChats().get_settings(chat_id)
    price = chat_settings["item_price"]["pluspad"]
    user = ManageUsers().get_user(message.from_id)
    if user is None:
        return
    if user.money < float(price):
        await message.answer("Недостаточно средств" )
        return
    ManageUsers().reduce_user_money(message.from_id, price)
    inventory = ManageChats().get_user_inventory(chat_id, message.from_id)
    inventory["pluspad"] += 1
    ManageChats().add_inventory_item(chat_id, message.from_id, "pluspad", 1)
    ManageChats().add_money_group(chat_id, int(price) * 0.4)
    await message.answer("Вы купили плюсопад" )

@chat_labeler.message(text=["купить минусит"])
async def buy_minusit(message: Message):
    chat_id = message.peer_id
    chat_settings = ManageChats().get_settings(chat_id)
    price = chat_settings["item_price"]["minusit"]
    user = ManageUsers().get_user(message.from_id)
    if user is None:
        return
    if user.money < float(price):
        await message.answer("Недостаточно средств" )
        return
    ManageUsers().reduce_user_money(message.from_id, price)
    inventory = ManageChats().get_user_inventory(chat_id, message.from_id)
    inventory["minusit"] += 1
    ManageChats().add_inventory_item(chat_id, message.from_id, "minusit", 1)
    ManageChats().add_money_group(chat_id, int(price) * 0.4)
    await message.answer("Вы купили минусит")

@chat_labeler.message(text=["купить коины <count>"])
async def buy_coins(message: Message, count: int):
    chat_id = message.peer_id
    chat_settings = ManageChats().get_settings(chat_id)
    price = count
    user = ManageUsers().get_user(message.from_id)
    if user is None:
        return
    if user.money < float(price):
        await message.answer("Недостаточно средств")
        return
    ManageUsers().reduce_user_money(message.from_id, price)
    ManageUsers().add_user_coins(message.from_id, int(price) * 100)
    ManageChats().add_money_group(chat_id, int(price) * 0.4)
    await message.answer(f"Вы купили {int(price) * 100} коинов")

@chat_labeler.message(text=["купить анонимка"])
async def buy_anon(message: Message):
    chat_id = message.peer_id
    chat_settings = ManageChats().get_settings(chat_id)
    price = chat_settings["item_price"]["anon"]
    user = ManageUsers().get_user(message.from_id)
    if user is None:
        return
    if user.money < float(price):
        await message.answer("Недостаточно средств" )
        return
    ManageUsers().reduce_user_money(message.from_id, price)
    inventory = ManageChats().get_user_inventory(chat_id, message.from_id)
    inventory["anon"] += 1
    ManageChats().add_inventory_item(chat_id, message.from_id, "anon", 1)
    ManageChats().add_money_group(chat_id, int(price) * 0.4)
    await message.answer("Вы купили анонимку")

@chat_labeler.message(text=["кубышка в ириски"])
async def get_money_to_owner(message: Message):
    chat_id = message.peer_id
    chat = ManageChats().get_chat(chat_id)
    user = ManageUsers().get_user(message.from_id)
    if message.from_id == chat.owner:
        amount = ManageChats().money_to_owner(chat_id)
        ManageUsers().add_user_money(message.from_id, amount)
        await message.answer(f"Выведенно {amount}" )

@chat_labeler.message(text=["купить звёзды <count>", "купить звезды <count>"])
async def buy_stars(message: Message, count: int):
    chat_id = message.peer_id
    chat_settings = ManageChats().get_settings(chat_id)
    price = count
    user = ManageUsers().get_user(message.from_id)
    if user is None:
        return
    if user.money < float(price):
        await message.answer("Недостаточно средств" )
        return
    ManageUsers().reduce_user_money(message.from_id, price)
    ManageUsers().add_user_stars(message.from_id, int(count) * 10)
    ManageChats().add_money_group(chat_id, int(count) * 0.4)
    await message.answer(f"Вы купили {int(count) * 10} звёзд" )

@chat_labeler.message(text=["купить ириски <count>"])
async def buy_iris(message: Message, count: float):
    chat_id = message.peer_id
    ManageUsers().add_user_money(message.from_id, float(count))
    await message.answer(f"В разработке. (Добавлено {count})")

