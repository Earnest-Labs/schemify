import argparse
import glob
import itertools
import logging
import os
import db # schemify.db as db
import sys
import yaml

schemifyTypeToPostgresType = {
    'blob': 'bytea'
}

constraintSql = {
    'primary_key' : 'PRIMARY KEY',
    'unique' : 'UNIQUE'
    }

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
    logging.debug(f"SchemaDirectory: {schemaDir} [Note:You can select a different schema directory with '-s']")
    schemaFiles = glob.glob(os.path.join(schemaDir,"*.schema.yml"))
    logging.debug(f"schemaFiles: {schemaFiles}")
    schemaLoL = [loadYaml(filename) for filename in schemaFiles]
    schema = list(itertools.chain(*schemaLoL))
    return schema

def migratorTableAddMissingColumns(args, connection, existingTable, desiredTable):
    schema  = desiredTable.get('schema','public')
    name = desiredTable['name']
    missingColumns = list(filter(lambda col: col['name'] not in existingTable['columns'], desiredTable['columns']))
    if len(missingColumns):
        sql = f"ALTER TABLE {schema}.{name} " + ",".join(["ADD COLUMN " + generateTableCreateColumn(column)
                                                          for column in missingColumns])
        logging.info(f"SQL: {sql}")
        if args.dryRun:
            return
        db.execute(connection, sql)
        connection.commit()

def constraintSuffix(constraintType):
    return {
        'primary_key' : 'pkey'
        }.get(constraintType,constraintType)

def tableConstraintDefaultName(tableName, constraintType):
    return f"{tableName}_{constraintSuffix(constraintType)}"

def migratorTableAddMissingConstraint(args, connection, existingTable, desiredTable, constraint):
    schema  = desiredTable.get('schema','public')
    name = desiredTable['name']
    constraintType = constraint['type']
    constraintName = constraint.get('name', tableConstraintDefaultName(name,constraintType))
    if constraintName in existingTable['constraints']:
        logging.debug(f"Constraint {constraintName} exists. Need to verify column membership")
    else:
        logging.debug(f"Constraint {constraintName} does not exist. Need to create")
        sql = f"ALTER TABLE {schema}.{name} ADD CONSTRAINT {constraintName} " +\
            constraintSql.get(constraintType,constraintType) + " (" +\
            ",".join(constraint['columns']) + ")"
        logging.info(f"SQL: {sql}")
        if args.dryRun:
            return
        db.execute(connection, sql)
        connection.commit()


def migratorTableAddMissingConstraints(args, connection, existingTable, desiredTable):
    logging.debug(f"desiredConstraints:{desiredTable.get('constraints',None)}")
    for constraint in desiredTable.get('constraints',[]):
        migratorTableAddMissingConstraint(args, connection, existingTable, desiredTable, constraint)
        pass

def migratorTableAlter(args, connection, existingTable, desiredTable):
    migratorTableAddMissingColumns(args, connection, existingTable, desiredTable)
    migratorTableAddMissingConstraints(args, connection, existingTable, desiredTable)

def columnLength(column):
    if 'length' in column:
        return f"({column['length']})"
    return ""

def generateTableCreateColumn(column):
    name = column['name']
    schemifyTypeName = column['type']
    typeName = schemifyTypeToPostgresType.get(schemifyTypeName, schemifyTypeName)
    length = columnLength(column)
    return f"{name} {typeName}{length}"

def generateTableCreateColumns(desiredTable):
    return [generateTableCreateColumn(column) for column in desiredTable['columns']]


def generateTableCreateConstraint(desiredTable, constraint):
    constraintTypeRaw = constraint['type']
    constraintType = constraintSql.get(constraint['type'], constraintTypeRaw)
    return constraintType + ' (' + ','.join(constraint.get('columns',[])) + ')'

def generateTableCreateConstraints(desiredTable):
    return [ generateTableCreateConstraint(desiredTable, constraint)
             for constraint in desiredTable.get('constraints',[]) ]

def migratorTableCreate(args, connection, desiredTable):
    schema  = desiredTable.get('schema','public')
    name = desiredTable['name']
    columns = generateTableCreateColumns(desiredTable)
    logging.debug(f"columns: {columns}")

    constraints = generateTableCreateConstraints(desiredTable)
    logging.debug(f"constraints: {constraints}")

    columnsAndConstraints = ", ".join(itertools.chain.from_iterable([columns,constraints]))
    sql = f"CREATE TABLE {schema}.{name} ({columnsAndConstraints})"
    logging.info(f"SQL: {sql}")
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
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

    connection = db.connect(vars(args))
    logging.debug(f"OriginalSchema:\n{yaml.dump(db.listTables(connection), default_flow_style=False)}")
    schema = loadSchema(args.schema)
    for entry in schema:
        typeName = entry['type']
        migrator = migrators.get(typeName, None)
        if migrator:
            migrator(args, connection, entry)
    logging.debug(f"TABLES:{db.listTables(connection)}")

if __name__ == "__main__":
    sys.exit(main())
