from db import db
from db.models import *
from sqlalchemy.exc import NoResultFound
import logging

session = db.create_db()

class ManageChats:
    def add_chat(self, chat:Chats):
        try:
            session.add(chat)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_chat(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one()
        except NoResultFound:
            return None
        
    def get_chats(self):
        try:
            return session.query(Chats).all()
        except NoResultFound:
            return None
        
    def get_chat_owner(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().owner
        except NoResultFound:
            return None

    def get_users(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().users
        except NoResultFound:
            return None
    
    def get_user(self, chat_id, user_id):
        try:
            users = session.query(Chats).filter(Chats.chat_id == chat_id).one().users
            for user in users:
                if user == str(user_id):
                    return {user: users[user]}
        except NoResultFound:
            return None
        
    def add_user(self, chat_id, user:User_info):
        try:
            users = session.query(Chats).filter(Chats.chat_id == chat_id).one().users
            users.update(user)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().users = users
            session.commit()
        except:
            session.rollback()
            raise Exception

    def update_user(self, chat_id, user):
        try:
            users = session.query(Chats).filter(Chats.chat_id == chat_id).one().users
            users.update(user)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().users = users
            session.commit()
        except:
            session.rollback()
            raise Exception

    def get_staff(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().staff
        except NoResultFound:
            return None
        
    def update_staff(self, chat_id, user_id, user):
        try:
            staff = session.query(Chats).filter(Chats.chat_id == chat_id).one().staff
            staff.update(user)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().staff = staff
            session.commit()
        except:
            session.rollback()
            raise Exception
    
    def add_staff(self, chat_id, user):
        try:
            staff = session.query(Chats).filter(Chats.chat_id == chat_id).one().staff
            staff.update(user)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().staff = staff
            session.commit()
        except:
            session.rollback()
            raise Exception
    
    def remove_staff(self, chat_id, user):
        try:
            staff = session.query(Chats).filter(Chats.chat_id == chat_id).one().staff
            staff.pop(user)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().staff = staff
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_rp_commands(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().rp_command
        except NoResultFound:
            return None
        
    def add_rp_command(self, chat_id, command):
        try:
            session.query(Chats).filter(Chats.chat_id == chat_id).one().rp_command.append(command)
            session.commit()
        except:
            session.rollback()
            raise Exception

    def delete_rp_command(self, chat_id, command):
        try:
            session.query(Chats).filter(Chats.chat_id == chat_id).one().rp_command.remove(command)
            session.commit()
        except:
            session.rollback()
            raise Exception       
        
    def get_punished(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().punished
        except NoResultFound:
            return None
        
    def add_punished(self, chat_id, punish):
        try:
            punished = session.query(Chats).filter(Chats.chat_id == chat_id).one().punished
            punished.update(punish)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().punished = punished
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def remove_punished(self, chat_id, user_id):
        try:
            punished = session.query(Chats).filter(Chats.chat_id == chat_id).one().punished
            punished.pop(user_id)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().punished = punished
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def delete_all_punished(self, chat_id):
        try:
            session.query(Chats).filter(Chats.chat_id == chat_id).one().punished = []
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def delete_warn(self, chat_id, user_id, count):
        try:
            delete = []
            if count != None:
                count = int(count)
            punished = session.query(Chats).filter(Chats.chat_id == chat_id).one().punished
            for punish in punished:
                if count == None and list(punish.keys())[0] == user_id and punish[list(punish.keys())[0]]['punishment'] == "warn":
                    delete.append(punish)
                elif count != 0 and list(punish.keys())[0] == user_id and punish[list(punish.keys())[0]]['punishment'] == "warn":
                    count -= 1
                    delete.append(punish)
            for d in delete:
                punished.pop(d)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().punished = punished
            session.commit()
            return len(delete)
        except:
            session.rollback()
            raise Exception
        
    def get_bookmarks(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().bookmarks
        except NoResultFound:
            return None
        
    def get_bookmark(self, chat_id, bookmark):
        try:
            bookmarks = session.query(Chats).filter(Chats.chat_id == chat_id).one().bookmarks
            for b in bookmarks:
                if b == str(bookmark):
                    return {b: bookmarks[b]}
        except NoResultFound:
            return None
        
    def get_bookmarks_count(self, chat_id):
        try:
            count = 0
            bookmarks = session.query(Chats).filter(Chats.chat_id == chat_id).one().bookmarks
            for bookmark in bookmarks:
                count = bookmark
            return int(count) + 1
        except NoResultFound:
            return 0
        
    def add_bookmark(self, chat_id, bookmark):
        try:
            bookmarks = session.query(Chats).filter(Chats.chat_id == chat_id).one().bookmarks
            bookmarks.update(bookmark)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().bookmarks = bookmarks
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def remove_bookmark(self, chat_id, bookmark):
        try:
            bookmarks = session.query(Chats).filter(Chats.chat_id == chat_id).one().bookmarks
            bookmarks.pop(bookmark)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().bookmarks = bookmarks
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def exclude_bookmark(self, chat_id, bookmark):
        try:
            bookmarks = session.query(Chats).filter(Chats.chat_id == chat_id).one().bookmarks
            for b in bookmarks:
                if b == str(bookmark):
                    bookmarks[b]["active"] = False
                    break
            session.query(Chats).filter(Chats.chat_id == chat_id).one().bookmarks = bookmarks
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def return_all_bookmarks_from_user(self, chat_id, user_id):
        try:
            bookmarks = session.query(Chats).filter(Chats.chat_id == chat_id).one().bookmarks
            for b in bookmarks:
                if bookmarks[b]["from_id"] == str(user_id):
                    bookmarks[b]["active"] = True
            session.query(Chats).filter(Chats.chat_id == chat_id).one().bookmarks = bookmarks
            session.commit()
        except:
            session.rollback()
            raise Exception

    def exclude_all_bookmarks_from_user(self, chat_id, user_id):
        try:
            bookmarks = session.query(Chats).filter(Chats.chat_id == chat_id).one().bookmarks
            for b in bookmarks:
                if bookmarks[b]["from_id"] == str(user_id):
                    bookmarks[b]["active"] = False
            session.query(Chats).filter(Chats.chat_id == chat_id).one().bookmarks = bookmarks
            session.commit()
        except:
            session.rollback()
            raise Exception
    
    def get_clans(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().clans
        except NoResultFound:
            return None
        
    def get_clan(self, chat_id, clan):
        try:
            clans = session.query(Chats).filter(Chats.chat_id == chat_id).one().clans
            for i in clans:
                if i == clan:
                    return {i: clans[i]}
        except NoResultFound:
            return None
        
    def get_clan_by_owner(self, chat_id, owner):
        try:
            clans = session.query(Chats).filter(Chats.chat_id == chat_id).one().clans
            for i in clans:
                if clans[i]["owner"] == owner:
                    return {i: clans[i]}
        except NoResultFound:
            return None
        
    def add_clan(self, chat_id, clan):
        try:
            clans = session.query(Chats).filter(Chats.chat_id == chat_id).one().clans
            clans.update(clan)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().clans = clans
            session.commit()
            return True
        except:
            session.rollback()
            raise Exception
        
    def delete_clan(self, chat_id, clan):
        try:
            clans = session.query(Chats).filter(Chats.chat_id == chat_id).one().clans
            clans.pop(clan)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().clans = clans
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def remove_clan_member(self, chat_id, clan):
        try:
            clans = session.query(Chats).filter(Chats.chat_id == chat_id).one().clans
            for i in clans:
                if i == clan:
                    clans[i]["members"] = []
                    break
            session.query(Chats).filter(Chats.chat_id == chat_id).one().clans = clans
            session.commit()
        except:
            session.rollback()

    def remove_user_clan(self, chat_id, user_id):
        try:
            user = self.get_user(chat_id, user_id)
            user[list(user.keys())[0]]["clan"] = None
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def leave_clan(self, chat_id, clan, member):
        try:
            clans = session.query(Chats).filter(Chats.chat_id == chat_id).one().clans
            for i in clans:
                if i == clan:
                    clans[i]["members"].remove(member)
                    break
            session.query(Chats).filter(Chats.chat_id == chat_id).one().clans = clans
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def change_clan_name(self, chat_id, clan, name):
        try:
            clans = session.query(Chats).filter(Chats.chat_id == chat_id).one().clans
            new_clan = {name: clans[clan]}
            clans.update(new_clan)
            for user in clans[clan]["members"]:
                user_info = self.get_user(chat_id, user)
                user_info[list(user_info.keys())[0]]["clan"].remove(clan)
                user_info[list(user_info.keys())[0]]["clan"].append(new_clan)
                self.update_user(chat_id, user_info)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().clans = clans
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def join_clan(self, chat_id, clan, member):
        try:
            clans = session.query(Chats).filter(Chats.chat_id == chat_id).one().clans
            for i in clans:
                if i == clan:
                    clans[i]["members"].append(member)
                    break
            session.query(Chats).filter(Chats.chat_id == chat_id).one().clans = clans
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def change_clans(self, chat_id, clans:Clans):
        try:
            session.query(Chats).filter(Chats.chat_id == chat_id).one().clans = clans
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_factions(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().factions
        except NoResultFound:
            return None
        
    def get_faction(self, chat_id, faction):
        try:
            factions = session.query(Chats).filter(Chats.chat_id == chat_id).one().factions
            for i in factions:
                if i == faction:
                    return {i: factions[i]}
        except NoResultFound:
            return None
        
    def add_faction(self, chat_id, faction):
        try:
            factions = session.query(Chats).filter(Chats.chat_id == chat_id).one().factions
            factions.update(faction)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().factions = factions
            session.commit()
            return True
        except:
            session.rollback()
            raise Exception

    def delete_faction(self, chat_id, faction):
        try:
            factions = session.query(Chats).filter(Chats.chat_id == chat_id).one().factions
            for user in faction[list(faction.keys())[0]]["members"]:
                user_info = self.get_user(chat_id, user)
                user_info[list(user_info.keys())[0]]["faction"].remove(faction)
                self.update_user(chat_id, user_info)
            faction_key = list(faction.keys())[0]
            factions.pop(faction_key)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().factions = factions
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_faction_members(self, chat_id, faction):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().factions[faction]["members"]
        except NoResultFound:
            return None
        
    def add_faction_member(self, chat_id, faction, member):
        try:
            factions = session.query(Chats).filter(Chats.chat_id == chat_id).one().factions
            factions[faction]["members"].append(member)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().factions = factions
            session.commit()
        except: 
            session.rollback()
            raise Exception

    def delete_faction_member(self, chat_id, faction, member):
        try:
            factions = session.query(Chats).filter(Chats.chat_id == chat_id).one().factions
            factions[faction]["members"].remove(member)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().factions = factions
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def change_faction_name(self, chat_id, faction, name):
        try:
            factions = session.query(Chats).filter(Chats.chat_id == chat_id).one().factions
            new_faction = {name: factions[faction]}
            factions.update(new_faction)
            for user in factions[faction]["members"]:
                user_info = self.get_user(chat_id, user)
                user_info[list(user_info.keys())[0]]["faction"].remove(faction)
                user_info[list(user_info.keys())[0]]["faction"].append(new_faction)
                self.update_user(chat_id, user_info)
            factions.pop(faction)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().factions = factions
            session.commit()
        except:
            session.rollback()
            raise Exception
    
    def change_factions(self, chat_id, factions):
        try:
            session.query(Chats).filter(Chats.chat_id == chat_id).one().factions = factions
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_commands(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().commands
        except NoResultFound:
            return None
        
    def change_commands(self, chat_id, commands:Commands):
        try:
            session.query(Chats).filter(Chats.chat_id == chat_id).one().commands = commands
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_settings(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().settings
        except NoResultFound:
            return None
        
    def change_settings(self, chat_id, settings:ChatSettings):
        try:
            session.query(Chats).filter(Chats.chat_id == chat_id).one().settings = settings
            session.commit()
        except:
            session.rollback()
            raise Exception
    
    def get_relationships(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().relationships
        except NoResultFound:
            return None
        
    def add_relationships(self, chat_id, relationship):
        try:
            relationships = session.query(Chats).filter(Chats.chat_id == chat_id).one().relationships
            relationships.update(relationship)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().relationships = relationships
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_relationship_count(self, chat_id):
        try:
            count = 0
            relationships = session.query(Chats).filter(Chats.chat_id == chat_id).one().relationships
            for rel in relationships:
                count = rel
            return int(count) + 1
        except NoResultFound:
            return 0
        
    def set_relationship_main(self, chat_id, from_id, main_id):
        try:
            user = self.get_user(chat_id, from_id)
            user[list(user.keys())[0]]["relationship_main"] = main_id
            self.update_user(chat_id, user)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def delete_relationships(self, chat_id, relationship):
        try:
            relationships = session.query(Chats).filter(Chats.chat_id == chat_id).one().relationships
            relationships.pop(relationship)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().relationships = relationships
            session.commit()
        except:
            session.rollback()
            raise Exception
    
    def change_relationships(self, chat_id, relationship):
        try:
            relationships = session.query(Chats).filter(Chats.chat_id == chat_id).one().relationships
            relationships.update(relationship)
            session.query(Chats).filter(Chats.chat_id == chat_id).one().relationships = relationships
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_group_coins(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().coins
        except NoResultFound:
            return None
        
    def add_group_coins(self, chat_id, coins):
        try:
            session.query(Chats).filter(Chats.chat_id == chat_id).one().coins += coins
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def reduce_group_coins(self, chat_id, coins):
        try:
            session.query(Chats).filter(Chats.chat_id == chat_id).one().coins -= coins
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def change_group_coins(self, chat_id, coins):
        try:
            coins = session.query(Chats).filter(Chats.chat_id == chat_id).one().coins
            coins = coins
            session.query(Chats).filter(Chats.chat_id == chat_id).one().coins = coins
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_money_group(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().money_group
        except NoResultFound:
            return None
        
    def add_money_group(self, chat_id, money_group):
        try:
            session.query(Chats).filter(Chats.chat_id == chat_id).one().money_group += money_group
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def remove_money_group(self, chat_id, money_group):
        try:
            session.query(Chats).filter(Chats.chat_id == chat_id).one().money_group -= money_group
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def money_to_owner(self, chat_id):
        try:
            amount = session.query(Chats).filter(Chats.chat_id == chat_id).one().money_group
            session.query(Chats).filter(Chats.chat_id == chat_id).one().money_group = 0
            session.commit()
            return amount
        except:
            session.rollback()
            raise Exception

    def change_money_group(self, chat_id, money_group):
        try:
            session.query(Chats).filter(Chats.chat_id == chat_id).one().money_group = money_group
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_domain(self, chat_id):
        try:
            return session.query(Chats).filter(Chats.chat_id == chat_id).one().settings['domain']
        except NoResultFound:
            return None
        
    def get_chat_by_domain(self, domain):
        try:
            return session.query(Chats).filter(Chats.settings['domain'] == f'"{domain}"').one()
        except NoResultFound:
            return None
        
    def change_domain(self, chat_id, domain):
        try:
            settings = session.query(Chats).filter(Chats.chat_id == chat_id).one().settings
            settings['domain'] = domain
            session.query(Chats).filter(Chats.chat_id == chat_id).one().settings = settings
            session.commit()
            return domain
        except:
            session.rollback()
            raise Exception
        
    def get_user_inventory(self, chat_id, user_id):
        try:
            user = self.get_user(chat_id, user_id)
            return user[list(user.keys())[0]]['inventory']
        except NoResultFound:
            return None
        
    def add_inventory_item(self, chat_id, user_id, item, count):
        try:
            user = self.get_user(chat_id, user_id)
            user[list(user.keys())[0]]["inventory"][item] += count
            self.update_user(chat_id, user)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def reduce_inventory_item(self, chat_id, user_id, item, count):
        try:
            user = self.get_user(chat_id, user_id)
            user[list(user.keys())[0]]["inventory"][item] -= count
            self.update_user(chat_id, user)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def change_inventory_view(self, chat_id, user_id, view:bool):
        try:
            user = self.get_user(chat_id, user_id)
            user[list(user.keys())[0]]["inventory_view"] = view
            self.update_user(chat_id, user)
            session.commit()
        except:
            session.rollback()
            raise Exception



class ManageUsers:
    def get_user(self, user_id):
        try:
            return session.query(Users).filter(Users.user_id == user_id).one()
        except NoResultFound:
            return None
        
    def get_user_by_username(self, username):
        try:
            return session.query(Users).filter(Users.username == username).one()
        except NoResultFound:
            return None
        
    def get_user_by_id(self, user_id):
        try:
            return session.query(Users).filter(Users.user_id == int(user_id)).one()
        except NoResultFound:
            return None
        
    def get_all_users(self):
        try:
            return session.query(Users).all()
        except NoResultFound:
            return None
        
    def add_user(self, user:Users):
        try:
            session.add(user)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def delete_user(self, user_id):
        try:
            session.query(Users).filter(Users.user_id == user_id).delete()
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def update_user(self, user:Users):
        try:
            user1 = session.query(Users).filter(Users.user_id == user.user_id).one()
            user1 = user
            session.commit()
        except:
            session.rollback()
            raise Exception
        
        
    def add_user_money(self, user_id, money):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().money += float(money)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def reduce_user_money(self, user_id, money):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().money -= float(money)
            session.commit()
        except:
            session.rollback()
            raise Exception

    def update_user_money(self, user_id, money):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().money = float(money)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def add_user_coins(self, user_id, coins):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().coins += int(coins)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def reduce_user_coins(self, user_id, coins):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().coins -= int(coins)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_reputation(self, user_id):
        try:    
            return session.query(Users).filter(Users.user_id == user_id).one().reputation
        except:
            raise Exception
                
    def add_user_reputation(self, user_id, rep):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().reputation += int(rep)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def reduce_user_reputation(self, user_id, rep):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().reputation -= int(rep)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def update_user_reputation(self, user_id, rep):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().reputation = int(rep)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_user_stars(self, user_id):
        try:
            return session.query(Users).filter(Users.user_id == user_id).one().stars
        except:
            raise Exception
        
    def add_user_stars(self, user_id, rep):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().stars += int(rep)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def reduce_user_stars(self, user_id, rep):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().stars -= int(rep)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def update_user_stars(self, user_id, rep):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().stars = int(rep)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_user_balance(self, user_id):
        try:
            user = session.query(Users).filter(Users.user_id == user_id).one()
            balance = [user.money, user.coins, user.stars, user.reputation, user.gold]
            return balance
        except:
            raise Exception
        
    def add_user_chats(self, user_id, chat_id):
        try:
            chats = session.query(Users).filter(Users.user_id == user_id).one().chats
            chats.append(chat_id)
            session.query(Users).filter(Users.user_id == user_id).one().chats = chats
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def delete_user_chats(self, user_id, chat_id):
        try:
            chats = session.query(Users).filter(Users.user_id == user_id).one().chats
            chats.remove(chat_id)
            session.query(Users).filter(Users.user_id == user_id).one().chats = chats
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def update_user_chats(self, user_id, chats):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().chats = chats
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def add_user_gold(self, user_id, gold):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().gold += int(gold)
            session.commit()
        except:
            session.rollback()
            raise Exception

    def reduce_user_gold(self, user_id, gold):
        try:
            session.query(Users).filter(Users.user_id == user_id).one().gold -= int(gold)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    


class ManageAntiSpam:
    def add_user(self, user:Antispam):
        try:
            session.add(user)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_user_by_id(self, user_id):
        try:
            return session.query(Antispam).filter(Antispam.user_id == user_id).one()
        except NoResultFound:
            return None
        
    def remove_user(self, user_id):
        try:
            session.query(Antispam).filter(Antispam.user_id == user_id).delete()
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_all_users(self):
        try:
            return session.query(Antispam).all()
        except NoResultFound:
            return None
        

class ManageStockMarket:
    def get_all_bids(self):
        try:
            return session.query(StockMarket).all()
        except:
            raise Exception

    def add_bid(self, bid):
        try:
            session.add(bid)
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def reduce_bid_count(self, bid_id, count):
        try:
            session.query(StockMarket).filter(StockMarket.id == bid_id).one().count -= count
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def remove_bid(self, bid_id):
        try:
            session.query(StockMarket).filter(StockMarket.id == bid_id).delete()
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def remove_bids_by_user_id(self, user_id):
        try:
            session.query(StockMarket).filter(StockMarket.user_id == user_id).delete()
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    def get_bids_by_user_id(self, user_id):
        try:
            return session.query(StockMarket).filter(StockMarket.user_id == user_id).all()
        except NoResultFound:
            return None
        
    def get_bids_by_price(self, user_id, price):
        try:
            return session.query(StockMarket).filter(StockMarket.user_id == user_id).filter(StockMarket.price == price).all()
        except NoResultFound:
            return None
        
    def get_bid_by_id(self, bid_id):
        try:
            return session.query(StockMarket).filter(StockMarket.id == bid_id).one()
        except NoResultFound:
            return None
        
    def remove_bids_by_price(self, user_id, price):
        try:
            session.query(StockMarket).filter(StockMarket.user_id == user_id).filter(StockMarket.price == price).delete()
            session.commit()
        except:
            session.rollback()
            raise Exception
        
    