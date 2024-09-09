import psycopg, dotenv, os

import psycopg.rows

dotenv.load_dotenv('.env')


# Extra hacked. I'd like to rewrite this for idempotency and single responsibility/abstracting the connection & cursor.
# Then I'd like to make it async. Then I'll deploy it as a library. I've been meaning to test using GitHub as a spot to host my packages.

def createDatabaseIfNotExists(dbName, dbPassword, dbPort, dbHost):
    with psycopg.connect(f'user=postgres password={dbPassword} port={dbPort} host={dbHost}') as conn:
    # with psycopg.connect('user=postgres password=mysecretpassword port=5432 host=localhost') as conn:
        with conn.cursor() as cur:
            conn.autocommit = True
            sql_query = f"CREATE DATABASE {dbName}"
            try:
                cur.execute(sql_query)
            except Exception as e:
                # Not necessary for this particular implementation but eventually I want to ad my own errors
                # import re
                # doesAlreadyExist = re.match('database "([a-zA-Z]*)" already exists', e)
                # print(e, doesAlreadyExist)
                print(e)
                cur.close()
                # conn.close()
            else: # hmm, this is untested but was in the docs
                # Revert autocommit settings
                print(cur)
                conn.autocommit = False
                # conn.close()

def createTableIfNotExists(dbName, dbPassword, dbPort, dbHost, tableName, schemaString):
    with psycopg.connect(f'dbname={dbName} user=postgres password={dbPassword} port={dbPort} host={dbHost}') as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT tablename
                FROM pg_catalog.pg_tables
                WHERE tablename = '{tableName}'
                """)
            tables = cur.fetchall()
            print(tables)
            if len(tables)<1:
                print(f'we made it: {tables}')
                print(f'creating table {tableName}')
                cur.execute(f"""
                    CREATE TABLE {tableName}
                    {schemaString}
                    """)
                conn.commit()
            else:
                print(f'tables: {tables}')
                print(f'table {tableName} already exists')


def insertRows(dbName, dbPassword, dbPort, dbHost, tableName, columnNames, rows):
    with psycopg.connect(f'dbname={dbName} user=postgres password={dbPassword} port={dbPort} host={dbHost}') as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    f"""
                    INSERT INTO {tableName} {columnNames}
                    VALUES {rows}
                    """
                )
                conn.commit()
            except Exception as e:
                print(e)
                print(f'something went wrong when wrting to {dbName}.{tableName}.')

def selectRecords(dbName, dbPassword, dbPort, dbHost, tableName, columnNames, whereClause=''):
    with psycopg.connect(f'dbname={dbName} user=postgres password={dbPassword} port={dbPort} host={dbHost}') as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            try:
                q = f"""
                    SELECT {columnNames}
                    FROM {tableName}
                    {whereClause}
                    """
                print(q)
                cur.execute(
                    q
                )
                return cur.fetchall()
            except Exception as e:
                print(e)
                print(f'something went wrong when reading from {dbName}.{tableName}.')


if __name__=='__main__':
    dbTableName = 'hereigoagaon'
    databaseName = os.environ['POSTGRES_DATABASE_NAME']
    databasePassword = os.environ['POSTGRES_PASSWORD']
    databasePort = os.environ['POSTGRES_PORT']
    databaseHost = os.environ['POSTGRES_HOST']
    createDatabaseIfNotExists(
        dbName=databaseName,
        dbPassword=databasePassword,
        dbPort=databasePort,
        dbHost=databaseHost
    )
    # createTableIfNotExists(
    #     dbName=databaseName,
    #     dbPassword=databasePassword,
    #     dbPort=databasePort,
    #     dbHost=databaseHost,
    #     tableName=dbTableName,
    #     schemaString='(temerature SMALLINT, tempUnit VARCHAR(2))'
    # )
    # insertRows(
    #     dbName=databaseName,
    #     dbPassword=databasePassword,
    #     dbPort=databasePort,
    #     dbHost=databaseHost,
    #     tableName=dbTableName,
    #     columnNames='(temerature, tempUnit)',
    #     rows="(10, 'F')"
    # )
    records = selectRecords(
        dbName=databaseName,
        dbPassword=databasePassword,
        dbPort=databasePort,
        dbHost=databaseHost,
        tableName=dbTableName,
        columnNames='*',
        whereClause='WHERE temperature>65'
    )
    for r in records:
        print(r)


