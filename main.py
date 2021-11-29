import telebot
import parse

from user_info import UserInfo
from stocking_info import StockingFetcher

bot_token = input("Please input bot token:")
db_user = input("database user:")
db_password = input("database password:") 


userdb = UserInfo(user = db_user, password=db_password)
stocking_fetcher = StockingFetcher()

with open("help.info", "r") as hlp_source:
    hlp = "".join(hlp_source.readlines())

bot = telebot.TeleBot(bot_token, parse_mode=None)


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.reply_to(message, hlp)


@bot.message_handler(commands=["ping"])
def send_ping(message):
    bot.reply_to(message, "pong")


@bot.message_handler(commands=["start"])
def send_start_message(message):
    bot.reply_to(message, f"Nice to see you, @{message.from_user.username}")
    if not userdb.user(message.from_user.id).exists:
        userdb.create_user(message.from_user.id)
        bot.reply_to(message, "First time? amybe you need /help?")
    else:
        bot.reply_to(message, "Welcome back")


@bot.message_handler(commands=["about"])
def send_about(message):
    print(message.text)
    symbol = parse.parse_symbol(message.text)
    if symbol is not None:
        print(symbol)
        ticker = stocking_fetcher.fetch(symbol)
        if ticker.exists:
            bot.reply_to(message, ticker.about())
        else:
            bot.reply_to(message, f"Can't find symbol {symbol}.")
    else:
        bot.reply_to(
            message, "Can`t find this symbol, print something like '\\info $TSLA'."
        )


@bot.message_handler(commands=["buy"])
def buy(message):
    user = userdb.user(message.from_user.id)
    if not user.exists:
        bot.reply_to(message, "Please log in using /start")
    else:
        symbol = parse.parse_symbol(message.text)
        money = parse.parse_sum(message.text)
        if symbol is not None and money is not None:
            ticker = stocking_fetcher.fetch(symbol)
            if ticker.exists:
                bot.reply_to(message, user.buy(ticker, money))
            else:
                bot.reply_to(message, "This symbol doesn't exist")
        else:
            bot.reply_to(
                message,
                "Please follow template '/buy $SYMBOL 0.00USD'. You may add extra symbols.",
            )

@bot.message_handler(commands=["sell"])
def sell(message):
    user = userdb.user(message.from_user.id)
    if not user.exists:
        bot.reply_to(message, "Please log in using /start")
    else:
        symbol = parse.parse_symbol(message.text)
        money = parse.parse_sum(message.text)
        if symbol is not None and money is not None:
            ticker = stocking_fetcher.fetch(symbol)
            if ticker.exists:
                bot.reply_to(message, user.sell(ticker, money))
            else:
                bot.reply_to(message, "This symbol doesn't exist")
        else:
            bot.reply_to(
                message,
                "Please follow template '/sell $SYMBOL 0.00USD'. You may add extra symbols.",
            )

@bot.message_handler(commands=["short"])
def short(message):
    user = userdb.user(message.from_user.id)
    if not user.exists:
        bot.reply_to(message, "Please log in using /start")
    else:
        symbol = parse.parse_symbol(message.text)
        money = parse.parse_sum(message.text)
        if symbol is not None and money is not None:
            ticker = stocking_fetcher.fetch(symbol)
            if ticker.exists:
                bot.reply_to(message, user.short(ticker, money))
            else:
                bot.reply_to(message, "This symbol doesn't exist")
        else:
            bot.reply_to(
                message,
                "Please follow template '/short $SYMBOL 0.00USD'. You may add extra symbols.",
            )

@bot.message_handler(commands=["close"])
def close(message):
    user = userdb.user(message.from_user.id)
    if not user.exists:
        bot.reply_to(message, "Please log in using /start")
    else:
        symbol = parse.parse_symbol(message.text)
        if symbol is not None:
            ticker = stocking_fetcher.fetch(symbol)
            if ticker.exists:
                bot.reply_to(message, user.close(ticker))
            else:
                bot.reply_to(message, "This symbol doesn't exist")
        else:
            bot.reply_to(
                message,
                "Please follow template '/close $SYMBOL '. You may add extra symbols.",
            )


@bot.message_handler(commands=["closeshort"])
def closeshort(message):
    user = userdb.user(message.from_user.id)
    if not user.exists:
        bot.reply_to(message, "Please log in using /start")
    else:
        symbol = parse.parse_symbol(message.text)
        if symbol is not None:
            ticker = stocking_fetcher.fetch(symbol)
            if ticker.exists:
                bot.reply_to(message, user.closeshort(ticker))
            else:
                bot.reply_to(message, "This symbol doesn't exist")
        else:
            bot.reply_to(
                message,
                "Please follow template '/close $SYMBOL '. You may add extra symbols.",
            )



@bot.message_handler(commands=["money"])
def send_money(message):
    user = userdb.user(message.from_user.id)
    if not user.exists:
        bot.reply_to(message, "Please log in using /start")
    else:
        bot.reply_to(message, f"Your cash is {round(user.money(), 2)}USD")
        

@bot.message_handler(commands=["reset"])
def reset(message):
    user = userdb.user(message.from_user.id)
    if not user.exists:
        bot.reply_to(message, "Please log in using /start")
    else:
        money = parse.parse_sum(message.text)
        if money is not None:
            user.reset(new_sum=money)
        else:
            bot.reply_to(
                message,
                "Please follow template '/reset 0.00USD'. You may add extra symbols.",
            )


@bot.message_handler(commands=["open"])
def send_open(message):
    user = userdb.user(message.from_user.id)
    if not user.exists:
        bot.reply_to(message, "Please log in using /start")
    else:
        positions = user.open()
        answer = "your open positions are:\n\n\n"
        total = 0
        for position in positions:
            answer += f"${position[0]} --- {round(position[1], 2)} = {round(position[1] * stocking_fetcher.fetch(position[0]).price(), 2)}USD\n\n"
            total += position[1] * stocking_fetcher.fetch(position[0]).price()
        answer += f"\n\nTotal:    {round(total, 2)}USD\nCash:    {round(user.money(), 2)}USD" 
        bot.reply_to(
                message,
                answer  
            )


@bot.message_handler(commands=["shorts"])
def send_shorts(message):
    user = userdb.user(message.from_user.id)
    if not user.exists:
        bot.reply_to(message, "Please log in using /start")
    else:
        positions = user.shorts()
        answer = "your open shorts are:\n\n\n"
        total = 0
        for position in positions:
            answer += f"${position[0]} --- {round(position[1], 2)} = {round(position[1] * stocking_fetcher.fetch(position[0]).price(), 2)}USD\n\n"
            total += position[1] * stocking_fetcher.fetch(position[0]).price()
        answer += f"\n\nTotal:    {round(total, 2)}USD" 
        bot.reply_to(
                message,
                answer  
            )

@bot.message_handler(func=lambda m: True)
def send_unknown_message(message):
    bot.reply_to(message, f"Sorry, I can't understand you")

bot.infinity_polling()
