from config import settings
from vkbottle import Bot
from handlers import labelers

bot = Bot(token=settings.BOT_TOKEN)

for labeler in labelers:
    print("loading labeler")
    bot.labeler.load(labeler)