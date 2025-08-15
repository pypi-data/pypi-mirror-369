import sqlite3


class DutCacher:

    def __init__(self, local_db: str, create_schema: bool = False, clean_up: bool = True):
        self.__connection: sqlite3.Connection = None
        self.__cursor: sqlite3.Cursor = None
        self.__schema = """
            CREATE TABLE device_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device TEXT NOT NULL,
                command TEXT NOT NULL,
                output TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """
        self.local_db = local_db
        self.create_schema = create_schema
        self.__connect()
        if self.create_schema:
            self.__create_schema()
        if clean_up:
            self.__cleanup()

    def __connect(self):
        if self.__connection is None:
            try:
                self.__connection = sqlite3.connect(self.local_db)
                self.__cursor = self.__connection.cursor()
            except Exception as e:
                print(f"Exception while connecting to sqlite DB : {e}")

    def __create_schema(self):
        try:
            self.__cursor.execute(self.__schema)
            self.__connection.commit()
        except Exception as e:
            print(f"Exception while creating schema on sqlite : {e}")

    def __cleanup(self):
        try:
            self.__cursor.execute("DELETE FROM device_cache WHERE timestamp <= datetime('now', '-1 hour')")
            self.__connection.commit()
        except Exception as e:
            print(f"Error while cleaning up the database {e}")

    def get_cache(self, device: str, command: str):
        try:
            self.__cursor.execute(f"SELECT output FROM device_cache WHERE device = '{device}' AND command = '{command}' AND timestamp >= datetime('now', '-1 hour') ORDER BY timestamp")
            result = self.__cursor.fetchall()
            if len(result) == 0:
                return None
            else:
                return result[0][0]
        except Exception as e:
            print(f"Error while fetching data from sqlite {e}")

    def put_many_cache(self, multiple_records: []):
        try:
            self.__cursor.executemany("INSERT INTO device_cache (device, command, output) VALUES (?, ?, ?)", multiple_records)
            self.__connection.commit()
        except Exception as e:
            print(f"Error while inserting data into sqlite {e}")

    def put_single_query(self, query: str):
        try:
            self.__cursor.execute(query)
            self.__connection.commit()
        except Exception as e:
            print(f"Error while inserting data into sqlite {e}")

    def put_cache(self, device: str, command: str, output: str):
        try:
            self.__cursor.execute(f"INSERT INTO device_cache (device, command, output) values (?, ?, ?)", (device, command, output))
            self.__connection.commit()
        except Exception as e:
            print(f"Error while inserting data into sqlite {e}")

    def get_cursor(self):
        return self.__cursor

