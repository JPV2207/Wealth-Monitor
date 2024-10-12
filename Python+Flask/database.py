import pymysql
 
hostname = 'localhost'
user = 'root'
password = 'root'
 
# Initializing connection
db = pymysql.connect(
    host=hostname,
    user=user,
    password=password,
    charset='utf8'  # Specify the character set here
)
 
# Creating cursor object
cursor = db.cursor()
 
# Executing SQL query
cursor.execute("CREATE DATABASE IF NOT EXISTS WealthMonitorDemo")
cursor.execute("SHOW DATABASES")
 
# Displaying databases
for databases in cursor:
    print(databases)
 
# Closing the cursor and connection to the database
cursor.close()
db.close()