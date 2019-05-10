import json
from datetime import datetime

import dateutil
import requests

import queries
from entities import Vertex
from gql_notary import GqlNotary


class GqlConnection:
    def __init__(self, gql_url=None, session=None):
        if not gql_url:
            import os
            gql_url = os.getenv(
                'GQL_URL', 'https://vi2wfvboq5aozlqmstb24p5tbq.appsync-api.us-east-1.amazonaws.com/graphql')
        if not session:
            session = requests.session()
        self._gql_url = gql_url
        self._notary = GqlNotary(gql_url)
        self._session = session

    def query(self, query_text, variables):
        headers = self._notary.generate_headers(query_text, variables)
        payload = {'query': query_text, 'variables': variables}
        request = requests.post(self._gql_url, headers=headers, json=payload)
        if request.status_code != 200:
            raise RuntimeError(request.content)
        return request.text


class GqlClient:
    def __init__(self, gql_url=None):
        self._connection = GqlConnection(gql_url)

    def query(self, query_text, variables):
        results = self._connection.query(query_text, variables)
        return json.loads(results)

    def get_vertex_properties(self, query_text, variables):
        results = self._connection.query(query_text, variables)
        results = json.loads(results)
        vertex_data = results['data']['vertex']
        vertex_properties = {}
        for vertex_property in vertex_data['vertex_properties']:
            property_name = vertex_property['property_name']
            property_value = vertex_property['property_value']
            property_value = property_value['property_value']
            if 'date_utc' in property_name:
                property_value = datetime.fromtimestamp(float(property_value))
                property_value = property_value.strftime('%m/%d/%Y %H:%M')
            vertex_properties[property_name] = property_value
        return Vertex(variables['internal_id'],  vertex_data['vertex_type'], vertex_properties)

    def get_connected_vertex(self, variables):
        max_runs = 2500
        results = self._connection.query(queries.GET_VERTEX, variables)
        results = json.loads(results)
        vertex_data = results['data']['vertex']
        edge_connection = vertex_data['connected_edges']
        edge_data = edge_connection['edges']
        page_info = edge_connection['page_info']

        connected_vertexes = self._parse_edge_data(edge_data)
        run_count = 0
        while page_info['more'] and run_count <= max_runs:
            token = page_info['token']
            variables['token'] = token
            results = self._connection.query(queries.GET_EDGE_CONNECTOR, variables)
            results = json.loads(results)
            query_data = results['data']['edges']
            edge_data = query_data['edges']
            page_info = query_data['page_info']
            new_connections = self._parse_edge_data(edge_data)
            for direction, edges in new_connections.items():
                connected_vertexes[direction].extend(edges)
            run_count += 1
        return connected_vertexes

    @classmethod
    def _parse_edge_data(cls, edge_data):
        connected_vertexes = {'inbound': [], 'outbound': []}
        for direction, edges in edge_data.items():
            vertex_name = 'to_vertex'
            if direction == 'inbound':
                vertex_name = 'from_vertex'
            for edge in edges:
                connected_vertex = edge[vertex_name]
                vertex_properties = {}
                for vertex_property in connected_vertex['vertex_properties']:
                    property_name = vertex_property['property_name']
                    property_value = vertex_property['property_value']
                    property_value = property_value['property_value']
                    if 'date' in property_name:
                        try:
                            property_value = datetime.fromtimestamp(float(property_value))
                        except ValueError:
                            property_value = dateutil.parser.parse(property_value)
                        # 2019 - 02 - 19 09: 33:55.187 - 0500
                        property_value = property_value.strftime('%Y - %m - %d %H:%M:%S')
                    vertex_properties[property_name] = property_value
                connected_vertexes[direction].append({
                    'vertex': Vertex(connected_vertex['internal_id'], connected_vertex['vertex_type'],
                                     vertex_properties),
                    'edge': edge['edge_label']
                })
        return connected_vertexes


class GqlPaginator:
    def __init__(self, gql_url=None):
        self._connection = GqlConnection(gql_url)

    def get_vertex_edges(self, internal_id, pagination_token=None):
        variables = {
            'internal_id': internal_id,
            'token': pagination_token
        }
        query_text = '''
            query getVertex($internal_id: ID!){
                vertex(internal_id: $internal_id){
                    vertex_type
                    vertex_properties{
                        property_name
                        property_value{
                            data_type
                            property_value
                        }
                    }
                    connected_edges{
                        
                    }
                }
            }
        '''
        results = self._connection.query(query_text, variables)
        print(results)
