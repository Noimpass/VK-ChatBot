from vkbottle.bot import BotLabeler, Message, rules
from vkbottle_types.objects import MessagesConversation
from handlers.rule import RankRule
from handlers.utils import *
from config import group_api

chat_labeler = BotLabeler()
chat_labeler.vbml_ignore_case = True
chat_labeler.custom_rules["rank_filter"] = RankRule

async def get_users_names(first, second):
    first = await group_api.users.get(user_ids=first)
    first_name = first[0].first_name + " " + first[0].last_name
    second = await group_api.users.get(user_ids=second)
    if second == []:
        return [first_name, "group"]
    second_name = second[0].first_name + " " + second[0].last_name
    return [first_name, second_name]

@chat_labeler.message(text=["пожать руку <user_link>","пожать руку"])
async def shake_hands(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id) 
    await message.answer(f"{user_names[0]} пожал(a) руку {user_names[1]}")

@chat_labeler.message(text=["обнять <user_link>","обнять"])
async def hug(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} обнял(a) {user_names[1]}")

@chat_labeler.message(text=["куснуть <user_link>","куснуть"])
async def bite_small(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} куснул(a) {user_names[1]}")

@chat_labeler.message(text=["укусить <user_link>","укусить"])
async def bite_big(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} укусил(a) {user_names[1]}")

@chat_labeler.message(text=["лизнуть <user_link>","лизнуть"])
async def lick(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} лизнул(a) {user_names[1]}")

@chat_labeler.message(text=["убить <user_link>","убить"])
async def kill(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} убил(a) {user_names[1]}")

@chat_labeler.message(text=["сжечь <user_link>","сжечь"])
async def burn(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} сжёг {user_names[1]}")

@chat_labeler.message(text=["ударить <user_link>","ударить"])
async def hit(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} ударил(a) {user_names[1]}")

@chat_labeler.message(text=["уебать <user_link>","уебать"])
async def hit_hard(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} уебал(a) {user_names[1]}")

@chat_labeler.message(text=["трахнуть <user_link>","трахнуть"])
async def bonk(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} трахнул(a) {user_names[1]}")

@chat_labeler.message(text=["выебать <user_link>","выебать"])
async def scold(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} выебал(a) {user_names[1]}")

@chat_labeler.message(text=["изнасиловать <user_link>","изнасиловать"])
async def rape(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} изнасиловал(a) {user_names[1]}")

@chat_labeler.message(text=["погладить <user_link>","погладить"])
async def pat(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} погладил(a) {user_names[1]}")

@chat_labeler.message(text=["шлёпнуть <user_link>","шлёпнуть"])
async def slap(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} шлёпнул(a) {user_names[1]}")

@chat_labeler.message(text=["отдаться <user_link>","отдаться"])
async def give(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} отдал(ся/aсь) {user_names[1]}")

@chat_labeler.message(text=["расстрелять <user_link>","расстрелять"])
async def shoot(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} расстрелял(a) {user_names[1]}")

@chat_labeler.message(text=["кастрировать <user_link>","кастрировать"])
async def castrate(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} кастрировал(a) {user_names[1]}")

@chat_labeler.message(text=["пнуть <user_link>","пнуть"])
async def punch(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} пнул(a) {user_names[1]}")

@chat_labeler.message(text=["потрогать <user_link>","потрогать"])
async def spank(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} потрогал(a) {user_names[1]}")

@chat_labeler.message(text=["похвалить <user_link>","похвалить"])
async def praise(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} похвалил(a) {user_names[1]}")

@chat_labeler.message(text=["поздравить <user_link>","поздравить"])
async def congratulate(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} поздравил(a) {user_names[1]}")

@chat_labeler.message(text=["поцеловать <user_link>","поцеловать"])
async def kiss(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} поцеловал(a) {user_names[1]}")

@chat_labeler.message(text=["послать нахуй <user_link>","послать нахуй"])
async def fuck_it(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} послал(а) {user_names[1]}")

@chat_labeler.message(text=["делать секс <user_link>","делать секс"])
async def sex(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} делал(а) секс {user_names[1]}")

@chat_labeler.message(text=["понюхать <user_link>","понюхать"])
async def sniff(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} понюхал(a) {user_names[1]}")

@chat_labeler.message(text=["ущипнуть <user_link>","ущипнуть"])
async def pinch(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} ущипнул(a) {user_names[1]}")

@chat_labeler.message(text=["сделать кусь <user_link>","сделать кусь"])
async def scratch(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} сделал(а) кусь {user_names[1]}")

@chat_labeler.message(text=["покормить <user_link>","покормить"])
async def feed(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} покормил(a) {user_names[1]}")

@chat_labeler.message(text=["записать на ноготочки <user_link>","записать на ноготочки"])
async def record_nose(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} записал(а) на ноготочки {user_names[1]}")

@chat_labeler.message(text=["пригласить на чай <user_link>","пригласить на чай"])
async def invite_to_party(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} пригласил(а) {user_names[1]} на чай")

@chat_labeler.message(text=["отравить <user_link>","отравить"])
async def poison(message: Message):
    user_names = await get_users_names(message.from_id, message.reply_message.from_id)
    await message.answer(f"{user_names[0]} отравил(а) {user_names[1]}")