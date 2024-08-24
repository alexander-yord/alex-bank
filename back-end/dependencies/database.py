import mysql.connector as sql
from mysql.connector import pooling
import configparser
import sys
import os


try:
    cfile = configparser.ConfigParser()  # reads credentials from the config.ini file (git ignored)
    cfile.read(os.path.join(sys.path[0], "config.ini"))

    dbconfig = {
        "user": cfile["DATABASE"]["DB_USER"],
        "password": cfile["DATABASE"]["DB_PASS"],
        "host": cfile["DATABASE"]["DB_HOST"],
        "database": cfile["DATABASE"]["DB_NAME"],
        "pool_name": "mypool",
        "pool_size": 5,
        "pool_reset_session": True,  # Resets session state before returning connection to the pool
    }

except KeyError:
    cfile = configparser.ConfigParser()  # reads credentials from the config.ini file (git ignored)
    cfile.read(os.path.join(sys.path[0], "../config.ini"))


connection_pool = sql.pooling.MySQLConnectionPool(**dbconfig)


def get_db_connection():
    return connection_pool.get_connection()


def connect():
    try:
        cfile = configparser.ConfigParser()  # reads credentials from the config.ini file (git ignored)
        cfile.read(os.path.join(sys.path[0], "config.ini"))

        cnx = sql.connect(host=cfile["DATABASE"]["DB_HOST"],
                          user=cfile["DATABASE"]["DB_USER"],
                          password=cfile["DATABASE"]["DB_PASS"],
                          database=cfile["DATABASE"]["DB_NAME"])
    except KeyError:
        cfile = configparser.ConfigParser()  # reads credentials from the config.ini file (git ignored)
        cfile.read(os.path.join(sys.path[0], "../config.ini"))

        cnx = sql.connect(host=cfile["DATABASE"]["DB_HOST"],
                          user=cfile["DATABASE"]["DB_USER"],
                          password=cfile["DATABASE"]["DB_PASS"],
                          database=cfile["DATABASE"]["DB_NAME"])
    except sql.Error as err:
        if err.errno == sql.errorcode.ER_ACCESS_DENIED_ERROR:
            print("User authorization error")
        elif err.errno == sql.errorcode.ER_BAD_DB_ERROR:
            print("Database doesn't exist")
        raise err
    cursor = cnx.cursor(buffered=True)
    return cnx, cursor


def verify_connection():  # reconnects to the database if the connection has been lost
    try:  # tests the connection
        _ = cnx.cursor()  # meaningless statement to test the connection
    except sql.Error:  # if it is not working, it will reconnect
        connect()


cnx, cursor = connect()