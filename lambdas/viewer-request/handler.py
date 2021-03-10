import json
import random
import boto3

boto3.setup_default_session(region_name='us-east-1')
parameter_store_client = boto3.client('ssm')


def lambda_handler(event, context):
    request = event['Records'][0]['cf']['request']
    headers = request['headers']

    cookie_version_blue = 'X-Version-Name=Blue'
    cookie_version_green = 'X-Version-Name=Green'
    path_blue = '/Blue'
    path_green = '/Green'

    uri = ''

    if request['uri'].endswith('/'):
        request['uri'] = request['uri'] + 'index.html'

    if 'cookie' not in request['headers']:
        request['headers']['cookie'] = []

    # Reset weights, ignore already set cookie
    reset_weight, reset_cookie = do_weight_reset(headers)
    if not reset_weight:
        for cookie in headers.get('cookie', []):
            if cookie_version_blue in cookie['value']:
                uri = path_blue + request['uri']
                break
            elif cookie_version_green in cookie['value']:
                uri = path_green + request['uri']
                break
    request['headers']['cookie'].append(
        {'key': 'Cookie', 'value': reset_cookie})

    if not uri:
        weight = int(load_parameter('Weight'))
        cookie_value = ''

        if random.random() < float(weight / 100.0):
            uri = path_blue + request['uri']
            cookie_value = cookie_version_blue
        else:
            uri = path_green + request['uri']
            cookie_value = cookie_version_green
        request['headers']['cookie'].append(
            {'key': 'Cookie', 'value': cookie_value})

    request['uri'] = uri
    return request


def do_weight_reset(headers):
    reset = load_parameter('ResetWeights')
    if not reset:
        return False, None

    cookie_reset = f'X-Version-Reset={reset}'
    for cookie in headers.get('cookie', []):
        if cookie_reset in cookie['value']:
            return False, cookie_reset

    return True, cookie_reset


def load_parameter(param_name):
    response = parameter_store_client.get_parameters_by_path(
        Path='/CloudFront/Lambda/',
        Recursive=True,
        WithDecryption=False,
        MaxResults=10
    )

    for param in response['Parameters']:
        if param['Name'].endswith(param_name):
            return param['Value']
