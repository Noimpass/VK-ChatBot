import asyncio
import sys
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

from db import db
from dispatcher import bot

session = db.create_db()

def main() -> None:
    bot.run_forever()

if __name__ == "__main__":
    main()