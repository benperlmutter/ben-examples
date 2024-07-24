import json
import jaydebeapi

jdbc_url = "jdbc:mongodb://atlas-sql-669e8c7d4a90bf00e90be298-e1adf.a.query.mongodb.net/:27017?ssl=true&authSource=admin"
driver_name = "com.mongodb.jdbc.MongoDriver"
driver_jar = "/Users/ben.perlmutter/Downloads/mongodb-jdbc-2.1.4-all.jar"

f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

db_username = pData["ben-demo-username"]
db_password = pData["ben-demo-password"]

print('here')
conn = jaydebeapi.connect(driver_name, jdbc_url, [db_username, db_password], driver_jar,)
print('also here')
curs = conn.cursor()
curs.execute("select * from retail.orders")
curs.fetchall()

# with jaydebeapi.connect(driver_name, jdbc_url)


# with jaydebeapi.connect("org.hsqldb.jdbcDriver",
# ...                         "jdbc:hsqldb:mem:.",
# ...                         ["SA", ""],
# ...                         "/path/to/hsqldb.jar",) as conn:
# ...     with conn.cursor() as curs:
# ...         curs.execute("select count(*) from CUSTOMER")
# ...         curs.fetchall()
# [(1,)]