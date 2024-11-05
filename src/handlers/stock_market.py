from datetime import datetime, timedelta

from vkbottle import API
from vkbottle.bot import BotLabeler, Message, rules

from config import group_api
from db.dataspace import ManageChats, Chats, ManageUsers, Users, ManageStockMarket, StockMarket

def find_sublist_index(lst, target):
    for index, sublist in enumerate(lst):
        if sublist[0] == target:
            return index
    return -1


async def stock_market(message: Message):
    text = message["text"].lower().split(" ")
    print(text)
    if text[0] == "биржа" and len(text) == 1:
        await stock_market_display(message)
    elif text[0] == "биржа" and text[1] == "мои" and text[2] == "заявки":
        await get_user_bids(message)
    elif text[0] == "биржа" and text[1] == "купить" and text[2] != None and text[3] != None:
        await stock_market_add_bid(message, text[1],int(text[2]),int(text[3]))
    elif text[0] == "биржа" and text[1] == "продать" and text[2] != None and text[3] != None:
        await stock_market_add_bid(message, text[1],int(text[2]),int(text[3]))
    elif text[0] == "биржа" and text[1] == "отменить" and (text[2] == "всё" or text[2] == "все"):
        await stock_market_remove_all_bids(message)
    elif text[0] == "биржа" and text[1] == "отменить" and text[2] != None:
        await stock_market_remove_bid_by_price(message, int(text[2]))
    elif text[0] == "биржа" and text[1] == "ирис-голд":
        await stock_market_add_gold(message)

async def stock_market_display(message):
    all_bids = ManageStockMarket().get_all_bids()
    bid_buy = []
    bid_sell = []
    for bid in all_bids:
        if bid.type == "buy":
            bid_buy.append(bid)
        elif bid.type == "sell":
            bid_sell.append(bid)
    
    bid_buy.sort(key=lambda x: x.price, reverse=True)
    bid_sell.sort(key=lambda x: x.price, reverse=True)

    depth_of_buy = []
    depth_of_sell = []
    for bid in bid_buy:
        if bid.price not in [sublist[0] for sublist in depth_of_buy]:
            depth_of_buy.append([bid.price, bid.count])
        else:
            index = find_sublist_index(depth_of_buy, bid.price)
            depth_of_buy[index][1] += bid.count
    for bid in bid_sell:
        if bid.price not in [sublist[0] for sublist in depth_of_sell]:
            depth_of_sell.append([bid.price, bid.count])
        else:
            index = find_sublist_index(depth_of_sell, bid.price)
            depth_of_sell[index][1] += bid.count
        

    msg1 = f"Заявки на продажу\n"
    msg2 = f"Заявки на покупку\n"
    for i in range(10):
        if i < len(bid_buy):
            try:
                msg2 = msg2 + f"🟢 {depth_of_buy[i][0]} ирисок|{depth_of_buy[i][1]} ирис-голд\n"
            except:
                pass
        if i < len(bid_sell):
            try:
                msg1 = msg1 + f"🔴 {depth_of_sell[i][0]} ирисок|{depth_of_sell[i][1]} ирис-голд\n"
            except:
                pass
    msg = msg1 + msg2
    await group_api.messages.send(peer_id=message["peer_id"], message=msg, random_id = 0)

async def get_user_bids(message):
    user_bids = ManageStockMarket().get_bids_by_user_id(message["from_id"])
    msg = "Ваши заявки\n"
    for bid in user_bids:
        msg = msg + f"{bid.type} - {bid.count} - {bid.price} \n"
    await group_api.messages.send(peer_id=message["peer_id"], message=msg, random_id = 0)

async def stock_market_add_bid(message, type, count, price):
    if type == "купить":
        type = "buy"
    elif type == "продать":
        type = "sell"
    if count <= 0:
        await group_api.messages.send(peer_id=message["peer_id"], message="Количество должно быть больше нуля", random_id = 0)
        return
    if price <= 0:
        await group_api.messages.send(peer_id=message["peer_id"], message="Цена должна быть больше нуля", random_id = 0)
        return
    if type == "buy":
        cost = price * count
        user= ManageUsers().get_user(message["from_id"])
        user_money = user.money
        if user_money < cost:
            await group_api.messages.send(peer_id=message["peer_id"], message="Недостаточно ирисок", random_id = 0)
            return
        ManageUsers().reduce_user_money(message["from_id"], cost)
    if type == "sell":
        if count > ManageUsers().get_user(message["from_id"]).gold:
            await group_api.messages.send(peer_id=message["peer_id"], message="Недостаточно ирис-голд", random_id = 0)
            return
        ManageUsers().reduce_user_gold(message["from_id"], count)
    bids = ManageStockMarket().get_all_bids()
    bid_buy = []
    bid_sell = []
    for bid in bids:
        if bid.type == "buy":
            bid_buy.append(bid)
        elif bid.type == "sell":
            bid_sell.append(bid)
    bid_buy.sort(key=lambda x: x.price, reverse=True)
    bid_sell.sort(key=lambda x: x.price)
    if type == "buy":
        for bid in bid_sell:
            if bid.price <= price:
                change = count - bid.count
                if change < 0:
                    ManageUsers().add_user_gold(message["from_id"], count)
                    ManageStockMarket().reduce_bid_count(bid.id, count)
                    ManageUsers().add_user_money(bid.user_id, bid.price * count)
                    await group_api.messages.send(peer_id=bid.user_id, message=f"Заявка {bid.price} - {bid.count + count} на продажу частично исполнена. Заявка изменена на {bid.price} - {bid.count}. Средства пополнены на {bid.price * count}", random_id = 0)
                    await group_api.messages.send(peer_id=message["from_id"], message=f"Заявка на покупку исполнена.\nБаланс ирис-голд: {ManageUsers().get_user(message['from_id']).gold}", random_id = 0)
                    return
                else:
                    ManageUsers().add_user_gold(message["from_id"], bid.count)
                    ManageStockMarket().remove_bid(bid.id)
                    ManageUsers().add_user_money(bid.user_id, bid.price * bid.count)
                    await group_api.messages.send(peer_id=bid.user_id, message=f"Заявка {bid.price} - {bid.count} на продажу исполнена. Средства пополнены на {bid.price * bid.count}", random_id = 0)
                    count -= bid.count

    elif type == "sell":
        for bid in bid_buy:
            if bid.price == price:
                change = count - bid.count
                if change < 0:
                    ManageUsers().add_user_money(message["from_id"], bid.price * count)
                    ManageStockMarket().reduce_bid_count(bid.id, count)
                    await group_api.messages.send(peer_id=bid.user_id, message=f"Заявка {bid.price} - {bid.count + count} на покупку частично исполнена. Заявка изменена на {bid.price} - {bid.count}.\nИрис-голд пополнены на {bid.price * bid.count}. Баланс ирис-голд: {ManageUsers().get_user(message['from_id']).gold}", random_id = 0)
                    await group_api.messages.send(peer_id=message["from_id"], message=f"Заявка на продажу исполнена.\nБаланс пополнена на {price * count}", random_id = 0)
                    return
                else:
                    ManageUsers().add_user_money(message["from_id"], bid.price * bid.count)
                    ManageStockMarket().remove_bid(bid.id)
                    await group_api.messages.send(peer_id=bid.user_id, message=f"Заявка {bid.price} - {bid.count} на покупку исполнена.\nБалан ирис-гоглд {ManageUsers().get_user(message['from_id']).gold}", random_id = 0)
                    count -= bid.count

    bid = StockMarket(user_id=message["from_id"], price=price, count=count, type=type)
    ManageStockMarket().add_bid(bid)
    if type == "buy":
        await group_api.messages.send(peer_id=message["peer_id"], message=f"Заявка {price} ирисок|{count} ирис-голд на покупку добавлена", random_id = 0)
    elif type == "sell":
        await group_api.messages.send(peer_id=message["peer_id"], message=f"Заявка {price} ирисок|{count} ирис-голд на продажу добавлена", random_id = 0)

async def stock_market_remove_all_bids(message):
    bids = ManageStockMarket().get_bids_by_user_id(message["from_id"])
    price = 0
    for bid in bids:
        if bid.type == "buy":
            price += bid.price
    ManageStockMarket().remove_bids_by_user_id(message["from_id"])
    ManageUsers().add_user_money(message["from_id"], price)
    await group_api.messages.send(peer_id=message["peer_id"], message="Все заявки удалены", random_id = 0)

async def stock_market_remove_bid_by_price(message, price):
    price = int(price)
    bids = ManageStockMarket().get_bids_by_price(message["from_id"], price)
    money = 0
    for bid in bids:
        if bid.type == "buy":
            money += bid.price
    ManageStockMarket().remove_bids_by_price(message["from_id"], price)
    ManageUsers().add_user_money(message["from_id"], money)
    await group_api.messages.send(peer_id=message["peer_id"], message=f"Заявки на {price} удалены", random_id = 0)

async def stock_market_add_gold(message):
    ManageUsers().add_user_gold(message["from_id"], 1000)
    await group_api.messages.send(peer_id=message["peer_id"], message=f"Вы получили 1000 ирис-голд", random_id = 0)
