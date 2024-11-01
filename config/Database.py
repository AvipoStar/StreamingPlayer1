import mysql.connector


def getConnection():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="MySQL_Password01!",
        database="test"
    )
    return db
