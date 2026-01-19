# config.py
import pymysql
import os

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="ecommerce_db"
)