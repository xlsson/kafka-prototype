#!/usr/bin/env python3

"""
Mockdata creator for SQL Server database
"""

import os
from errors import MissingEnvironmentVariables
from job import Job

class Mocker():
    """ Singleton class for Mocker """

    def __init__(self):
        """ Instantiate a Mocker object """

        self.job = None
        self.scenario = None
        self.cfg = {}

        try:
            self.cfg = {
                "hostname": os.environ['DBHOSTNAME'],
                "port": os.environ['DBPORT'],
                "sql_server_name": os.environ['SERVERNAME'],
                "db_name": os.environ['DBNAME'],
                "db_table": os.environ['DBTABLE'],
                "db_user": os.environ['DBUSER'],
                "db_password": os.environ['DBPASSWORD'],
                "mockdata": os.environ['MOCKDATA']
            }
            self.scenario_name = os.environ['SCENARIO']

        except MissingEnvironmentVariables:
            print("Failed to read one or more environment variables")

    def create_job(self):
        """
        Scenarios with the parameters:
        - job duration (seconds)
        - batch size
        - time between inserts (seconds)

        The scenarios represent certain conditions under which the system should be tested

        std = standard
        bur = burst
        """
        scenarios = {
            "std": (200, 3, 2),
            "bur": (360, 500, 60)
        }

        job_duration, rows_per_batch, time_between_batches = scenarios[self.scenario_name]

        self.job = Job(self.cfg, self.scenario_name, job_duration, rows_per_batch, time_between_batches)
        

if __name__ == '__main__':
    mocker = Mocker()
    mocker.create_job()
    mocker.job.start()