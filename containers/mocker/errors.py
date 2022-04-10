"""
Module for user defined exception errors for mocker.py
"""

class Error(Exception):
    """ Base class for own exceptions """

class MissingEnvironmentVariables(Error):
    """ Raised when one or more environment variables are missing """

class ConnectError(Error):
    """ Raised when a SQL Server connection could not be established """

class TransactionError(Error):
    """ Raised when a transaction could not be completed """