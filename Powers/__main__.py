from Config import TOKEN
from Powers import telethn
from Powers.bot_class import Nikki

if __name__ == "__main__":
    telethn.start(bot_token=TOKEN)
    Nikki.run()
