import schemify.db as db

def testConnect():
    connection = db.connect()

def testListTables():
    connection = db.connect()
    tables = db.listTables(connection, 'public')
    print(tables)

def testCreateTable():
    connection = db.connect()
    db.createTable(connection, 'demo')
    tables = db.listTables(connection, 'public')
    print(f"Tables:{tables}")
