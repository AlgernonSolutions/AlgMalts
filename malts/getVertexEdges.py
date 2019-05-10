import sys

from MaltegoTransform import MaltegoTransform
from gql_client import GqlClient


maltego_transform = MaltegoTransform()
maltego_transform.parseArguments(sys.argv)
maltego_transform.addUIMessage('passed arguments are: %s' % str(sys.argv))
vertex_internal_id = maltego_transform.getVar('algObject.internalId')
maltego_transform.addUIMessage('queried internal_id is %s' % vertex_internal_id)
if not vertex_internal_id:
    vertex_internal_id = "bfc522d3f5e7e52a76f44850ae6b1c2b"

variables = {
    'internal_id': vertex_internal_id
}
gql_client = GqlClient()
vertexes = gql_client.get_connected_vertex(variables)
internal_ids = set()
for direction, connected_vertexes in vertexes.items():
    for connected_vertex in connected_vertexes:
        inbound = direction == 'inbound'
        vertex = connected_vertex['vertex']
        internal_ids.add(vertex._internal_id)
        edge_label = connected_vertex['edge']
        vertex.bind_to_transformation(maltego_transform, inbound, edge_label)
maltego_transform.returnOutput()
