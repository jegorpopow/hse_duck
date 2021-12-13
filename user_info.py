import os
from stocking_info import StockingFetcher
from database_common import Connection

TABLE_DROP_QUERY = """
DROP TABLE IF EXISTS users;
"""

TABLE_CREATION_QUERY = """
CREATE TABLE users (
    telegram_id integer unique primary key,
    money real,
    race integer,
    name text
);
"""

stocking = StockingFetcher()
try:
    with open("database.cfg", "r") as f:
        db_line = f.readline().strip()
except:
     db_line = os.envron.get("database_url")
class User(object):
    def __init__(self, db_connection, telegram_id):
        self.connection = db_connection
        fetched = self.connection.fetch(f"SELECT * FROM users WHERE telegram_id={telegram_id};")
        self.telegram_id = telegram_id 
        if len(fetched) != 0:
            self.exists = True
            self.info = fetched[0]
        else:
            self.exists = False
            self.info = None
    def race(self):
        if self.exists:
            return self.info[2]
        else:
            return None
    def money(self):
        if self.exists:
            print(self.info[1])
            return self.info[1]
        else:
            return None
    def telegram_id(self):
        if self.exists:
            return self.info[0]
        else:
            return None
    def username(self):
        return self.info[3]
    def reset(self, new_sum=0):
        self.connection.execute(f"TRUNCATE TABLE user{self.telegram_id}")
        self.connection.execute(f"TRUNCATE TABLE user{self.telegram_id}_shorts")
        self.connection.execute(f"UPDATE users SET money = {new_sum} WHERE telegram_id = {self.telegram_id}")
    def buy(self, ticker, money):
        if money > self.money():
            return f"I haven't {money}USD."
        amount = money / ticker.price()
        self.connection.execute(f"UPDATE users SET money = {self.info[1] - money} WHERE telegram_id = {self.telegram_id}")
        self.info = self.connection.fetch(f"SELECT * FROM users WHERE telegram_id = {self.telegram_id};")
        position = self.connection.fetch(f"SELECT * FROM user{self.telegram_id} WHERE symbol = '{ticker.symbol}';")
        if len(position) == 0:
            self.connection.execute(f"INSERT INTO user{self.telegram_id} (symbol, amount) VALUES ('{ticker.symbol}', {amount});")
        else:
            self.connection.execute(f"UPDATE user{self.telegram_id} SET amount = {position[0][1] + amount} WHERE symbol = '{ticker.symbol}'")
        return f"${ticker.symbol} succesfully bought"
    def sell(self, ticker, money):
        position = self.connection.fetch(f"SELECT * FROM user{self.telegram_id} WHERE symbol = '{ticker.symbol}';")
        if len(position) == 0:
            return f"You haven't any ${ticker.symbol}"
        position = position[0]
        amount = money / ticker.price()
        if amount > position[1]:
            return f"I haven't {amount} ${ticker.symbol}. (Maybe there some problems with floating numbers. Try to clode this position)"
        if abs(amount - position[1]) < 0.01:
            return self.close(ticker)
        self.connection.execute(f"UPDATE users SET money = {self.info[1] + money} WHERE telegram_id = {self.telegram_id}")
        self.info = self.connection.fetch(f"SELECT * FROM users WHERE telegram_id = {self.telegram_id};")
        self.connection.execute(f"UPDATE user{self.telegram_id} SET amount = {position[1] - amount} WHERE symbol = '{ticker.symbol}'")
        return f"You have received {round(ticker.price() * amount, 2)}USD selling ${ticker.symbol}" 
    def close(self, ticker):
        position = self.connection.fetch(f"SELECT * FROM user{self.telegram_id} WHERE symbol = '{ticker.symbol}';")
        if len(position) == 0:
            return f"You haven't any ${ticker.symbol}"
        position = position[0]
        self.connection.execute(f"UPDATE users SET money = {self.info[1] + ticker.price() * position[1]} WHERE telegram_id = {self.telegram_id}")
        self.connection.execute(f"DELETE FROM user{self.telegram_id} WHERE symbol = '{ticker.symbol}'")
        return f"You have received {round(ticker.price() * position[1], 2)}USD selling ${ticker.symbol}"    
    def open(self):
        return self.connection.fetch(f"SELECT * from user{self.telegram_id};")
    def shorts(self):
        return self.connection.fetch(f"SELECT * from user{self.telegram_id}_shorts;")
    def short(self, ticker, money):
        amount = money / ticker.price()
        position = self.connection.fetch(f"SELECT * FROM user{self.telegram_id}_shorts WHERE symbol = '{ticker.symbol}';")
        if len(position) != 0:
            return "You have already shorted ${ticker.symbol} close last short before"
        self.connection.execute(f"INSERT INTO user{self.telegram_id}_shorts (symbol, amount) VALUES ('{ticker.symbol}', {amount});")            
        self.connection.execute(f"UPDATE users SET money = {self.info[1] + money} WHERE telegram_id = {self.telegram_id}")
        self.info = self.connection.fetch(f"SELECT * FROM users WHERE telegram_id = {self.telegram_id};")
        return f"You have received {round(ticker.price() * amount, 2)}USD shorting ${ticker.symbol} don't forget to close short"         
    def closeshort(self, ticker):
        position = self.connection.fetch(f"SELECT * FROM user{self.telegram_id}_shorts WHERE symbol = '{ticker.symbol}';")
        if len(position) == 0:
            return f"You haven't shorted ${ticker.symbol}"
        position = position[0]
        money = position[1] * ticker.price()
        if money > self.money():
            return "You don't have enough cash to close this short"
        self.connection.execute(f"UPDATE users SET money = {self.info[1] - money} WHERE telegram_id = {self.telegram_id}")
        self.connection.execute(f"DELETE FROM user{self.telegram_id}_shorts WHERE symbol = '{ticker.symbol}'")
        return f"You successfully closed short"
    def contest_money(self):
        total =  self.info[1]
        opened = self.connection.fetch(f"SELECT * FROM user{self.telegram_id}")
        total += sum(stocking.fetch(position[0]).price() * position[1] for position in opened)
        shorts =  self.connection.fetch(f"SELECT * FROM user{self.telegram_id}_shorts")
        total -= sum(stocking.fetch(position[0]).price() * position[1] for position in shorts)
        return total

        
class UserInfo(object):
    def __init__(self):
        self.connection = Connection(db_line)
    def reset(self):
        self.connection.execute(TABLE_DROP_QUERY)
        self.connection.execute(TABLE_CREATION_QUERY)
    def create_user(self, telegram_id, name, money = 1000):
        self.connection.execute(f"DROP TABLE IF EXISTS user{telegram_id};")
        self.connection.execute(f"CREATE TABLE user{telegram_id} (symbol text, amount real);")
        self.connection.execute(f"DROP TABLE IF EXISTS user{telegram_id}_shorts;")
        self.connection.execute(f"CREATE TABLE user{telegram_id}_shorts (symbol text, amount real);")
        self.connection.execute(f"INSERT INTO users (telegram_id, money, race, name) VALUES ({telegram_id}, {money}, 0, '{name}');")
        print(f"Created user {telegram_id}")
        return self.user(telegram_id)
    def remove_user(self, telegram_id):
        if self.user(telegram_id).exists:
            self.connection.execute(f"DROP TABLE IF EXISTS user{telegram_id}_shorts;")        
            self.connection.execute(f"DROP TABLE IF EXISTS user{telegram_id};")
            self.connection.execute(f"DELETE FROM users WHERE telegram_id = {telegram_id}")
            print(f"Removed user {telegram_id}")
    def everybody(self):
        fetched = self.connection.fetch("SElECT * FROM users ")
        return sorted([User(self.connection, record[0]) for record in fetched], key = lambda user: user.contest_money())
    def safe_user(self, telegram_id):
        if not self.user(telegram_id).exists:
            self.create_user(telegram_id)
        return self.user(telegram_id)
    def user(self, telegram_id):
        return User(self.connection, telegram_id) 

if __name__ == "main":
    print("'", db_name, "'", sep="")
