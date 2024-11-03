from . import commands, on_invite, rp_commands, on_new_message, capcha, buy_items

labelers = [commands.chat_labeler, on_invite.bl, rp_commands.chat_labeler, on_new_message.bl,buy_items.chat_labeler, capcha.bl]

__all__ = ["labelers"]