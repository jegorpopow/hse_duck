import psycopg

class Connection(object):
    def __init__(self, dbname, user="postgres", password=None):
        self.name = dbname
       #print(f"dbname={dbname} user={user} " + f"password={password}" if password else "")
        try:
            self.connection = psycopg.connect(f"dbname={dbname} user={user} " + f"password={password}" if password else "")
            print(f"Connceted with {dbname} database")
        except:
            print(f"Connection with database {dbname} failed...")
            self.connection = None
    def execute(self, query):
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                self.connection.commit()
    def fetch(self, query):
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                self.connection.commit()
                return cursor.fetchall()
    def __del__(self):
        if self.connection:
            self.connection.close()
            print(f"connection with {self.name} database closed")
