import json, logging, dotenv, weatherGovClient, os, postgresClient

dotenv.load_dotenv('.env')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

weatherPostgresTypeMapping = {
    'forecastStartTimeTimestamp': 'BIGINT',
    'forecastEndTimeTimestamp': 'BIGINT',
    'forecastStartTimeHour': 'SMALLINT',
    'temperature': 'SMALLINT',
    'temperatureUnit': 'VARCHAR(2)',
    'forecastRetrievedTimestamp': 'BIGINT',
    'hoursFromForecastApproximate': 'SMALLINT',
    'wfoXY': 'VARCHAR(20)',
    'lat': 'VARCHAR(20)',
    'lon': 'VARCHAR(20)'
}

def handler(event, context):
    dbTableName = 'hereigoagaonagainn'

    databaseName = os.environ['POSTGRES_DATABASE_NAME']
    databasePassword = os.environ['POSTGRES_PASSWORD']
    databasePort = os.environ['POSTGRES_PORT']
    databaseHost = os.environ['POSTGRES_HOST']

    try:
        monitoredCoordinatePair = json.loads(os.environ['COORDINATE_PAIRS_MONITORED'])[0]
        forecastPointsPostgres = weatherGovClient.forecast(**monitoredCoordinatePair)
        insertKeys = f'({', '.join(forecastPointsPostgres[0].keys())})'
        rowsAsListOfTupleString = ','.join([f'{tuple(r.values())}' for r in forecastPointsPostgres])
        weatherPostgresTypeMappingSchemaString = f'({', '.join([f'{k} {v}' for k,v in weatherPostgresTypeMapping.items()])})'
    except Exception as e:
        logger.error(f'issue fetching forecast')
    try:
        postgresClient.createDatabaseIfNotExists(
                dbName=databaseName,
                dbPassword=databasePassword,
                dbPort=databasePort,
                dbHost=databaseHost
            )
        postgresClient.createTableIfNotExists(
                dbName=databaseName,
                dbPassword=databasePassword,
                dbPort=databasePort,
                dbHost=databaseHost,
                tableName=dbTableName,
                schemaString=weatherPostgresTypeMappingSchemaString
            )
        postgresClient.insertRows(
                dbName=databaseName,
                dbPassword=databasePassword,
                dbPort=databasePort,
                dbHost=databaseHost,
                tableName=dbTableName,
                columnNames=insertKeys,
                rows=rowsAsListOfTupleString
            )
    except Exception as e:
        logger.error(f'issue persisting forecast')
    

if __name__=='__main__':
    print('hi there')
    handler({},{})