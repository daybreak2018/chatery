__author__ = 'shaurya'

import os
from abc import abstractmethod


class DatabaseTable(object):
    """"Abstract DB Model specifying the required methods """
    @abstractmethod
    def create_schema_query(self):
        pass

    @abstractmethod
    def empty_database_content(self):
        pass

    @abstractmethod
    def delete_database(self):
        pass

    @abstractmethod
    def get_insert_query(self):
        pass

    @abstractmethod
    def get_update_query(self):
        pass


class MessageTable(DatabaseTable):
    """DB Model to specify the message table in DB"""
    def __init__(self,dbname,path):
        if dbname[-3:]!=".db":
            dbname += ".db"
        self.dbname = dbname
        self.path = os.path.join(path,dbname)

        self._createquery = """
            CREATE TABLE MESSAGES (
                username	TEXT,
                message	TEXT,
                created	TEXT
            )
        """

        self._insert_query = """
            INSERT INTO MESSAGES(username,message,created)
             VALUES (?,?,?)"""

        self._drop_all_rows = """
            DELETE FROM CATEGORY
        """

        self._get_all_rows = "SELECT * FROM MESSAGES"

        self._get_limited_rows = "SELECT * FROM MESSAGES LIMIT 1000"

    def create_schema_query(self):
        return self._createquery

    def empty_database_query(self):
        return self._drop_all_rows

    def get_insert_query(self):
        return self._insert_query

    def get_get_query(self):
        return self._get_all_rows

    def get_limited_get_query(self):
        return self._get_limited_rows