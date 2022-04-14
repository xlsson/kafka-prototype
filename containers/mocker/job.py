#!/usr/bin/env python3

"""
Job class for mockdata
"""
import datetime
import random
import string
import time
import pymssql
from errors import ConnectError, TransactionError

class Job():

    def __init__(self, cfg, scenario_name, job_duration, rows_per_batch, time_between_batches):
        """ Instantiate a Job object """

        self.connection = None
        self.cursor = None

        self.scenario_name = scenario_name
        self.job_duration = job_duration
        self.rows_per_batch = rows_per_batch
        self.time_between_batches = time_between_batches
        self.nr_of_batches = int(job_duration / time_between_batches)

        self.host = cfg["hostname"]
        self.port = cfg["port"]
        self.server = cfg["sql_server_name"]
        self.database = cfg["db_name"]
        self.table = cfg["db_table"]
        self.user = cfg["db_user"]
        self.password = cfg["db_password"]

    def _connect(self):

        try:
            connection = pymssql.connect(
                host=self.host,
                port=self.port,
                server=self.server,
                database=self.database,
                user=self.user,
                password=self.password
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

    def _create_row(self, row_nr, batch_nr):
        """
        Create a unique row
        
        Metadata fields:

        Field #2 ("Buchungscode", varchar(12)):
        Part of combined primary key.
        Timestamp marking the creation time of the row: mmddHHMMSS
        m = month, d = date, H = hour, M = minute, S = second

        Field #4 ("Zimmercode", varchar(6)):
        A randomized string to comply with combined primary key constraint.
        Practically unique. 52^6 = 1/19770609664 risk of being identical.

        Field #7 ("WaehrungISO", varchar(3)):
        Identifier for the mockdata scenario

        Field #8 ("PartnerId", int): current row_nr in the current batch
        Field #23 ("WebseitePreis", int): number of rows_per_batch

        Field #24 ("PreiszeileId", int): batch_nr of the job
        Field #25 ("PreisId", int): total nr_of_batches of the job

        Field #30 ("MarkupAktion", tinyint):
        Default 0.
        Is set to 1 for the last row in the last batch.

        Other important fields:

        Field #1 ("ProduktId", tinyint):
        1 = SnowTrex, 2 = HolidayTrex, 5 = SportsTrex

        """

        creation_time = datetime.datetime.now().strftime("%m%d%H%M%S")

        random_string = ''.join(random.choices(string.ascii_letters, k=6))

        last_row_flag = 0
        if (self.nr_of_batches - (batch_nr + 1) + self.rows_per_batch - (row_nr + 1)) == 0:
            last_row_flag = 1
        
        mockdata_row = (1, creation_time, 6053, random_string, 28322, 51, self.scenario_name, row_nr + 1, '2022-04-10', 2,2, 269.00, 191.30, 77.70, 1, 0.00, 
	                    '1753-01-01', 0, 0, 0, 0, self.rows_per_batch, batch_nr + 1, self.nr_of_batches, 0, 0, 0, 0, last_row_flag, None, None)
        
        return mockdata_row

    def _create_batch(self, batch_nr):
        """
        Create a list of 'rows_per_batch' nr. of rows to insert in one insert transaction
        """
        batch = []

        # Data types based on:
        # https://docs.microsoft.com/en-us/dotnet/framework/data/adonet/sql-server-data-type-mappings
        for row_nr in range(self.rows_per_batch):
            mockdata_row = self._create_row(row_nr, batch_nr)
            batch.append(mockdata_row)

        return batch

    def _insert_batch(self, batch_nr):
        """
        Perform a SQL insert transaction of 'rows_per_batch' nr. of rows
        """
        self._set_cursor()

        batch = self._create_batch(batch_nr)

        # Legend: %d = number, %s = string
        sql_statement = "INSERT INTO " + self.table + " VALUES (%d, %s, %d, %s, %d, %d, %s, %d, %d, %d, %d, %s, %s, %s, %d, %s, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d)"

        print(batch)
        
        try:
            self.cursor.executemany(sql_statement, batch)
            self.connection.commit()

        except TransactionError:
            print("The transaction could not be completed")
            self.connection.rollback()

        finally:
            self._close_cursor()

    def start(self):
        """
        Perform SQL inserts during a given timeframe (job_duration). At each insert, insert 'rows_per_batch' 
        nr of rows, at intervals of 'time_between_batches' seconds.
        """

        self._connect()

        for batch_nr in range(self.nr_of_batches):
            self._insert_batch(batch_nr)
            print(f"Insert batch nr {batch_nr + 1} of {self.nr_of_batches}")
            if batch_nr < (self.nr_of_batches - 1):
                print(f"Waiting {self.time_between_batches} seconds.")
                time.sleep(self.time_between_batches)

        return self._close_connection()