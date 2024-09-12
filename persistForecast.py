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

def handler(event = {}, context = {}):
    dbTableName = os.environ['POSTGRES_TABLE_NAME']
    databaseName = os.environ['POSTGRES_DB']
    databasePassword = os.environ['POSTGRES_PASSWORD']
    databasePort = os.environ['POSTGRES_PORT']
    databaseHost = os.environ['POSTGRES_HOST']

    try:
        # Should handle more pairs coming in through the event.
        monitoredCoordinatePair = json.loads(os.environ['COORDINATE_PAIRS_MONITORED'])[0]
        forecastPointsPostgres = weatherGovClient.forecast(**monitoredCoordinatePair)
        insertKeys = f'({', '.join(forecastPointsPostgres[0].keys())})'
        rowsAsListOfTupleString = ','.join([f'{tuple(r.values())}' for r in forecastPointsPostgres])
        weatherPostgresTypeMappingSchemaString = f'({', '.join([f'{k} {v}' for k,v in weatherPostgresTypeMapping.items()])})'
    except Exception as e:
        logger.error(f'issue fetching forecast from weather.gov')
        return {'message':f'issue fetching forecast from weather.gov: {e}'}
    print('success calling weather.gov api')
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
        return {'message':f'Successfully persisted forecast periods for {monitoredCoordinatePair}'}
    except Exception as e:
        logger.error(f'issue persisting forecast')
        return {'message':f'Error persisting forecast: {e}'}
    

if __name__=='__main__':
    handler()
