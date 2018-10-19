
import sys

from MaltegoTransform import MaltegoTransform
from gql_client import GqlClient

query = '''
    query expandVertex($internal_id: ID!){
        vertex(internal_id: $internal_id){
            connected_edges{
                edges{
                    inbound{
                        edge_label
                        from_vertex
                    }
                    outbound{
                        edge_label
                        to_vertex
                    }
                }
            }
        }
    }
'''

maltego_transform = MaltegoTransform()
maltego_transform.parseArguments(sys.argv)
vertex_internal_id = maltego_transform.getVar('internal_id')

variables = {
    'internal_id': vertex_internal_id
}

gql_client = GqlClient()
results = gql_client.query(query, variables)
print(results)
maltego_transform.addUIMessage("completed!")
maltego_transform.returnOutput()
