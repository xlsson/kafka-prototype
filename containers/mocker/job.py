#!/usr/bin/env python3

"""
Job class for mockdata
"""
import json
import datetime
import time
import pymssql
import random
from errors import ConnectError, TransactionError

class Job():

    def __init__(self, cfg, scenario_name, job_duration, rows_per_batch, time_between_batches):
        """ Instantiate a Job object """

        self.host = cfg["hostname"]
        self.port = cfg["port"]
        self.server = cfg["sql_server_name"]
        self.database = cfg["db_name"]
        self.table = cfg["db_table"]
        self.user = cfg["db_user"]
        self.password = cfg["db_password"]

        self.connection = None
        self.cursor = None

        self.scenario_name = scenario_name
        self.job_duration = job_duration
        self.rows_per_batch = rows_per_batch
        self.time_between_batches = time_between_batches
        self.nr_of_batches = int(job_duration / time_between_batches)

        self.mockdata = self._load_mockdata(cfg["mockdata"])
        self.read_counter = 0
        self.read_id = random.randint(0, 2147483647)

    def _load_mockdata(self, filename):
        mockdata = []

        with open(filename, encoding='utf-8-sig') as f:
            mockdata = json.load(f)

        return mockdata    

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
        Metadata fields:

        LastMinute = total nr_of_batches
        Markup = current batch_nr
        AktionsRabatt = rows_per_batch
        AktionsAufschlag = row_nr of the  current batch

        UnterkunftUuid = scenario name
        PartnerId = 0 or above, nr of reuses of the same source data, makes row unique

        ZimmerUuid = creation time (mmddHHMMSS = month, date, hours, minutes, seconds)
        IstSkipassInklusive = true/false if this is the last row of the last bath = scenario is done
        """

        mockdata_dict = self.mockdata[self.read_counter].copy()

        print(f"read_counter: {self.read_counter}, dict: {mockdata_dict}")

        # Remove Abreisedatum key+value (generated from two other values)
        mockdata_dict.pop("Abreisedatum")

        # Add metadata
        mockdata_dict['LastMinute'] = self.nr_of_batches
        mockdata_dict['Markup'] = batch_nr

        mockdata_dict['AktionsRabatt'] = self.rows_per_batch
        mockdata_dict['AktionsAufschlag'] = row_nr

        mockdata_dict['UnterkunftUuid'] = self.scenario_name
        
        creation_time = datetime.datetime.now().strftime('%m%d%H%M%S')
        mockdata_dict['ZimmerUuid'] = creation_time

        # Set last_row to True if this is the last row of the last batch
        is_last_row = False
        if ((batch_nr + 1) == self.nr_of_batches) and ((row_nr +1) == self.rows_per_batch):
            is_last_row = True
        mockdata_dict['IstSkipassInklusive'] = is_last_row

        # If required nr of rows exceeds the source mockdata rows, reuse the rows, but make them unique
        # by setting the read_id (in the PartnerId field) to a random value of 0 to 2147483647
        if (self.read_counter + 1) == len(self.mockdata):
            self.read_id = random.randint(0, 2147483647)
            self.read_counter = -1
        
        mockdata_dict['PartnerId'] = self.read_id
        
        self.read_counter += 1

        values = []
        for key in mockdata_dict:
            values.append(mockdata_dict[key])

        mockdata_row = tuple(values)

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
        sql_statement = 'INSERT INTO ' + self.table + ' VALUES (%d, %s, %d, %s, %d, %d, %s, %d, %d, %d, %d, %s, %s, %s, %d, %s, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %d, %s, %s)'

        print(batch)
        
        try:
            self.cursor.executemany(sql_statement, batch)
            self.connection.commit()

        except TransactionError:
            print('The transaction could not be completed')
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
            print(f'Insert batch nr {batch_nr + 1} of {self.nr_of_batches}')
            if batch_nr < (self.nr_of_batches - 1):
                print(f'Waiting {self.time_between_batches} seconds.')
                time.sleep(self.time_between_batches)

        return self._close_connection()