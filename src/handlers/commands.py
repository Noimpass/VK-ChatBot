from vkbottle.bot import BotLabeler, Message, rules
from vkbottle_types.objects import MessagesConversation
from handlers.rule import RankRule
from handlers.utils import *
from config import group_api
    
chat_labeler = BotLabeler()
chat_labeler.vbml_ignore_case = True
chat_labeler.custom_rules["rank_filter"] = RankRule
duel_users = {}

@chat_labeler.message(text=["/start"])
async def start(message: Message):
    members = await get_chat_members(group_api, message.peer_id)
    if members is None:
        await message.answer("Нет прав администратора")
        return
    is_chat_exists = await add_chat(chat_id=message.peer_id, chat_members=members)
    if is_chat_exists:
        await message.answer("Бот уже запущен")
        return

    await message.answer("Бот запущен")

@chat_labeler.message(text=["повысить <user_link>"], rank_filter=5)
async def promote_moder(message: Message, user_link):
    response = await promote_staff(message, user_link)
    await message.answer(f"{user_link} {response}")

@chat_labeler.message(text=["понизить <user_link>"], rank_filter=5)
async def demote_moder(message: Message, user_link):
    response = await demote_staff(message, user_link)
    await message.answer(f"{user_link} {response}")

@chat_labeler.message(text=["исключить модера <user_link>"], rank_filter=5)
async def remove_moder(message: Message, user_link):
    response = await remove_staff(message, user_link)
    await message.answer(f"{user_link} {response}")

@chat_labeler.message(text=["!staff", "!админы", "!упарвляющие","!admins"])
async def get_moders(message: Message):
    names = ""
    response = await get_admins(message)
    for i in range(len(response)):
        names += str(f"{response[i][0]} - {response[i][1]}\n")
    await message.answer(names)

@chat_labeler.message(text=["позвать модеров", "позвать админов"])
async def call_moders(message: Message):
    names = ""
    response = await get_admins(message)
    for i in range(len(response)):
        names += str(f"[id{response[i][2]}|{response[i][0]}] ")
    await message.answer(names)

#========================Warn========================

@chat_labeler.message(text=["варн <user_link> <reason>", "варн <reason>"], rank_filter="warn")
async def warning_user(message: Message, user_link: str | None = None, reason: str | None = None):
    response = await warn_user(message, user_link, reason)
    await message.answer(f"{response}")

@chat_labeler.message(text=["снять варны <count> <user_link>", "снять варны <user_link>"], rank_filter="warn")
async def remove_warnings(message: Message, user_link: str | None = None, count: str | None = None):
    response = await remove_warnings_user(message, user_link, count)
    await message.answer(f"{response}")

@chat_labeler.message(text=["варны <user_link>", "варны"], rank_filter="warn")
async def get_warnings(message: Message, user_link: str | None = None):
    response = await get_warn(message, user_link)
    msg = ""
    for i in range(len(response)):
        msg += str(f"{i+1} - Предупреждение получено: {response[i][0]}\nДо: {response[i][1]}\nПричина: {response[i][2]}\n")
    await message.answer(msg)

@chat_labeler.message(text=["мут <time> <user_link>", "мут <time>"], rank_filter="mute")
async def mute_user(message: Message, user_link: str | None = None, time: str | None = None):
    response = await mute_user_func(message, user_link, time)
    await message.answer(f"{response}")

#=========================Команды банов=========================

@chat_labeler.message(text=["банлист"], rank_filter=1)
async def banlist(message: Message):
    response = await get_banlist(message)
    if response == []:
        return await message.answer("Список банов пуст")
    msg = ""
    for i in range(len(response)):
        msg += str(f"{i+1} - {response[i][0]}\nВремя бана: {response[i][1]}\nДо: {response[i][2]}\nПричина: {response[i][3]}\nКто выдал: {response[i][4]}\nРанк админа: {response[i][5]}\n")
    await message.answer(msg)

@chat_labeler.message(text=["!амнистия"], rank_filter=5)
async def amnistia(message: Message):
    response = await get_amnistia(message)
    await message.answer(response)

@chat_labeler.message(text=["!снимаю полномочия"], rank_filter=1)
async def remove_powers(message: Message):
    response = await remove_power(message)
    await message.answer(response)
    
@chat_labeler.message(text=["восстановить создателя"])
async def restore_owner(message: Message):
    chat_owner = ManageChats().get_chat_owner(message.peer_id)
    if message.from_id == chat_owner:
        response = await resotre_owner_rank(message)
        await message.answer(response)

@chat_labeler.message(text=["!ban <user_pointer> <reason> <time>","забанить <user_pointer> <resaon> <time>","чс <user_pointer> <reason> <time>"], rank_filter=3)
async def ban_user(message: Message, user_pointer: str | None = None, reason: str | None = None, time: str | None = None):
    response = await ban_user_func(message, user_pointer, reason, time)
    await message.answer(response)

@chat_labeler.message(text=["!unban <user_pointer>","вернуть <user_pointer>"])
async def unban_user(message: Message, user_pointer: str | None = None):
    response = await unban_user_func(message, user_pointer)
    await message.answer(response)

@chat_labeler.message(text=["причина <user_link>"], rank_filter=1)
async def get_reason(message: Message, user_link: str | None = None):
    response = await get_reason_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["кикнуть <user_link>", "кикнуть", "кик <user_link>", "кик", "kick <user_link>", "kick"], rank_filter="kick")
async def kick_user(message: Message, user_link: str | None = None):
    if user_link == "собак":
        await kick_dogs(message)
        return
    elif user_link == "молчунов":
        await kick_molch(message)
        return
    elif user_link.split(" ")[0] == "новичков":
        await kick_newcomers(message, user_link.split(" ")[1])
        return
    elif user_link.split(" ")[0] == "от":
        await kick_by_user(message, user_link.split(" ")[1])
        return
    response = await kick_user_func(message, user_link)
    await message.answer(response)

#============================Чистка беседы=============================

@chat_labeler.message(text=["кик новичков <time>"], rank_filter="kick")
async def kick_newcomers(message: Message, time: str | None = None):
    response = await kick_newcomers_func(message, time)
    await message.answer(response)

@chat_labeler.message(text=["кик собак"], rank_filter="kick")
async def kick_dogs(message: Message):
    response = await kick_dogs_func(message)
    await message.answer(response)

@chat_labeler.message(text=["кик от <user_link>"], rank_filter="kick")
async def kick_by_user(message: Message, user_link: str | None = None):
    response = await kick_by_user_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["кик молчунов <time>"], rank_filter="kick")
async def kick_molch(message: Message, time: str | None = None):
    response = await kick_molch_func(message, time)
    await message.answer(response)

@chat_labeler.message(text=["кик по смс <count> <time>", "кик по смс <count>", "кик по сообщениям <count> <time>", "кик по сообщениям <count>"], rank_filter="kick")
async def kick_by_messages(message: Message, count: str | None = None, time: str | None = None):
    response = await kick_by_messages_func(message, count, time)
    await message.answer(response)

#============================Темы модераторов=============================

@chat_labeler.message(text=["модераторы названия"])
async def moder_name(message: Message):
    response = await moder_name_func(message)
    await message.answer(response)

@chat_labeler.message(text=["модераторы названия <text>"], rank_filter=5)
async def set_moder_name(message: Message, text: str | None = None):
    response = await set_moder_name_func(message, text)
    await message.answer(response)

#============================Настройка беседы=============================

# @chat_labeler.message(text=["чат-ссылка <link>", "/link <link>"], rank_filter=5)
# async def change_link(message: Message, link: str | None = None):
#     response = await change_link_func(message, link)
#     await message.answer(response)

@chat_labeler.message(text=["правила"])
async def get_rules(message: Message):
    response = await get_rules_func(message)
    if response is "":
        response = "Правила отсутствуют"
    await message.answer(response)

@chat_labeler.message(text=["правила <text>"], rank_filter=5)
async def set_rules(message: Message, text: str | None = None):
    response = await set_rules_func(message, text)
    await message.answer(response)

@chat_labeler.message(text=["удалить правила"], rank_filter=5)
async def delete_rules(message: Message):
    response = await delete_rules_func(message)
    await message.answer(response)

@chat_labeler.message(text=["приветствие <text>"], rank_filter=5)
async def set_welcome(message: Message, text: str | None = None):
    response = await set_welcome_func(message, text)
    await message.answer(response)

@chat_labeler.message(text=["удалить приветствие"], rank_filter=5)
async def delete_welcome(message: Message):
    response = await delete_welcome_func(message)
    await message.answer(response)

@chat_labeler.message(text=["ивайты <count>"], rank_filter=5)
async def set_invite_count(message: Message, count: str | None = None):
    response = await set_invite_count_func(message, count)
    await message.answer(response)

@chat_labeler.message(text=["антирейд <count>"], rank_filter=5)
async def set_antiraid(message: Message, count: str | None = None):
    response = await set_antiraid_func(message, count)
    await message.answer(response)

@chat_labeler.message(text=["+чп","чп 1"], rank_filter=5)
async def set_emergency_on(message: Message):
    response = await set_emergency_on_func(message)
    await message.answer(response)

@chat_labeler.message(text=["-чп","чп 0"], rank_filter=5)
async def set_emergency_off(message: Message):
    response = await set_emergency_off_func(message)
    await message.answer(response)

@chat_labeler.message(text=["+беседы","беседы 1"], rank_filter=5)
async def set_chat_filter_on(message: Message):
    response = await set_chat_filter_on_func(message)
    await message.answer(response)

@chat_labeler.message(text=["-беседы","беседы 0"], rank_filter=5)
async def set_chat_filter_off(message: Message):
    response = await set_chat_filter_off_func(message)
    await message.answer(response)

@chat_labeler.message(text=["+сайты","сайты 1"], rank_filter=5)
async def set_site_filter_on(message: Message):
    response = await set_site_filter_on_func(message)
    await message.answer(response)

@chat_labeler.message(text=["-сайты","сайты 0"], rank_filter=5)
async def set_site_filter_off(message: Message):
    response = await set_site_filter_off_func(message)
    await message.answer(response)

@chat_labeler.message(text=["+группы","группы 1"], rank_filter=5)
async def set_group_filter_on(message: Message):
    response = await set_group_filter_on_func(message)
    await message.answer(response)

@chat_labeler.message(text=["-группы","группы 0"], rank_filter=5)
async def set_group_filter_off(message: Message):
    response = await set_group_filter_off_func(message)
    await message.answer(response)

@chat_labeler.message(text=["+инвайты","инвайты 1"], rank_filter=5)
async def set_invite_filter_on(message: Message):
    response = await set_invite_filter_on_func(message)
    await message.answer(response)

@chat_labeler.message(text=["-инвайты","инвайты 0"], rank_filter=5)
async def set_invite_filter_off(message: Message):
    response = await set_invite_filter_off_func(message)
    await message.answer(response)

#============================Развлекательные команды=============================

@chat_labeler.message(text=["!рулетка", "!русская рулетка"])
async def russian_roulette(message: Message):
    response = await russian_roulette_func(message)
    await message.answer(response)

@chat_labeler.message(text=["погода <city>"])
async def weather(message: Message, city: str | None = None):
    response = await weather_func(message, city)
    await message.answer(response)

@chat_labeler.message(text=["рандом <min> <max>", "рандом <min>"])
async def random_number(message: Message, min: str | None = None, max: str | None = None):
    response = await random_number_func(message, min, max)
    await message.answer(response)

@chat_labeler.message(text=["Ирис выбери <first> или <second>"])
async def choose(message: Message, first: str | None = None, second: str | None = None):
    response = await choose_func(message, first, second)
    await message.answer(response)

@chat_labeler.message(text=["Ирис данет <text>"])
async def choose_text(message: Message, text: str | None = None):
    response = await choose_text_func(message, text)
    await message.answer(response)

#============================Команды для покупок=============================

@chat_labeler.message(text=["анонимка"])
async def anonymous(message: Message):
    response = await anonymous_func(message)
    await message.answer(response)

@chat_labeler.message(text=["анонимка <domain> <text>"])
async def anonymous_message(message: Message, domain: str | None = None, text: str | None = None):
    response = await anonymous_message_func(message, domain, text)
    await message.answer(response)

@chat_labeler.message(text=["!домен <domain>"])
async def domain(message: Message, domain: str | None = None):
    response = await domain_func(message, domain)
    await message.answer(response)

@chat_labeler.message(text=["передать <amount> <user_link>", "передать <amount>"])
async def transfer(message: Message, amount: str | None = None, user_link: str | None = None):
    response = await transfer_func(message, amount, user_link)
    await message.answer(response)

@chat_labeler.message(text=["мешок"])
async def bag(message: Message):
    response = await bag_func(message)
    await message.answer(response)

@chat_labeler.message(text=["мешок <user_link>"])
async def bag_user(message: Message, user_link: str | None = None):
    response = await bag_user_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["баланс"])
async def balance(message: Message):
    response = await balance_func(message)
    user_id = message.from_id
    user_info = await group_api.users.get(user_ids=user_id)
    user_name = user_info[0].first_name + " " + user_info[0].last_name
    msg = f"Баланс {user_name}:\n {response[0]} Ирисок, {response[1]} Монет, {response[2]} Звёздочек\nРепутация: {response[3]}\nИрис-голд: {response[4]}"
    await message.answer(msg)

@chat_labeler.message(text=["+мешок"])
async def open_bag(message: Message):
    response = await open_bag_func(message)
    await message.answer(response)

@chat_labeler.message(text=["-мешок"])
async def close_bag(message: Message):
    response = await close_bag_func(message)
    await message.answer(response)

@chat_labeler.message(text=["применить банхаммер <user_link>"])
async def banhammer(message: Message, user_link: str | None = None):
    response = await banhammer_ban_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["использовать плюсопад"])
async def plusopad(message: Message):
    response = await plusopad_func(message)
    await message.answer(response)

@chat_labeler.message(text=["использовать минусит"])
async def minusit(message: Message):
    response = await minusit_func(message)
    await message.answer(response)

#============================Анкета пользователя=============================

@chat_labeler.message(text=["кто я"])
async def whoami(message: Message):
    response = await whoami_func(message)
    await message.answer(response)

@chat_labeler.message(text=["кто ты <user_link>"])
async def whoami_user(message: Message, user_link: str | None = None):
    response = await whoami_user_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["о себе <text>"])
async def about_me(message: Message, text: str | None = None):
    response = await about_me_func(message, text)
    await message.answer(response)

@chat_labeler.message(text=["описание <user_link>"])
async def about_me_user(message: Message, user_link: str | None = None):
    response = await about_me_user_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["награды <user_link>"])
async def user_rewards(message: Message, user_link: str | None = None):
    response = await user_rewards_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["ник <nick>"])
async def user_nickname(message: Message, nick: str | None = None):
    response = await user_nickname_func(message, nick)
    await message.answer(response)

@chat_labeler.message(text=["ник удалить"])
async def delete_nickname(message: Message):
    response = await delete_nickname_func(message)
    await message.answer(response)

@chat_labeler.message(text=["звание <text>"])
async def user_title(message: Message, text: str | None = None):
    response = await user_title_func(message, text)
    await message.answer(response)

@chat_labeler.message(text=["звание удалить"])
async def delete_title(message: Message):
    response = await delete_title_func(message)
    await message.answer(response)

@chat_labeler.message(text=["мои кружки"])
async def show_factions(message: Message):
    response = await show_user_factions_func(message)
    if response == []:
        await message.answer("Нет кружков")
        return
    msg = ""
    for i in range(len(response)):
        msg = msg + f"{i+1}. {response[i]} \n"
    await message.answer(msg)

@chat_labeler.message(text=["мои кланы"])
async def show_clans(message: Message):
    response = await show_user_clan_func(message)
    if response == []:
        await message.answer("Нет кланов")
        return
    await message.answer(response)


#============================Статистическая информация=============================

@chat_labeler.message(text=["чат инфо"])
async def chat_info(message: Message):
    response = await chat_info_func(message)
    msg = (f"Правила канала - {response.settings['rules']}\n"
          f"Домен - {response.settings['domain']}\n"
          f"Сетка группы - {response.settings['chat_grid']}\n"
          f"Сыллки на чаты - {response.settings['chat_link']}\n"
          f"Ссылки на сайты - {response.settings['site_link']}\n"
          f"Cсылки на группы - {response.settings['group_link']}\n"
          f"Приглашение ботов - {response.settings['invite_link']}\n"
          f"Приветвенное сообщение - {response.settings['greeting_msg']}\n"
          f"Антирейд - {response.settings['emergency']}\n"
          f"Кик пользователей из списка antispam - {response.settings['antispam_auto']}\n"
          f"Цена на предметы - {response.settings['item_price']}\n")
    await message.answer(msg)

@chat_labeler.message(text=["стата <time>"])
async def chat_stats(message: Message, time: str | None = None):
    response = await chat_stats_func(message, time)
    msg = ""
    print(response)
    response.sort(key=lambda x: x[1], reverse=True)
    for i in response:
        msg = msg + f"{i[0]} - {i[1]} \n"
    await message.answer(msg)

@chat_labeler.message(text=["олды"])
async def old_members(message: Message):
    response = await old_members_func(message)
    if response == []:
        await message.answer("Нет старых пользователей")
        return
    msg = ""
    for i in response:
        msg = msg + f"[id{i[0]}|{i[1]}], "
    await message.answer(msg, disable_mentions=True)

@chat_labeler.message(text=["новички"])
async def new_members(message: Message):
    response = await new_members_func(message)
    if response == []:
        await message.answer("Нет новых пользователей")
        return
    msg = ""
    for i in response:
        msg = msg + f"[id{i[0]}|{i[1]}], "
    await message.answer(msg, disable_mentions=True)


@chat_labeler.message(text=["кто онлайн"])
async def online_members(message: Message):
    response = await online_members_func(message)
    if response == []:
        await message.answer("Нет онлайн пользователей")
        return
    msg = ""
    for i in response:
        msg = msg + f"[id{i[0]}|{i[1]}], "
    await message.answer(msg, disable_mentions=True)
    
@chat_labeler.message(text=["мои баны"])
async def my_bans(message: Message):
    response = await my_bans_func(message)
    await message.answer(response)

@chat_labeler.message(text=["кто меня добавил"])
async def who_added_me(message: Message):
    response = await who_added_me_func(message)
    user_info = ManageUsers().get_user_by_id(response)
    user_name = user_info.first_name + " " + user_info.last_name
    await message.answer(f"[id{response}|{user_name}]", disable_mentions=True)

@chat_labeler.message(text=["кто добавил <user_link>"])
async def who_added_user(message: Message, user_link: str | None = None):
    response = await who_added_user_func(message, user_link)
    user_info = ManageUsers().get_user_by_id(response)
    user_name = user_info.first_name + " " + user_info.last_name
    await message.answer(f"[id{response}|{user_name}]", disable_mentions=True)

#============================Модуль «Репутация»=============================

@chat_labeler.message(text=["рейтинг"])
async def rating(message: Message):
    response = await rating_func(message)
    response.sort(key=lambda x: x[1], reverse=True)
    msg = ""
    for i in range(len(response)):
        msg = msg + f"{i+1}. {response[i][0]} - {response[i][1]} \n"
    await message.answer(msg)

@chat_labeler.message(text=["+<amount>"])
async def add_rating(message: Message, amount: int | None = None):
    response = await add_rating_func(message, amount)
    await message.answer(response)

@chat_labeler.message(text=["-<amount>"])
async def reduce_rating(message: Message, amount: int | None = None):
    response = await reduce_rating_func(message, amount)
    await message.answer(response)

@chat_labeler.message(text=["*<amount>"])
async def add_star_rating(message: Message, amount: int | None = None):
    response = await add_star_rating_func(message, amount)
    await message.answer(response)

@chat_labeler.message(text=["!сбросить рейтинг"])
async def reset_rating(message: Message):
    response = await reset_rating_func(message)
    await message.answer(response)

@chat_labeler.message(text=["хранители звёзд", "хранители звезд"])
async def star_holders(message: Message):
    response = await star_holders_func(message)
    msg = ""
    response.sort(key=lambda x: x[1], reverse=True)
    for i in range(len(response)):
        msg = msg + f"{i}. {response[i][0]} - {response[i][1]} \n"
    await message.answer(msg)

@chat_labeler.message(text=["звёзды", "звезды"])
async def users_stars(message: Message):
    response = await users_stars_func(message)
    print(response)
    msg = ""
    response.sort(key=lambda x: x[1], reverse=True)
    for i in range(len(response)):
        msg = msg + f"{i}. {response[i][0]} - {response[i][1]} \n"
    await message.answer(msg)

@chat_labeler.message(text=["все звёзды", "все звезды"])
async def all_stars(message: Message):
    response = await all_stars_func(message)
    msg = ""
    for i in range(len(response)):
        msg = msg + f"{i}. {response[i][0]} - {response[i][1]} \n"
    await message.answer(msg)

@chat_labeler.message(text=["ирисфорбс"])
async def iris_forbs(message: Message):
    response = await iris_forbs_func(message)
    msg = ""
    for i in range(len(response)):
        msg = msg + f"{i+1}. {response[i][0]} - {response[i][1]} \n"
    await message.answer(msg)

@chat_labeler.message(text=["девиз"])
async def deviz(message: Message):
    await message.answer("в разработке")

@chat_labeler.message(text=["б-коин <amount>"])
async def b_coin(message: Message, amount: int | None = None):
    response = await b_coin_func(message, amount)
    await message.answer(response)

@chat_labeler.message(text=["коинс <amount> <chat_link>"])
async def coins(message: Message, amount: int | None = None, chat_link: str | None = None):
    response = await coins_func(message, amount, chat_link)
    await message.answer(response)

@chat_labeler.message(text=["б-топ"])
async def b_top(message: Message):
    response = await b_top_func(message)
    msg = ""
    for i in range(len(response)):
        msg = msg + f"{i}. {response[i][0]} - {response[i][1]} \n"
    await message.answer(msg)

@chat_labeler.message(text=["б-топ дня"])
async def b_top_day(message: Message):
    response = await b_top_day_func(message)
    await message.answer(response)

@chat_labeler.message(text=["г-топ"])
async def g_top(message: Message):
    response = await g_top_func(message)
    await message.answer(response)

#============================Модуль «Закладки»=============================

@chat_labeler.message(text=["новая закладка <text>"])
async def bookmark(message: Message, text: str | None = None):
    response = await bookmark_func(message, text)
    await message.answer(response)

@chat_labeler.message(text=["закладка <number>"])
async def bookmark_number(message: Message, number: int | None = None):
    response = await bookmark_number_func(message, number)
    print(response)
    msg = f"{response[number]['name']}\n({response[number]['date']})"
    forward = {
        "peer_id": message.peer_id,
        "conversation_message_ids": response[number]['message_id']
    }
    await message.answer(message=msg, forward=forward, disable_mentions=True)

@chat_labeler.message(text=["чатбук"])
async def chatbook(message: Message):
    response = await chatbook_func(message)
    msg = ""
    print(response)
    for i in response:
        if response[i]['active'] == False:
            continue
        msg = msg + f"{i}. {response[i]['name']} - ({response[i]['date']})\n"
    if msg == "":
        msg = "Список закладок пуст"
    await message.answer(msg)

@chat_labeler.message(text=["удалить закладку <number>"])
async def delete_bookmark(message: Message, number: int | None = None):
    response = await delete_bookmark_func(message, number)
    await message.answer(response)

@chat_labeler.message(text=["исключить закладку <number>"])
async def exclude_bookmark(message: Message, number: int | None = None):
    response = await exclude_bookmark_func(message, number)
    await message.answer(response)

@chat_labeler.message(text=["мои закладки"])
async def my_bookmarks(message: Message):
    response = await my_bookmarks_func(message)
    msg = ""
    for i in response:
        msg = msg + f"{i}. {response[i]['name']} - ({response[i]['date']})\n"
    await message.answer(msg)

@chat_labeler.message(text=["+кладмен <user_link>"])
async def cladman_add(message: Message, user_link: str | None = None):
    response = await cladman_add_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["-кладмен <user_link>"])
async def cladman_remove(message: Message, user_link: str | None = None):
    response = await cladman_remove_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["закладки рейтинг <number>"])
async def bookmarks_rating(message: Message, number: int | None = None):
    response = await bookmarks_rating_func(message, number)
    await message.answer(response)

#============================Модуль «Награды»=============================

@chat_labeler.message(text=["наградить <grade> <ser_link> <text>"], rank_filter=3)
async def reward(message: Message, grade: int | None = None, ser_link: str | None = None, text: str | None = None):
    response = await reward_func(message, grade, ser_link, text)
    await message.answer(response)

@chat_labeler.message(text=["снять все награды <user_link>"], rank_filter=3)
async def remove_all_rewards(message: Message, user_link: str | None = None):
    response = await remove_all_rewards_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["снять награды от <user_link>"], rank_filter=3)
async def remove_rewards_from_user(message: Message, user_link: str | None = None):
    response = await remove_rewards_from_user_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["снять награду <number> <user_link>"], rank_filter=3)
async def remove_reward(message: Message, number: int | None = None, user_link: str | None = None):
    response = await remove_reward_func(message, number, user_link)
    await message.answer(response)

@chat_labeler.message(text=["награды <user_link>"])
async def user_rewards(message: Message, user_link: str | None = None):
    response = await user_rewards_func(message, user_link)
    msg = "Награды пользователя: \n"
    for i in range(len(response)):
        msg = msg + f"{i+1}. {response[i][0]} степень: {response[i][1]} - от {response[i][3]} ({response[i][2]})\n"
    await message.answer(response)

#============================Модуль «Карта»=============================



#============================Модуль «Дуэли»=============================

@chat_labeler.message(text=["дуэль <user_link>", "дуэль"])
async def duel(message: Message, user_link: str | None = None):
    if user_link != None and user_link.split(" ")[0] == "исход":
        await duel_outcome(message, user_link.split(" ", 1)[1])
        return
    if user_link != None and user_link.split(" ")[0] == "да":
        await duel_accept(message)
        return
    if user_link != None and user_link.split(" ")[0] == "нет":
        await duel_decline(message)
        return
    global duel_users
    first = await group_api.users.get(user_ids=message.from_id)
    first_id = first[0].id
    if message.reply_message:
        user_link = message.reply_message.from_id
    else:
        user_link = user_link.split("|")[0][3:]
    second = await group_api.users.get(user_ids=user_link)
    second_id = second[0].id
    duel_users.update({first_id:{ "with": second_id,
                             "outcome": None}})
    await message.answer(f"Выберите исход дуэли написав 'дуэль исход (исход дуэли)'.\n"
                        "Исход дуэли:\n дуэль исход 0 (ничего не делать)\n"
                        "дуэль исход кик\n"
                        "дуэль исход бан минута\n"
                        "дуэль исход бан 10 минут\n"
                        "дуэль исход бан час\n"
                        "дуэль исход бан сутки\n"
                        "дуэль исход бан навсегда\n")
    #await message.answer(f"{first_name} вызвал на дуэль {second_name}.\nДля принятия дуэли напишите 'Дуэль да', для отмены 'Дуэль отмена'")

@chat_labeler.message(text=["дуэль исход <outcome>"])
async def duel_outcome(message: Message, outcome: str | None = None):
    global duel_users
    first_name = ""
    second_name = ""
    duel_outcome = {
        "0": None,
        "кик": "kick",
        "бан минута": "ban_1_minute",
        "бан 10 минут": "ban_10_minutes",
        "бан час": "ban_1_hour",
        "бан сутки": "ban_1_days",
        "бан навсегда": "ban_permanently"
    }
    outcome_1 = duel_outcome[outcome]
    for key, value in duel_users.items():
        if key == message.from_id:
            first_info = await group_api.users.get(user_ids=key)
            first_name = first_info[0].first_name + " " + first_info[0].last_name
            second_info = await group_api.users.get(user_ids=value["with"])
            second_name = second_info[0].first_name + " " + second_info[0].last_name
            duel_users[key] = {"with": value["with"],
                               "outcome": outcome_1}
    if first_name == "":
        return
    await message.answer(f"{first_name} вызвал на дуэль {second_name}.\nИсход дуэли {outcome}.\nДля принятия дуэли напишите 'Дуэль да', для отмены 'Дуэль отмена'")

@chat_labeler.message(text=["дуэль да"])
async def duel_accept(message: Message):
    global duel_users
    to_empty = None
    for key, value in duel_users.items():
        if value["with"] == message.from_id:
            to_empty = key
            response = await duel_accept_func(message, key, value["with"], value["outcome"])
            await message.answer(response)
    del duel_users[to_empty]

@chat_labeler.message(text=["дуэль отмена"])
async def duel_decline(message: Message):
    global duel_users
    for key, value in duel_users.items():
        if value[value] == message.from_id:
            first_info = await group_api.users.get(user_ids=key)
            first_name = first_info[0].first_name + " " + first_info[0].last_name
            second_info = await group_api.users.get(user_ids=value["with"])
            second_name = second_info[0].first_name + " " + second_info[0].last_name
            del duel_users[key]
            await message.answer(f"{second_name} отменил дуэль с {first_name}.")
        if key == message.from_id:
            first_info = await group_api.users.get(user_ids=key)
            first_name = first_info[0].first_name + " " + first_info[0].last_name
            second_info = await group_api.users.get(user_ids=value["with"])
            second_name = second_info[0].first_name + " " + second_info[0].last_name
            del duel_users[key]
            await message.answer(f"{first_name} отменил дуэль с {second_name}.")
    else:
        return

#============================Модуль «Антиспам»=============================

@chat_labeler.message(text=["+антиспам"])
async def antispam_add(message: Message):
    response = await antispam_add_func(message)
    await message.answer(response)

@chat_labeler.message(text=["-антиспам"])
async def antispam_remove(message: Message):
    response = await antispam_remove_func(message)
    await message.answer(response)

#============================Модуль «Кланы»=============================

@chat_labeler.message(text=["создать клан <name>"])
async def create_clan(message: Message, name: str | None = None):
    response = await create_clan_func(message, name)
    await message.answer(response)

@chat_labeler.message(text=["клан вступить <name>"])
async def join_clan(message: Message, name: str | None = None):
    response = await join_clan_func(message, name)
    await message.answer(response)

@chat_labeler.message(text=["удалить клан <name>"])
async def delete_clan(message: Message, name: str | None = None):
    response = await delete_clan_func(message, name)
    await message.answer(response)

@chat_labeler.message(text=["выйти из клана"])
async def leave_clan(message: Message):
    response = await leave_clan_func(message)
    await message.answer(response)

@chat_labeler.message(text=["клан изменить <name>"])
async def change_clan_name(message: Message, name: str | None = None):
    response = await change_clan_name_func(message, name)
    await message.answer(response)

@chat_labeler.message(text=["кланы"]) #FIX
async def get_clans(message: Message):
    chat_id = message.peer_id
    response = await get_clans_func(message)
    if response == {}:
        await message.answer("Кланов нет")
        return
    msg = "Список кланов: \n"
    print(response)
    for i in response:
        owner_info = ManageChats().get_user(chat_id, response[i]['owner'])
        owner = f"{owner_info[list(owner_info.keys())[0]]['first_name']} {owner_info[list(owner_info.keys())[0]]['last_name']}"
        msg = msg + f"{i} - Основатель: {owner}\nКоличество членов: {len(response[i]['members'])}\nОписание: {response[i]['description']}\n\n"
    await message.answer(msg)

@chat_labeler.message(text=["клан созвать всех"])
async def call_all_clans(message: Message):
    response = await call_all_clans_members_func(message)
    msg = ""
    for i in response:
        msg = msg + f"[id{i[0]}|{i[1]}]"
    await message.answer(msg)

@chat_labeler.message(text=["участники клана <name>"])
async def get_clan_members(message: Message, name: str | None = None):
    response = await get_clan_members_func(message, name)
    msg = "Участники клана: \n"
    for i in range(len(response)):
        msg = msg + f"{i+1}. {response[i][0]}\n"
    await message.answer(response)

@chat_labeler.message(text=["клан исключить <user_link>"])
async def kick_from_clan(message: Message, user_link: str | None = None):
    response = await kick_from_clan_func(message, user_link)
    await message.answer(response)

#============================Модуль «Кружки»=============================

@chat_labeler.message(text=["создать кружок <name>"])
async def create_faction(message: Message, name: str | None = None):
    response = await create_faction_func(message, name)
    await message.answer(response)

@chat_labeler.message(text=["удалить кружок <name>"])
async def delete_faction(message: Message, name: str | None = None):
    response = await delete_faction_func(message, name)
    await message.answer(response)

@chat_labeler.message(text=["кружки"])
async def get_factions(message: Message):
    chat_id = message.peer_id
    response = await get_factions_func(message)
    if response == {}:
        await message.answer("Кружков нет")
        return
    msg = "Список кружков: \n"
    for i in response:
        owner_info = ManageChats().get_user(chat_id, response[i]['owner'])
        owner = f"{owner_info[list(owner_info.keys())[0]]['first_name']} {owner_info[list(owner_info.keys())[0]]['last_name']}"
        msg = msg + f"{i} - Основатель кружка: {owner}\nКоличество членов: {len(response[i]['members'])}\nОписание: {response[i]['description']}\n\n"
    await message.answer(msg)

@chat_labeler.message(text=["участники кружка <name>"])
async def get_faction_members(message: Message, name: str | None = None):
    response = await get_faction_members_func(message, name)
    msg = "Участники кружка: \n"
    for i in range(len(response)):
        user_info = ManageChats().get_user(message.peer_id, response[i])
        user = f"{user_info[list(user_info.keys())[0]]['first_name']} {user_info[list(user_info.keys())[0]]['last_name']}"
        msg = msg + f"{i+1}. {user}\n"
    await message.answer(msg)

@chat_labeler.message(text=["кружок исключить <user_link>"])
async def kick_from_faction(message: Message, user_link: str | None = None):
    response = await kick_from_faction_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["кружок вступить <name>"])
async def join_faction(message: Message, name: str | None = None):
    response = await join_faction_func(message, name)
    await message.answer(response)

@chat_labeler.message(text=["выйти из кружка <name>"])
async def leave_faction(message: Message, name: str | None = None):
    response = await leave_faction_func(message, name)
    await message.answer(response)

@chat_labeler.message(text=["кружок <old_name> изменить <name>"])
async def change_faction_name(message: Message, old_name: str | None = None, name: str | None = None):
    response = await change_faction_name_func(message, old_name, name)
    await message.answer(response)

@chat_labeler.message(text=["кружок <name> созвать всех"])
async def call_all_faction_members(message: Message, name: str | None = None):
    response = await call_all_faction_members_func(message, name)
    msg = ""
    for i in response:
        user_info = ManageChats().get_user(message.peer_id, i)
        user = f"{user_info[list(user_info.keys())[0]]['first_name']} {user_info[list(user_info.keys())[0]]['last_name']}"
        msg = msg + f"[id{i}|{user}]"
    await message.answer(msg)

@chat_labeler.message(text=["удалить кружок <name>"])
async def delete_faction(message: Message, name: str | None = None):
    response = await delete_faction_func(message, name)
    await message.answer(response)

@chat_labeler.message(text=["кружок участники <name>"])
async def get_faction_members(message: Message, name: str | None = None):
    response = await get_faction_members_func(message, name)
    msg = "Участники кружка: \n"
    for i in range(len(response)):
        msg = msg + f"{i+1}. {response[i][0]}\n"
    await message.answer(response)

#============================Модуль «Отношения и Браки»=============================

@chat_labeler.message(text=["действие <text>"])
async def send_message(message: Message, text: str | None = None):
    if text.startswith("сделать завтрак"):
        response = await make_breakfast_func(message, "сделать завтрак", 100, 120)
        return response
    
    elif text.startswith("пригласить погулять"):
        response = await relationship_action_func(message, "пригласить погулять", 70, 60)
        return response
    
    elif text.startswith("подарить шокаладку"):
        response = await relationship_action_func(message, "подарить шокаладку", 50, 60)
        return response
    
    elif text.startswith("поговорить"):
        response = await relationship_action_func(message, "поговорить", 30, 44)
        return response

    elif text.startswith("поделитьcя едой"):
        response = await relationship_action_func(message, "поделитьcя едой", 20, 19)
        return response

    elif text.startswith("кинуть мем"):
        response = await relationship_action_func(message, "кинуть мем", 20, 19)
        return response

    elif text.startswith("расказать анекдот"):
        response = await relationship_action_func(message, "расказать анекдот", 10, 9)
        return response

    elif text.startswith("сделать комплимент"):
        response = await relationship_action_func(message, "сделать комплимент", 5, 4)
        return response

    elif text.startswith("дать пять"):
        response = await relationship_action_func(message, "дать пять", 0, 0)
        return response

    elif text.startswith("устроить сюрприз"):
        response = await relationship_action_func(message, "устроить сюрприз", 750, 0, 350)
        return response

    elif text.startswith("поговорить по душам"):
        response = await relationship_action_func(message, "поговорить по душам", 300, 0, 150)
        return response


@chat_labeler.message(text=["отн+ <user_link>"])
async def add_relationship(message: Message, user_link: str | None = None):
    relationships = ManageChats().get_relationships(message.peer_id)
    if message.from_id == str(user_link.split("|")[0][3:]):
        await message.answer("Вы не можете добавить себя в список отношений")
        return 
    for i in relationships:
        if relationships[i]["with_user"] == str(user_link.split("|")[0][3:]) and relationships[i]["status"] == 0:
            await message.answer("Вы уже отправили запрос на заключения знакомства")
            return
        if relationships[i]["with_user"] == str(user_link.split("|")[0][3:]) and relationships[i]["status"] != 0:
            await message.answer("Вы уже знакомы")
            return 
        if relationships[i]["user"] == str(user_link.split("|")[0][3:]) and relationships[i]["status"] == 0:
            response = await accept_relationship_func(message, relationships[i], i)
            await message.answer(response)
            return
        if relationships[i]["user"] == str(user_link.split("|")[0][3:]) and relationships[i]["status"] != 0:
            await message.answer("Вы уже знакомы")
            return
            
    response = await add_relationship_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["отн- <user_link>"])
async def remove_relationship(message: Message, user_link: str | None = None):
    response = await remove_relationship_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["отн основа <user_link>"])
async def set_relationship_base(message: Message, user_link: str | None = None):
    response = await set_relationship_base_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["статус отн <user_link>", "статус отн"])
async def get_relationship_status(message: Message, user_link: str | None = None):
    response = await get_relationship_status_func(message, user_link)
    print(response)
    user_id = message.from_id
    user_info = ManageChats().get_user(message.peer_id, user_id)
    status = "Женаты" if response[0]["married"] else response[0]["status"]
    duration = datetime.now() - datetime.strptime(response[0]['start_date'].split('.')[0], '%Y-%m-%d %H:%M:%S')
    available = ""
    if user_info[list(user_info.keys())[0]]['relationship_cd'] == None or user_info[list(user_info.keys())[0]]['relationship_cd'] <= 0:
        available = "Можно совершить действие"
    else:
        available = f"Доступно через {user_info[list(user_info.keys())[0]]['relationship_cd']} секунд"
    msg = (f"Отношения между {response[1]} и {response[2]}\n"
          f"Статус отношений: {status}\n"
          f"Крепкость отношений: {response[0]['hp']}\n"
          f"Длительность отношений: {duration.days} дней, {duration.seconds//3600} часов, {(duration.seconds//60)%60} минут, {duration.seconds%60} секунд\n\n"
          f"Доступность: {available}\n"
          f"Доступные действия:\n"
          f"'Сделать завтрак' +100hp, -2 часа\n"
          f"'Пригласить погулять' +70hp, -1 часа\n"
          f"'Подарить шокаладку' +50hp, -1 часа\n"
          f"'Поговорить' +30hp, -45 минут\n"
          f"'Поделитьмя едой' +20hp, -20 минут\n"
          f"'Кинуть мем' +20hp, -20 минут\n"
          f"'Расказать анекдот' +10hp, -10 минут\n"
          f"'Сделать комплимент' +5hp, -5 минут\n"
          f"'Дать пять' РП\n\n"
          f"Устроить сюрприз (+750hp) за 350 монет\n"
          f"Поговорить по душам (+300hp) за 150 монет\n")

    await message.answer(msg)

@chat_labeler.message(text=["история отн <user_link>"])
async def get_relationship_history(message: Message, user_link: str | None = None):
    response = await get_relationship_history_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["мои отношения"])
async def get_my_relationships(message: Message):
    response = await get_my_relationships_func(message)
    msg = "Мои отношения: \n"
    for i in response:
        user_info = ManageUsers().get_user_by_id(i[1])
        user_name = user_info.first_name + " " + user_info.last_name
        user_info2 = ManageUsers().get_user_by_id(i[0])
        user_name2 = user_info2.first_name + " " + user_info2.last_name
        msg += f"{user_name} и {user_name2} - Статус отношений: {i[2]}\n"
    await message.answer(msg)

@chat_labeler.message(text=["отны"])
async def get_all_main_relationships(message: Message):
    response = await get_all_main_relationships_func(message)
    msg = "Все основные отношения: \n"
    for i in response:
        msg += f"{i[0]} и {i[1]}\n"
    await message.answer(msg)

@chat_labeler.message(text=["брак <user_link>"])
async def create_marriage(message: Message, user_link: str | None = None):
    print(user_link, user_link == "да", user_link == "нет")
    if user_link == "да":
        await accept_marriage(message)
        return
    if user_link == "нет":
        await decline_marriage(message)
        return
    response = await create_marriage_func(message, user_link)
    await message.answer(response)

@chat_labeler.message(text=["брак да"])
async def accept_marriage(message: Message):
    response = await accept_marriage_func(message)
    await message.answer(response)

@chat_labeler.message(text=["брак нет"])
async def decline_marriage(message: Message):
    response = await decline_marriage_func(message)
    await message.answer(response)

@chat_labeler.message(text=["!развод"])
async def delete_marriage(message: Message):
    response = await delete_marriage_func(message)
    await message.answer(response)

@chat_labeler.message(text=["поженить пару <user_link> <with_link>"])
async def make_marriage(message: Message, user_link: str | None = None, with_link: str | None = None):
    response = await make_marriage_func(message, user_link, with_link)
    await message.answer(response)

@chat_labeler.message(text=["развести пару <user_link> <with_link>"])
async def divorce_marriage(message: Message, user_link: str | None = None, with_link: str | None = None):
    response = await divorce_marriage_func(message, user_link, with_link)
    await message.answer(response)

@chat_labeler.message(text=["!сброс браков"])
async def reset_marriages(message: Message):
    response = await reset_marriages_func(message)
    await message.answer(response)

# @bot.on.message(text="Привет")
# async def hi_handler(message: Message):
#     users_info = await bot.api.users.get(message.from_id)
#     await message.answer("Привет, {}".format(users_info[0].first_name))
    