from vkbottle.bot import Message
from vkbottle.dispatch.rules import ABCRule

from config import group_api
from db.dataspace import ManageChats


class RankRule(ABCRule[Message]):
    def __init__(self, rank_filter) -> None:
        self.rank_filter = rank_filter
                
    async def check(self, message: Message) -> bool:

        print(message, message.from_id)

        staff = ManageChats().get_staff(message.peer_id)
        try:
            user_rank = staff[str(message.from_id)]['role']
        except:
            user_rank = 0
        command_ranks = ManageChats().get_commands(message.peer_id)
        try:
            command_rank = command_ranks[self.rank_filter]
        except:
            command_rank = self.rank_filter
        if user_rank >= command_rank:
            return True
        await message.answer("Недостаточно прав для использования комманды")

