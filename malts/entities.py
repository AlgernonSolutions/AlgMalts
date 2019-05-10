_vertex_mapping = {
    'IdSource': 'algernon.DataSource',
    'ExternalId': 'algernon.ExternalId',
    'ChangeLog': 'algernon.ChangeLog'
}

_display_name_mapping = {
    'change_date_utc': 'Change Date UTC',
    'change_date': 'Change Date'
}

_internal_name_mapping = {
    'id_type': 'properties.idType',
    'id_name': 'properties.idName',
    'id_source': 'properties.idSource',
    'id_value': 'properties.idValue',
    'change_date_utc': 'properties.changeDateUTC',
    'action_id': 'properties.actionId',
    'by_emp_id': 'properties.byEmpId',
    'fungal_stem': 'properties.fungalStem',
    'action': 'properties.action'
}


class MaltegoObject:
    def bind_to_transformation(self, transformation):
        raise NotImplementedError


class Vertex(MaltegoObject):
    def __init__(self, internal_id, vertex_type, vertex_properties=None):
        if not vertex_properties:
            vertex_properties = {}
        self._internal_id = internal_id
        self._vertex_type = vertex_type
        self._vertex_properties = vertex_properties

    def bind_to_transformation(self, transformation, inbound=False, edge_label=None):
        maltego_vertex_name = 'algernon.AlgObject'
        maltego_vertex_name = _vertex_mapping.get(self._vertex_type, maltego_vertex_name)
        if self._internal_id in transformation:
            return transformation
        entity = transformation.addEntity(maltego_vertex_name, self._internal_id)
        # entity.addAdditionalFields(field_name='vertex_type', value=self._vertex_type)
        for property_name, vertex_property in self._vertex_properties.items():
            display_name = _display_name_mapping.get(property_name, property_name)
            property_name = _internal_name_mapping.get(property_name, property_name)
            entity.addAdditionalFields(field_name=property_name, display_name=display_name, value=vertex_property)
        if not inbound:
            entity.addAdditionalFields(field_name='link#maltego.link.direction', value='output-to-input')
        if edge_label:
            entity.addAdditionalFields(field_name='link#maltego.link.label', value=edge_label)
        return transformation
