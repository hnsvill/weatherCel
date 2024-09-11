import json, logging, dotenv, os, postgresClient, jsonschema, datetime

dotenv.load_dotenv('.env')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def handler(event, context={}):
    from jsonschema import validate
    requestSchema = json.load(open('model/requestBodySchema.json','r'))
    latlonSchema = json.load(open('model/latlonSchema.json','r'))
    try:
        validate(instance=event['body'], schema=requestSchema)
        [
            validate(instance={
                   'lat': float(r['lat']),
                   'lon': float(r['lon'])
                },schema=latlonSchema)
            for r in event['body']
        ]
    except jsonschema.exceptions.ValidationError as e:
        return {'message':f'Request body validation error: {e}'}
    except Exception as e:
        return {'message':e}

    dbTableName = os.environ['POSTGRES_TABLE_NAME']
    databaseName = os.environ['POSTGRES_DATABASE_NAME']
    databasePassword = os.environ['POSTGRES_PASSWORD']
    databasePort = os.environ['POSTGRES_PORT']
    databaseHost = os.environ['POSTGRES_HOST']

    try:
        for requestI in event['body']:
            requestedDay = datetime.datetime.strptime(requestI['date'],'%Y-%m-%d')
            requestedDayAsTimestamp = requestedDay.timestamp()
            oneDay = datetime.timedelta(days=1).total_seconds()
            
            qwhere = f"""
                WHERE forecaststarttimehour = {requestI['hour']}
                AND lat = \'{requestI['lat']}\'
                AND lon = \'{requestI['lon']}\'
                AND forecastStartTimeTimestamp BETWEEN {requestedDayAsTimestamp - 86400} AND {requestedDayAsTimestamp}
                """
            results = postgresClient.selectRecords(
                dbName=databaseName,
                dbPassword=databasePassword,
                dbPort=databasePort,
                dbHost=databaseHost,
                tableName=dbTableName,
                columnNames='*',
                whereClause= qwhere
            )
            sortedResults = sorted(results, key=lambda p:p['temperature'])
            if len(sortedResults)>0:
                return {
                    "lat": requestI['lat'],
                    "lon": requestI['lon'],
                    "date": requestI['date'],
                    "hour": requestI['hour'],
                    "high": sortedResults[-1]['temperature'],
                    "low": sortedResults[0]['temperature'],
                    "highForecastretrievedtimestamp":sortedResults[-1]['forecastretrievedtimestamp'],
                    "lowPredictionTimestamp":sortedResults[0]['forecastretrievedtimestamp']
                }
            else:
                return {
                    "lat": requestI['lat'],
                    "lon": requestI['lon'],
                    "date": requestI['date'],
                    "hour":requestI['hour'],
                }
    except Exception as e:
        return {'message':f'Error while querying forecast: {e}'}

if __name__=='__main__':
    body = [
        {
            "lat": "39.7456",
            "lon": "-97.0892",
            "date":"2024-09-10",
            "hour":23,
            "ignore":"me"
        }
    ]
    print(json.dumps(
                handler({'body':body}),
                indent=2
            ))
