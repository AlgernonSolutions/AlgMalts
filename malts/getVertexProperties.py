import sys

from MaltegoTransform import MaltegoTransform
from gql_client import GqlClient

query = '''
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
        }
    }
'''

maltego_transform = MaltegoTransform()
maltego_transform.parseArguments(sys.argv)
vertex_internal_id = maltego_transform.getVar('internal_id')
if not vertex_internal_id:
    vertex_internal_id = "b7216ade973350b3b37780538792216f"

variables = {
    'internal_id': vertex_internal_id
}
gql_client = GqlClient()
updated_vertex = gql_client.get_vertex_properties(query, variables)
updated_vertex.bind_to_transformation(maltego_transform)
maltego_transform.returnOutput()
