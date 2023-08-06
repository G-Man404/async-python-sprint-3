import pymysql

try:
    import mysql.connector

    mysql_connector = mysql.connector
except:
    import pymysql

    mysql_connector = pymysql

mysql_connector.connect(user='root', password='root', host='xxx:3306', database='test')
