__author__ = 'shaurya'
import os
import sqlite3


class SQLiteDBManager(object):
    """Class to Manage DB Connections for SQLite Database """

    def __init__(self,db):
        self.db = db
        self.create_and_connect()

    def create_and_connect(self):
        if not os.path.isdir(os.path.dirname(self.db.path)):
            os.mkdir(os.path.dirname(self.db.path))
            self.construct_structure()

    def run_query(self,query,vals):
        with sqlite3.connect(self.db.path) as connection:
            return_value = connection.cursor().execute(query,vals)
            self.commit_changes(connection)
        return  return_value

    def commit_changes(self,connection):
        connection.commit()

    def clean_content(self):
        with sqlite3.connect(self.db.path) as connection:
            connection.cursor().execute(self.db.empty_database_query())
            self.commit_changes(connection)

    def construct_structure(self):
        with sqlite3.connect(self.db.path) as connection:
            connection.cursor().execute(self.db.create_schema_query())
            self.commit_changes(connection)