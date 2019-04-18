import argparse
import glob
import itertools
import os
import schemify.db as db
import sys
import yaml

def argParser():
    parser = argparse.ArgumentParser("schemify")
    parser.add_argument('-H','--host',dest='host',default=os.environ.get('POSTGRES_HOST','localhost'))
    parser.add_argument('-p','--port',dest='port',default=os.environ.get('POSTGRES_PORT','5432'))
    parser.add_argument('-U','--user',dest='user',default=os.environ.get('POSTGRES_USER','schemify'))
    parser.add_argument('-P','--password',dest='password',default=os.environ.get('POSTGRES_PASSWORD','schemify'))
    parser.add_argument('-d','--database',dest='database',default=os.environ.get('POSTGRES_DB','schemify'))
    parser.add_argument('-s','--schema',dest='schema',default=os.environ.get('SCHEMA_DIR','./demo/schema'))
    parser.add_argument('-n','--dry-run',dest='dryRun',default=False,action='store_true')
    parser.add_argument('-v','--verbose',dest='verbose',default=False,action='store_true')
    return parser

def loadYaml(filename):
    with open(filename, 'r') as stream:
        return list(yaml.load_all(stream, Loader=yaml.SafeLoader))

def loadSchema(schemaDir):
    print(f"SchemaDirectory: {schemaDir} [Note:You can select a different schema directory with '-s']")
    schemaFiles = glob.glob(os.path.join(schemaDir,"*.schema.yml"))
    schemaLoL = [loadYaml(filename) for filename in schemaFiles]
    schema = list(itertools.chain(*schemaLoL))
    return schema

def migratorTableAddMissingColumns(args, connection, existingTable, desiredTable):
    schema  = desiredTable.get('schema','public')
    name = desiredTable['name']
    missingColumns = list(filter(lambda col: col['name'] not in existingTable['columns'], desiredTable['columns']))
    if len(missingColumns):
        sql = f"ALTER TABLE {schema}.{name} " + ",".join(["ADD COLUMN " + generateTableCreateColumn(column) for column in missingColumns])
        if args.verbose:
            print(f"SQL: {sql}")
        if args.dryRun:
            return
        db.execute(connection, sql)
        connection.commit()

def migratorTableAlter(args, connection, existingTable, desiredTable):
    migratorTableAddMissingColumns(args, connection, existingTable, desiredTable)

def columnLength(column):
    if 'length' in column:
        return f"({column['length']})"
    return ""

def generateTableCreateColumn(column):
    name = column['name']
    typeName = column['type']
    length = columnLength(column)
    return f"{name} {typeName}{length}"

def generateTableCreateColumns(desiredTable):
    return ", ".join([generateTableCreateColumn(column) for column in desiredTable['columns']])

def migratorTableCreate(args, connection, desiredTable):
    schema  = desiredTable.get('schema','public')
    name = desiredTable['name']
    columns = generateTableCreateColumns(desiredTable)
    sql = f"CREATE TABLE {schema}.{name} ({columns})"
    if args.verbose:
        print(f"SQL: {sql}")
    if args.dryRun:
        return
    db.execute(connection, sql)
    connection.commit()

def migratorTable(args, connection, desiredTable):
    tables = db.listTables(connection)
    tableName = desiredTable['name']
    if tableName in tables:
        migratorTableAlter(args, connection, tables[tableName], desiredTable)
    else:
        migratorTableCreate(args, connection, desiredTable)

migrators = {
    'table': migratorTable
    }

def main():
    args = argParser().parse_args()
    connection = db.connect(vars(args))
    print(f"OriginalSchema:{yaml.dump(db.listTables(connection), default_flow_style=False)}")
    schema = loadSchema(args.schema)
    for entry in schema:
        typeName = entry['type']
        migrator = migrators.get(typeName, None)
        if migrator:
            migratorTable(args, connection, entry)
    if args.verbose:
        print(f"TABLES:{db.listTables(connection)}")

if __name__ == "__main__":
    sys.exit(main())
