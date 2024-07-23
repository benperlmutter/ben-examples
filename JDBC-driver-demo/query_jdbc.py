import json
import jaydebeapi

jdbc_url = "jdbc:mongodb://atlas-sql-669e8c7d4a90bf00e90be298-e1adf.a.query.mongodb.net/retail?ssl=true&authSource=admin"
driverName = "com.mongodb.jdbc.MongoDriver"
driverJar = "/Users/ben.perlmutter/Downloads/mongodb-jdbc-2.1.4.jar"

f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

db_username = pData["ben-demo-username"]
db_password = pData["ben-demo-password"]

conn = jaydebeapi.connect(driverName, jdbc_url, [db_username, db_password], driverJar)
curs = conn.cursor()
