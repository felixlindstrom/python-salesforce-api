import xmltodict
from ..models import retrieve


def package_xml_to_type_list(xml_string):
    doc = xmltodict.parse(xml_string)
    return [
        retrieve.Type(
            x['name'],
            x['members'] if isinstance(x['members'], list) else [x['members']]
        )
        for x in doc['Package']['types']
    ]
