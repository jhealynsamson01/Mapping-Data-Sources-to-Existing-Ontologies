# Task: Preprocessing the uploaded file. Clean up Column Names
import pandas as pd
import mysql.connector
import re
from datasource_mappings.reusable_modules.sbert import *
from datasource_mappings.reusable_modules.load_ontology import fetch_ontology_classes, create_new_class
from datasource_mappings.reusable_modules.gui_interface import right_class_mapping
from rdflib import Graph, URIRef, Literal, RDFS, OWL, RDF, BNode, Namespace
import warnings
warnings.filterwarnings('ignore')

class RDBSM:
    def __init__(self, onto, df, host, database_name, username, password, database_all_results, database_column_only):
        self.__onto = onto
        self.__df = df
        self.__host = host
        self.__database_name = database_name
        self.__username = username
        self.__password = password
        self.__database_all_results = database_all_results
        self.__connection = None
        self.__database_column_only = database_column_only

    def preprocessing(self, dataset):
        keywordsList = []

        for clUpperCase in dataset:
            for i in dataset[clUpperCase]:
                keywordsList.append(i)
        return keywordsList

    def get_column_names(self, dataset):
        column_names = []
        tempdf = pd.DataFrame(dataset)
        for i in tempdf:
            column_names.append(i)
        return column_names

    def make_multiple_dataframes(self, sql_result):
        dataset = pd.DataFrame(sql_result)
        return dataset

    def connection(self):
        self.__connection = mysql.connector.connect(
            host=self.__host,
            database=self.__database_name,
            user=self.__username,
            password=self.__password,
            auth_plugin='mysql_native_password')

    def query(self):
        tables = pd.read_sql('show tables;', self.__connection)
        tablesdf = pd.DataFrame(tables)
        column = self.preprocessing(tablesdf)
        for i in column:
            query = 'SELECT * FROM ' + i + ';'
            columnData = pd.read_sql(query, self.__connection)
            column_name = self.get_column_names(columnData)
            self.__database_column_only.update({i: column_name})
            columnData2 = self.make_multiple_dataframes(columnData)
            self.__database_all_results.update({i: columnData2})
            self.__connection.cursor()
        return tablesdf

    def close_connection(self, connection, cursor):
        if connection.is_connected():
            cursor.close()
            connection.close()

    def match_relationships(self):
        temp = []
        for i in self.__database_column_only:
            first_column = self.__database_column_only[i][0]
            for j in self.__database_column_only.items():
                if first_column in j[1]:
                    x = (i, j[0])
                    temp.append(x)
        for i in temp:
            if i[0] == i[1]:
                temp.remove(i)
        return temp

    # def add_relationship_SQL(self, list_of_classes, combined_dicitonary):
    #     for i in list_of_classes:
    #         ontoClass1 = self.__onto[str(combined_dicitonary[i[0]])]
    #         ontoClass2 = self.__onto[str(re.sub("^[^.]*.", "", str(combined_dicitonary[i[1]])))]
    #         with self.__onto:
    #             class has(ontoClass1 >> ontoClass2):
    #                 pass

    def preprocessing_for_data_property(self, temp):
        newrelationships = {}
        for i in self.__database_all_results:
            newrelationships[i] = []
        for i in self.__database_all_results:
            for x in temp:
                if i == x[0]:
                    newrelationships[i].append(x[1])
        return newrelationships

    def add_instance_to_classes(self, database_all, combined_dicitonary):
        for i in database_all:
            j = pd.DataFrame(database_all[i])
            k = j.iloc[:, 0]
            # l = j.iloc[:, 1:]
            if len(j) != 0:
                for k_index in range(len(k)):
                    ontoclass = str(re.sub("^[^.]*.", "", str(combined_dicitonary[i])))
                    if ontoclass is None:
                        ontoclass =  combined_dicitonary[i]
                        self.__onto[str(ontoclass)](
                            str(k[k_index]).replace(" ", ""))

    def save_ontology(self):
        try:
            self.__onto.save(file="datasource_mappings/output_files/ontology_template.rdf", format="rdfxml")
        except ValueError:
            error_message = ("Error. Cannot Save ontology as RDF File due to: ", ValueError)
            return error_message

    def set_class_relationships_rdflib(self, ontology_uri, newrelationships):
        base_iri = self.__onto.base_iri
        namespace = Namespace(ontology_uri)
        g = Graph()
        g.bind("", namespace)
        g.parse('datasource_mappings/output_files/ontology_template.rdf')
        for i in self.__database_all_results:
            j = pd.DataFrame(self.__database_all_results[i])
            k = j.iloc[:, 0]
            l = j.iloc[:, 1:]
            if len(j) != 0:
                for kindex in range(len(k)):
                    targetnode = URIRef(base_iri + str(k[kindex]).replace(" ", ""))
                    for x, y in l.items():
                        for yindex in range(len(y)):
                            if kindex == yindex:
                                g.add((targetnode, namespace[str(x)], Literal(str(y[yindex]).replace(" ", ""))))

            lists = []
            for i in newrelationships:
                for x in range(len(newrelationships[i])):
                    if x is not None:
                        temptemp = pd.DataFrame(self.__database_all_results[i])
                        query1 = ("Select * from " + newrelationships[i][x])
                        columnData = pd.read_sql(query1, self.__connection)
                        columnname = self.get_column_names(columnData)
                        for c in columnname:
                            if (i == newrelationships[i][x]):
                                continue
                            else:
                                if (c == temptemp.columns[0]):
                                    query2 = ("Select " + columnname[0] + "," + newrelationships[i][x].strip() + "." +
                                              temptemp.columns[0] + " from " + newrelationships[i][
                                                  x].strip() + ", " + i.strip() + " WHERE " + i + "." +
                                              temptemp.columns[0] + " = " + newrelationships[i][x] + "." + c)
                                    columnData2 = pd.read_sql(query2, self.__connection)
                                    lists.append(columnData2)
            for i in lists:
                j = pd.DataFrame(i)
                k = pd.DataFrame(j.iloc[:, 0])
                l = j.iloc[:, 1:]
                for kindex, kvalues in enumerate(k):
                    for kvalue in k[kvalues]:
                        for x, y in l.items():
                            for yindex in range(len(y)):
                                if kindex == yindex:
                                    node1 = URIRef(base_iri + str(kvalue).replace(" ", ""))
                                    node2 = base_iri + str(y[yindex]).replace(" ", "")
                                    g.add((node1, namespace.foreign_key, URIRef(node2)))


def sql_to_ontology(onto, df, host, database_name, username, password, ontology_uri):
    database_column_only = {}
    database_all = {}
    sql = RDBSM(onto, df, host, database_name, username, password, database_all, database_column_only)
    sql.connection()
    table_sdf = sql.query()
    keywordsList = sql.preprocessing(table_sdf)
    results, create_class, choices, temp_class = s_bert(onto, keywordsList)
    right_class_mapping(choices, create_class, results, temp_class)
    newClasses = create_new_class(onto, create_class)
    if newClasses is None: newClasses = {}
    if temp_class is None: temp_class = {}
    combinedDicitonary = {**results, **newClasses, **temp_class}
    list_of_classes = sql.match_relationships()
    # sql.add_relationship_SQL(list_of_classes, combinedDicitonary)
    newrelationships = sql.preprocessing_for_data_property(list_of_classes)
    sql.add_instance_to_classes(database_all,combinedDicitonary)
    sql.save_ontology()
    sql.set_class_relationships_rdflib(ontology_uri, newrelationships)
