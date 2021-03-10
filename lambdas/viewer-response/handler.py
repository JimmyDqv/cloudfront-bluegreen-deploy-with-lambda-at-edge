import json
import random


def lambda_handler(event, context):
    response = event['Records'][0]['cf']['response']
    request = event['Records'][0]['cf']['request']
    # Persist cookie, set the set-cookie header
    if 'set-cookie' not in response['headers']:
        response['headers']['set-cookie'] = []

    request_headers = request['headers']
    cookie_version_blue = 'X-Version-Name=Blue'
    cookie_version_green = 'X-Version-Name=Green'
    cookie_reset = 'X-Version-Reset'

    for cookie in request_headers.get('cookie', []):
        if cookie_version_blue in cookie['value']:
            response['headers']['set-cookie'].append(
                {'key': 'set-cookie', 'value': cookie_version_blue})
        elif cookie_version_green in cookie['value']:
            response['headers']['set-cookie'].append(
                {'key': 'set-cookie', 'value': cookie_version_green})
        elif cookie_reset in cookie['value']:
            response['headers']['set-cookie'].append(
                {'key': 'set-cookie', 'value': cookie['value']})

    return response
