# AT HOME CODING CHALLENGE

Please spend no more than 4 hours on this exercise. If you have any questions, please reach out to the recruiter at CEL for assistance.

## INSTRUCTIONS

Implement a Dockerized application in Python that tracks the variation in weather temperature forecasts over time for a given location using the weather.gov API and a local data store.

## REQUIREMENTS
1. As an input, the application must accept a configurable location for which to track weather forecasts, specified as a latitude and longitude, for example:
```json
{
    "location": {
        "lat": "39.7456",
        "lon": "-97.0892"
    }
}
```
2. At a configurable interval, defaulting to 60 minutes, the application must query the API described at https://www.weather.gov/documentation/services-web-api to retrieve forecast data for the specified latitude and longitude
3. The application must store the set of hourly temperature forecasts for the next 72 hours, as predicted at the time of retrieval, in a local datastore.
4. The application must expose an API or endpoint that accepts as inputs: a latitude, longitude, date, and UTC hour of day (0-23)
5. The API or endpoint must return the highest and lowest recorded forecast in the database for the specified location, day and hour of day
6. The application must contain an appropriate Dockerfile and other resources to containerize the application
7. The application must include a README with instructions for building the Docker container and running the application
8. Clearly state all of the assumptions you made in completing the application

---
</br>

# Solution

<details>
  <summary>If you'd like a "pencils down at 2-4h" please visit <a target="_blank" href="https://github.com/hnsvill/weatherCel/commit/886af8399c58d85fe3954e026e19329fd52caec1">this commit.</a></summary>
  Time is approximate because I chipped away at it here and there. I kept going because
  <ol>
    <li>I want to impress you and</li>
    <li>my outside-of-employed-at-company "cookbook" is thin ^[nonexistent ¯\_(ツ)_/¯] anyway. That first commit doesn't meet all the requirements but I'm <s>assuming</s> ^[hopeful] you were looking to see where I go when there's not enough time to do everything.</li>
  </ol>
</details>

## Requirements: 
1. Configurable location for which to track weather forecasts. I like lists for this kind of thing because it's traversable. Plus the JSON object can hold human-readable fields the app can discard.
```json
[
    {
        "lat": "39.7456",
        "lon": "-97.0892"
    }
]
```
2. At a configurable interval, defaulting to 60 minutes, the application must query the API described at https://www.weather.gov/documentation/services-web-api to retrieve forecast data for the specified latitude and longitude
3. The forecasts for the next 72 hours are persisted in a postgres database from the postgres docker image.
4. The application must expose an API or endpoint that accepts as inputs: a latitude, longitude, date, and UTC hour of day (0-23)
5. The API or endpoint must return the highest and lowest recorded forecast in the database for the specified location, day and hour of day
6. The application must contain an appropriate Dockerfile and other resources to containerize the application
7. The application must include a README with instructions for building the Docker container and running the application
8. Clearly state all of the assumptions you made in completing the application


</br>

| Field Name                   | Type        | Description                                       | Sample     |
|------------------------------|-------------|---------------------------------------------------|------------|
| forecastStartTimeTimestamp   | BIGINT      | Timestamp of the forecast period start            | 1725706800 |
| forecastEndTimeTimestamp     | BIGINT      | Timestamp of the forecast period end              | 1725710400 |
| forecastStartTimeHour        | SMALLINT    | Forecast start hour of the day (0-23)             | 20         |
| temperature                  | SMALLINT    | Temperature as a value                            | 53         |
| temperatureUnit              | VARCHAR(2)  | Temerature units, either F for us or C for si     | F          |
| forecastRetrievedTimestamp   | BIGINT      | Timestamp of when the forecast was captured       | 1725706392 |
| hoursFromForecastApproximate | SMALLINT    | Hours between forecast retrieval and period start | 6          |
| wfoXY                        | VARCHAR(20) | Forecast office ID, forecast grid x,y: wfo/x,y    | TOP/32,81  |
| lat                          | VARCHAR(20) | Latitude used to query api.weather.gov            | 39.7456    |
| lon                          | VARCHAR(20) | Latitude used to query api.weather.gov            | -97.0892   |


*Postgres' POINT was a headache to pass through `psycopg`

## Development

### Instructions to run locally:

Build and run the docker container:
```bash
docker build -t persistforecast . && docker run --platform linux/amd64 -p 9000:8080 persistforecast:latest
```

chmod the bash script that invokes the lambda
```bash
chmod +x invokePersistForecast.sh
```
copy this line
```bash
0 * * * * [qualified_path_to_script]/invokePersistForecast.sh
```
Paste in to your [mac's cron jobs](https://phoenixnap.com/kb/cron-job-mac)
```bash
crontab -e
```
Run the container
```bash
docker run --platform linux/amd64 -p 9000:8080 persistforcast:latest
```

The cron job runs the `invokePersistForecast` script which invokes the lambda every hour with a cURL request. See ["(Optional) Test the image locally"]((https://docs.aws.amazon.com/lambda/latest/dg/python-image.html#python-image-instructions))

---

### Instructions to deploy to AWS

This assumes you already have jq, the aws cli, and terraform installed

Create the ECR
```bash
cd terraform/prerequisiteInfrastructure/
terraform init
terraform apply
cd ../..
```

Log into ECR
```bash
aws ecr get-login-password --region $(aws configure get region) | docker login --username AWS --password-stdin $(aws sts get-caller-identity | jq -r '.Account').dkr.ecr.$(aws configure get region).amazonaws.com
```

Tag and push the docker image.
```bash
docker build -t $(aws sts get-caller-identity | jq -r '.Account').dkr.ecr.us-west-1.amazonaws.com/persistforecast . && docker push $(aws sts get-caller-identity | jq -r '.Account').dkr.ecr.us-west-1.amazonaws.com/persistforecast:latest
```

Create the lambda
```bash
cd terraform/app/
terraform init
terraform apply
cd ../..
```

You can see the lambda and invoke it manually
```bash
aws lambda list-functions | jq ".Functions" | jq ".[] | select(.FunctionName==\"persistForecast\")"
aws lambda invoke --function-name persistForecast --cli-binary-format raw-in-base64-out --payload '{ "key":"value" }' responses.json
```

https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function




Just in case something seems fishy: https://alexwlchan.net/2023/fish-venv/

I do currently use camelCase because of recent js development. I can change. I do like camelCase because of the reduced length and ease of typing though.


### Waterfalls I ~~did not~~ ^[sort of tried not to] chase (potential next steps)


- ~~Preprocessing. I'd want to convert C into F when saving the forecasts~~
- Types. Implement something like AJV for python for nicer data validation.
- ~~Retries. Something on the weather site said something about the API call sometimes not returning a 200 or returning null values but retrying fixes it. Only sorta crossed off.~~
- Housekeeping
  - Precommit hook for running tests & linting
  - ~~Linting with settings - PEP8's line length is too short and enforcing it at that length makes it _less_ readable 🫣~~
  - Pipeline for testing/building on new branches, +deploy on certain branches
- Telemetry - OpenTelemetry + Prometheus looked good but tbh and app this size and a bit bigger imo could be covered with Lambda's included telemetry depending on priorities.
- Tests are NOT a waterfall item but I made choices based on the time constraints. This was a lot like eating ice cream for dinner.
- More sophisticated logging that can be passed down the stack instead of repeating myself.
- Separate the endpoint and persisting the forecast into two images. It saved some time to use one container instead of composing.
- Error handling. I like to wrap the main function for every module in a try catch or equivalent for the language. If something goes wrong, throw an error to stop computing on a request that would fail anyway and reduce the need for other error handling in more places. Then I can throw custom errors that I can handle however I want at the next level(s)
