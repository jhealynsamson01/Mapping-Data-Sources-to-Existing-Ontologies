from owlready2 import types, get_ontology, Thing


def load_ontology(ontology_url):
    try:
        onto = get_ontology(ontology_url)
        onto.load()
        return onto

    except Exception as e:
        message = "Failed to Load Ontology:" + e
        return message


def get_onto(ontology_name, ontology_uri):
    if type(ontology_uri) == dict:
        onto = load_ontology(ontology_uri[ontology_name])
    else:
        onto = load_ontology(ontology_uri)
    return onto


def fetch_ontology_classes(onto):
    classes = list(onto.classes())
    newClasses = []
    for i in range(len(classes)): newClasses.append(str(classes[i]))

    return newClasses

def create_new_class(onto, create_class):
    # To do: Create New Class
    y = list(create_class.values())
    SuperClass = onto.Thing  # static value (root class)
    for index, val in enumerate(create_class):
        with onto:
            yvalue = y[index]
            NewClass = types.new_class(yvalue, (Thing,))
    return create_class

def removespaces(var):
    var.replace(" ", "")
    return var

