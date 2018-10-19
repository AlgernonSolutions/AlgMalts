class MaltegoObject:
    @property
    def to_maltego(self):
        raise NotImplementedError


class Vertex(MaltegoObject):
    def __init__(self, internal_id, vertex_type, vertex_properties=None):
        if not vertex_properties:
            vertex_properties = []
        self._internal_id = internal_id
        self._vertex_type = vertex_type
        self._vertex_properties = vertex_properties

    @property
    def to_maltego(self):
        return 'algernon.Vertex',
