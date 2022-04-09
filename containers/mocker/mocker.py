#!/usr/bin/env python3

"""
Mockdata creator for SQL Server database
"""

import os
import pymssql

def connect(hostname, port, sql_server_name, db_name, db_user, db_password):
    conn = pymssql.connect(
        host=hostname,
        port=port,
        server=sql_server_name,
        database=db_name,
        user=db_user,
        password=db_password
    )
    # conn = pymssql.connect(sql_server_name, db_user, db_password, db_name)
    cursor = conn.cursor(as_dict=True)

    cursor.execute('SELECT * FROM persons')
    for row in cursor:
        print(row)

    conn.close()

try:
    # Use docker compose environment variables. Will exist if started from docker-compose.
    hostname = os.environ['DBHOSTNAME']
    port = os.environ['DBPORT']
    sql_server_name = os.environ['SERVERNAME']
    db_name = os.environ['DBNAME']
    db_user = os.environ['DBUSER']
    db_password = os.environ['DBPASSWORD']

    print("Using environment parameters")

    connect(hostname, port, sql_server_name, db_name, db_user, db_password)

except:
    # Otherwise do nothing
    print("Failed to get environment params: exiting")