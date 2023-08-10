import mysql.connector 

dataBase = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = 'password'
)

# to create curser obj

cursorObject = dataBase.cursor()

#create a database
cursorObject.execute("CREATE DATABASE haystack")

print("created done!")