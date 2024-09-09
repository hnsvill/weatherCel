import requests, logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# It's tempting to use a lambda because I like JS' arrow functions but I haven't settled on what I like for python
def _req(reqMethod,reqUrl,reqHeaders={},reqPayload={}):
    return requests.request(reqMethod, reqUrl, headers=reqHeaders, data=reqPayload)


def reqRetriable(reqMethod,reqUrl,reqHeaders={},reqPayload={},retries=2,request=_req):
    logging.debug(f'calling {reqUrl}.. retries remaining: {retries}')
    response = _req(reqMethod,reqUrl,reqHeaders,reqPayload)
    if response.status_code == 200:
        return response
    elif retries >= 0:
        retries-=1
        # It was either recursion or a for loop with an early return and I guess this one won the moment ¯\_(ツ)_/¯
        logging.debug(f'call failed. Calling again. Retries remaining: {retries}')
        reqRetriable(reqMethod,reqUrl,reqHeaders,reqPayload,retries,request)
    else:
        logger.error(f'weatherGovClient: {__name__}: whoops, better sound the alarm. Response: {response.text}')
        # I like to raise an exception and bubble things up to the top level. This would also allow utilization of lambda's obervability