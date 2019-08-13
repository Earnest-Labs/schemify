import logging
import psycopg2
import os

def config():
    return {
        "database": os.environ.get('POSTGRES_DB','postgres'),
        "user": os.environ.get('POSTGRES_USER','schemify'),
        "password": os.environ.get('POSTGRES_PASSWORD','schemify'),
        "host": os.environ.get('POSTGRES_HOST','pgsql-dev')
        }

def cleanConfig(config):
    return {
        "database" : config['database'],
        "user" : config['user'],
        "password" : config['password'],
        "host" : config['host'],
        "port" : config['port']
        }

def connect(config=config()):
    return psycopg2.connect(**cleanConfig(config))

def listTableColumns(connection, table, schema='public'):
    cursor = execute(connection, f"SELECT column_name, column_default, data_type, character_maximum_length, character_octet_length FROM information_schema.columns WHERE table_schema='{schema}' AND table_name='{table}'")
    result = dict();
    for column in cursor.fetchall():
        result[column[0]] = {
            'name' : column[0],
            'default' : column[1],
            'type' : column[2],
            'length' : column[3],
            'octet_length' : column[4]
            }
    return result

def listConstraintColumns(connection, table, constraintName, schema='public'):
    cursor = execute(connection,f"SELECT column_name, ordinal_position FROM information_schema.key_column_usage WHERE table_schema='{schema}' AND table_name='{table}' AND constraint_name='{constraintName}'")
    result = dict();
    for column in cursor.fetchall():
        result[column[0]] = column[1]
    return result;

def listTableConstraints(connection, table, schema='public'):
    cursor = execute(connection, f"SELECT constraint_name, constraint_type FROM information_schema.table_constraints WHERE table_schema='{schema}' AND table_name='{table}'")
    result = dict();
    for column in cursor.fetchall():
        result[column[0]] = {
            'constraint_type' : column[1],
            'columns': listConstraintColumns(connection, table, column[0], schema)
            }
    return result

def listTables(connection, schema='public'):
    cursor = execute(connection, f"SELECT table_name FROM information_schema.tables WHERE table_schema='{schema}' AND table_type='BASE TABLE'")
    result = dict();
    for item in cursor.fetchall():
        logging.debug(f"listTables: {item[0]}")
        result[item[0]] = {
            'type': 'table',
            'name': item[0],
            'columns' : listTableColumns(connection, item[0]),
            'constraints' : listTableConstraints(connection, item[0])
            }
    return result

def createTable(connection, tableName, schema='public'):
    execute(connection, f"CREATE TABLE {schema}.{tableName} ()")

def execute(connection, sql):
    cursor = connection.cursor()
    cursor.execute(sql)
    return cursor
