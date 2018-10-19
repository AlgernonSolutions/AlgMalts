import json

import requests

from gql.gql_notary import GqlNotary


class GqlClient:
    def __init__(self, gql_url=None):
        if not gql_url:
            import os
            gql_url = os.getenv(
                'GQL_URL', 'https://vi2wfvboq5aozlqmstb24p5tbq.appsync-api.us-east-1.amazonaws.com/graphql')
        self._gql_url = gql_url
        self._notary = GqlNotary(gql_url)

    def query(self, query_text, variables):
        headers = self._notary.generate_headers(query_text, variables)
        payload = {'query': query_text, 'variables': variables}
        print('gql fire payload: %s' % payload)
        request = requests.post(self._gql_url, headers=headers, json=payload)
        if request.status_code != 200:
            raise RuntimeError(request.content)
        return json.loads(request.text)
