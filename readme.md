# AT HOME CODING CHALLENGE

Please spend no more than 4 hours on this exercise. If you have any questions, please reach out to the recruiter at CEL for assistance.

## INSTRUCTIONS

Implement a Dockerized application in Python that tracks the variation in weather temperature forecasts over time for a given location using the weather.gov API and a local data store.

## REQUIREMENTS
1. As an input, the application must accept a configurable location for which to track weather
forecasts, specified as a latitude and longitude, for example:
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

forecastRetrievedTimestamp
latitude
longitude
forecastTimestamp
temperature
temperatureUnit
wfoXY | Forecast office ID / forecast grid x coordinate, forecast grid y coordinate

PQR/120,105


## Dev

### Instructions to run locally:

Build and run the docker container:
```bash
docker build -t persistforecast . && docker run --platform linux/amd64 -p 9000:8080 persistforecast:latest
```

chmod the bash script that invokes the lambda
```
chmod +x invokePersistForecast.sh
```
copy this line
```
chmod +x invokePersistForecast.sh
```

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

Yup, I do currently use camelCase because of recent js development. I can change. I do like camelCase because of the reduced length and ease of typing though.


### Waterfalls I ~~did not~~ ^[sort of tried not to] chase (potential next steps)


- Preprocessing. I'd want to convert C into F when saving the forecasts 
- Types. Implement something like AJV for python for nicer data validation.
- ~~Retries. Something on the weather site said something about the API call sometimes not returning a 200 or returning null values but retrying fixes it.~~
- Housekeeping
  - Precommit hook for running tests & linting
  - ~~Linting with settings - PEP8's line length is too short and enforcing it at that length makes it _less_ readable 🫣~~
  - Pipeline for testing/building on new branches, +deploy on certain branches
- Telemetry - OpenTelemetry + Prometheus looked good but tbh and app this size and a bit bigger imo could be covered with Lambda's included telemetry depending on priorities.
- Tests are NOT a waterfall item but I made choices based on the time constraints. This was ice cream for dinner.
- More sophisticated logging that can be passed down the stack instead of repeating myself.
- Separate the endpoint and persisting the forecast into two images. It saved some time to use one container instead of composing.
- Error handling. I like to wrap the main function for every module in a try catch or equivalent for the language. If something goes wrong, throw an error to stop computing on a request that would fail anyway and reduce the need for other error handling in more places. Then I can throw custom errors that I can handle however I want at the next level(s)
