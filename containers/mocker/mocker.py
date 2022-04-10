#!/usr/bin/env python3

"""
Mockdata creator for SQL Server database
"""

import os
import random
import string
import time
import pymssql
from errors import MissingEnvironmentVariables, ConnectError, TransactionError

class Mocker():
    """ Singleton class for Mocker """

    def __init__(self):
        """ Instantiate a Mocker object """

        self.connection = None
        self.cursor = None

        try:
            self.hostname = os.environ['DBHOSTNAME']
            self.port = os.environ['DBPORT']
            self.sql_server_name = os.environ['SERVERNAME']
            self.db_name = os.environ['DBNAME']
            self.db_table = os.environ['DBTABLE']
            self.db_user = os.environ['DBUSER']
            self.db_password = os.environ['DBPASSWORD']

        except MissingEnvironmentVariables:
            print("Failed to read one or more environment variables")

    def _connect(self):
        try:
            connection = pymssql.connect(
                host=self.hostname,
                port=self.port,
                server=self.sql_server_name,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )

        except ConnectError:
            print("The transaction could not be completed")

        self.connection = connection

        return connection

    def _close_connection(self):
        return self.connection.close()

    def _set_cursor(self):
        self.cursor = self.connection.cursor(as_dict=True)
        return self.cursor

    def _close_cursor(self):
        return self.cursor.close()

    def _create_row(self):
        """
        Create a unique row (only one value will be unique)
        """
        # To comply with primary key contraint, a random string is generated (1/281474976710656 chance of being identical)
        random_string = ''.join(random.choices(string.ascii_uppercase, k=12))

        row_tuple = (1, random_string, 6053, 'TRHM30', 777, 51, 'EUR', 0, 19087, 3, 3, 'ctg=', 'VH4=',
            'Hlo=', 1, 'AA==', -79257, 0, 0, 0, 0, 294, 578537800, 1397609632, 0, 5, 0, 0, 0, None, None)
        
        return row_tuple

    def _create_batch(self, batch_size):
        """
        Create a list of 'size' nr. of rows to insert in one transaction
        """
        batch = []

        # Data types based on:
        # https://docs.microsoft.com/en-us/dotnet/framework/data/adonet/sql-server-data-type-mappings
        for i in range(batch_size):
            row_tuple = self._create_row()
            batch.append(row_tuple)

        # Change the value for one column in the last row
        # last_row = batch[batch_size-1]
        # etc.

        return batch

    def _insert_batch(self, batch_size=1):
        """
        Perform a SQL insert transaction of size nr. of rows
        """
        self._set_cursor()

        batch = self._create_batch(batch_size)

        # %d = number, %s = string
        sql_statement = "INSERT INTO " + self.db_table + " VALUES (%d, %s, %d, %s, %d, %d, %s, %d, %d, %d, %d, %s, %s, %s, %d, %s, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d)"

        print(batch)
        
        try:
            self.cursor.executemany(sql_statement, batch)
            self.connection.commit()

        except TransactionError:
            print("The transaction could not be completed")
            self.connection.rollback()

        finally:
            self._close_cursor()

    def start_insert_job(self, nr_of_inserts, batch_size, time_between_inserts):
        """
        Perform given nr (nr_of_inserts) of SQL operations, each insert 'batch_size' nr of rows,
        at intervals of 'time_between_inserts' seconds.
        """

        self._connect()

        for i in range(nr_of_inserts):
            self._insert_batch(batch_size)
            print(f"Will wait {time_between_inserts} seconds.")
            time.sleep(time_between_inserts)

        return self._close_connection()

if __name__ == '__main__':
    mocker = Mocker()
    mocker.start_insert_job(
        nr_of_inserts=10,
        batch_size=2,
        time_between_inserts=1
    )