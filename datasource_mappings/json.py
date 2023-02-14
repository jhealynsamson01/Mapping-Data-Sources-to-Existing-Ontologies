import re
import pandas as pd

from datasource_mappings.reusable_modules.sbert import *
from datasource_mappings.reusable_modules.gui_interface import right_class_mapping
from datasource_mappings.reusable_modules.load_ontology import *

class JSON:

    def __init__(self, file_path, onto, df=None, exclude_column=None):
        self.__file_path = file_path
        self.__onto = onto
        self.__df = df
        self.__exclude_column = exclude_column

    def set_csv_file(self):
        self.__df = pd.read_json(self.__file_path)
        return self.__df

    def pre_processing_csv(self):
        # Task: Preprocessing the uploaded file. Clean up Column Names

        # Check if unique column exists. If not, create one
        if not self.__df.iloc[:, 0].is_unique:
            temp_string = self.__df.columns[0] + " " + self.__df.columns[1]
            self.__df[str(temp_string)] = self.__df.iloc[:, 0].astype(str) + " " + self.__df.iloc[:, 1].astype(str)
            first_col = self.__df.pop(temp_string)
            self.__df.insert(0, str(temp_string), first_col)
            df = self.__df.drop([str(self.__df.columns[1]), str(self.__df.columns[2])], axis=1)
            for i in range(len(df)):
                df[str(temp_string)][i] = str(i) + " " + df[str(temp_string)][i]

        keywords_list = [re.sub("[:,.;'><-=]*", "", clUpperCase) for clUpperCase in self.__df.columns]
        self.__df.columns = keywords_list
        return keywords_list

    def specify_domain_range(self, result, create_class, temp_class):
        # To do: Add relationship to class: Specify Domain and Range. Everything should be related to the unique column in the database
        combined_dicitonary = {**result, **create_class, **temp_class}
        temp_string = self.__df.columns[0]
        target_domain = removespaces(temp_string)
        # m = re.sub("^[^.]*.","",combinedDicitonary[targetdomain])
        targetvalue = combined_dicitonary[target_domain]
        target_domain_class = self.__onto.search_one(iri="*" + (targetvalue.replace(".", "#")))
        self.__exclude_column = self.__df.columns[0]

        for index, val in enumerate(create_class):
            if val is not self.__exclude_column:
                with self.__onto:
                    val = str(val).replace(" ", "")
                    class has(target_domain_class >> self.__onto[str(val)]):
                        pass
        for index2, val2 in enumerate(result):
            if val2 is not self.__exclude_column:
                rangeclass = self.__onto.search_one(iri="*" + result[val2])
                if rangeclass is None:
                    rangeclass = self.__onto.search_one(is_a=self.__onto[str(re.sub("^[^.]*.", "", result[val2]))])
                    with self.__onto:
                        class has(target_domain_class >> rangeclass):
                            pass

        return target_domain_class

    def add_instances_to_class(self, result, temp_class, target_domain_class):
        # To do: Add instances to class (get classes, match right key word to the class and add instance to it)
        temp_combined_dic = {**result, **temp_class}
        objectProperties = list(self.__onto.object_properties())
        index_position_list = []
        for index, val in enumerate(temp_combined_dic):
            temp = re.sub("^[^.]*.", "", temp_combined_dic[val])
            range_class = self.__onto.search_one(iri="*" + temp)
            if range_class is None:
                range_class = self.__onto.search_one(
                    is_a=self.__onto[str(re.sub("^[^.]*.", "", temp))])
            for col in self.__df:
                if col == val:
                    for i, instance in self.__df[col].items():
                        if (instance is not None) and (instance != 0) and (instance != 0.0) and (instance != 'nan'):
                            insert_value = range_class(str(instance))
                            insert_value.label = str(insert_value)
                            if "{" in str(instance) and "}" in str(instance):
                                second_row = re.sub("['/[{}/]]*", "", str(instance))
                                split_second_row = second_row.split(",")
                                for individuals in split_second_row:
                                    fields = individuals.split(':')[0]
                                    values = individuals.split(':')[1]
                                    print(fields, values)
                            else:
                                if col is not self.__exclude_column:
                                    target_domain_class.instances()[i].has.append(insert_value)
                                    for indexObjectProperty in range(len(objectProperties)):
                                        domain_class = objectProperties[indexObjectProperty].domain
                                        range_class_y = objectProperties[indexObjectProperty].range
                                        if (domain_class is not None) and (len(domain_class) == 1) and (domain_class[0] == range_class_y):
                                            index_position_list.append([domain_class[0], insert_value, i])

    def add_instances_to_new_class(self, create_class, target_domain_class):
        # To do: Add instances to the new classes (get classes, match right key word to the class and add instance to it)
        if bool(create_class):
            for index, val in enumerate(create_class):
                for col in self.__df:
                    if col == val:
                        for i, instance in self.__df[col].items():
                            if (instance is not None) and (str(instance) != 0) and (instance != 0.0) and (str(instance) != 'nan'):
                                if "{" in str(instance) and "}" in str(instance):
                                    second_row = re.sub("['/[{}/]]*", "", str(instance))
                                    split_second_row = second_row.split(",")
                                    for individuals in split_second_row:
                                        fields = individuals.split(':')[0]
                                        values = individuals.split(':')[1]
                                        print(fields, values)
                                else:
                                    val = val.replace(" ","")
                                    class_name = self.__onto[str(val)]
                                    temp = class_name(str(instance))
                                    temp.label = str(temp)
                                    if col is not self.__exclude_column:
                                        target_domain_class.instances()[i].has.append(temp)

    def save_ontology(self):
        try:
            self.__onto.save(file="datasource_mappings/output_files/ontology_template.rdf", format="rdfxml")
        except ValueError:
            error_message = ("Error. Cannot Save ontology as RDF File due to: ", ValueError)
            return error_message

def json_to_ontology(file_path, onto):
    json = JSON(file_path, onto, None, None)
    json.set_csv_file()
    keywordsList = json.pre_processing_csv()
    result, createClass, choices, tempClass = s_bert(onto, keywordsList)
    right_class_mapping(choices, createClass, result, tempClass)
    create_new_class(onto, createClass)
    target_domain_class = json.specify_domain_range(result, createClass, tempClass)
    if str(target_domain_class) in str(list(result.values())[0]):
        json.add_instances_to_class(result, tempClass,target_domain_class)
        json.add_instances_to_new_class(createClass,target_domain_class)
    else:
        json.add_instances_to_new_class(createClass,target_domain_class)
        json.add_instances_to_class(result, tempClass, target_domain_class)
    json.save_ontology()