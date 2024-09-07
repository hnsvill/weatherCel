import dotenv, os, logging, client, json, datetime

dotenv.load_dotenv('.env')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

_defaultHeaders = {
        'User-Agent': os.environ['WEATHER_GOV_USER_AGENT']
    }

def _forecastHourlyUrlFromCoordinates(lat,lon):
    url = f'https://api.weather.gov/points/{lat},{lon}'
    response = client.reqRetriable('GET',url, _defaultHeaders)
    return response.json()['properties']['forecastHourly']

def _forecastPeriodsFromUrl(url):
    response = client.reqRetriable('GET',f'{url}?units=us', _defaultHeaders)
    return response.json()['properties']['periods']

def _forecastPeriodsFiltered(forecastPeriods,hoursFromNow=72):
    timestampFromIsoFormat = lambda isoString: datetime.datetime.fromisoformat(isoString).timestamp()
    nowTimestamp = datetime.datetime.now().timestamp()
    endTimestamp = nowTimestamp + (3600 * hoursFromNow)
    return [{
        'forecastStartTimeTimestamp': float(timestampFromIsoFormat(f['startTime'])),
        'forecastEndTimeTimestamp': timestampFromIsoFormat(f['endTime']),
        'temperature': f['temperature'],
        'temperatureUnit': f['temperatureUnit'],
        'forecastRetrievedTimestamp':round(nowTimestamp,0),
        'hoursFromForecastApproximate':int((timestampFromIsoFormat(f['startTime'])-round(nowTimestamp,0))/3600)
    } for f in forecastPeriods if nowTimestamp < timestampFromIsoFormat(f['startTime']) < endTimestamp]

def forecast(lat,lon):
    forecastHourlyUrl = _forecastHourlyUrlFromCoordinates(lat,lon)
    wfoXY = forecastHourlyUrl.split('gridpoints/')[1].split('/forecast')[0]
    forecastPeriods = _forecastPeriodsFromUrl(forecastHourlyUrl)
    hoursFromNow = int(os.environ['FORECAST_HOURS_FROM_NOW'])
    filtered = _forecastPeriodsFiltered(forecastPeriods,hoursFromNow)
    return([{'wfoXY':wfoXY,'lat':lat,'lon':lon,**f} for f in filtered])

if __name__=='__main__':
    # dataloaded = json.load(open('weatherGovResponse.json', 'r'))['properties']['periods']
    dataloaded = forecast(39.7456,-97.0892)
    print(json.dumps(
        dataloaded,
        indent=2
    ))