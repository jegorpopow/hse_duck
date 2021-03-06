import psycopg

class Connection(object):
    def __init__(self, line):
        self.name = line
        try:
            self.connection = psycopg.connect(line)
            print(f"Connceted with {self.name} database")
        except:
            print(f"Connection with database {self.name} !!!! failed...")
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
