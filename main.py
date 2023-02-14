from datasource_mappings.csv import *
from datasource_mappings.rdbsm import *
from datasource_mappings.json import *
from datasource_mappings.reusable_modules.error_gui import error_message
from datasource_mappings.reusable_modules.gui_interface import main_interface, upload_neo4j_gui

semantic_dic_url = {
    'SEMANCO': 'http://semanco-tools.eu/ontology-releases/eu/semanco/ontology/SEMANCO/SEMANCO.owl',
    'SAREF4ENER for Energy Domain': 'https://saref.etsi.org/saref4ener/v1.1.2/saref4ener.rdf',
    'SAREF4ENER for Smart Applications': 'https://saref.etsi.org/core/v3.1.1/saref.rdf'}


def process_gui(values, semantic_dic_url):
    try:
        if values['ontology_url_empty'] is None or values['ontology_url_empty'] == '':
            onto = get_onto(values['ontology'], semantic_dic_url)
            ontology_uri = (semantic_dic_url[values['ontology']])
        else:
            onto = get_onto(None, values)
            ontology_uri = values['ontology_url_empty']
        return onto, ontology_uri
    except Exception as process_gui_error_message:
        error_message(process_gui_error_message)


if __name__ == '__main__':
    values = main_interface()
    set_onto, ontology_uri = process_gui(values, semantic_dic_url)
    if values['datasource'] == "CSV":
        csv_to_ontology(values['Browse'], set_onto)
        neo4j_values = upload_neo4j_gui()
    elif values['datasource'] == "RDBSM":
        sql_to_ontology(set_onto, values['Browse'], 'localhost', 'power_plant', 'root', 'JhianJilliane1221!', ontology_uri)
        neo4j_values = upload_neo4j_gui()
    elif values['datasource'] == "JSON":
        json_to_ontology(values['Browse2'], set_onto)
    # elif values['datasource'] == "Text":