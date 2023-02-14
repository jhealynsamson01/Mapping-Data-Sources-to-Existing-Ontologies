# Upload ontology to Neo4j for graphing
from neo4j import GraphDatabase


class Neo4j_connection:  # neo4jconnection #used to be COnnect2Neo4j

    def __init__(self, uri, user, pwd,
                 database_name="neo4j"):  # connect to the server; create constraint if not exist; default database is "Neo4j"
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        self.__database_name = database_name

        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create driver:", e)

        # check if the neccessary config already existed. if not, create.
        query_string = '''
        CALL db.constraints()
                 '''
        a = self.query(query_string, db=self.__database_name)
        constr = str(a)
        try:
            b = constr[constr.find("description='") + 13:constr.find(' ON')]
        except Exception as e:
            pass
        if b == 'CONSTRAINT':
            print("Constraint already existed")
        else:
            try:
                query_string = '''
                    CREATE CONSTRAINT n10s_unique_uri FOR (r:Resource) REQUIRE r.uri IS UNIQUE  
                            '''
                self.query(query_string, db=self.__database_name)
            except Exception as e:
                print("Failed to create constraint - check again", e)

        # check if the neccessary config already existed. if not, create.
        query_string = '''
        match(n) return count(n)
        '''
        a = self.query(query_string, db=self.__database_name)
        strin = str(a[0])
        config_check = int(strin[strin.find("=") + 1:strin.find(">")])
        if config_check != 0:
            print("Config already existed")
        else:
            try:  # setting up neccessary config for neosemantics
                query_string = '''
                    CALL n10s.graphconfig.init()
                                '''
                self.query(query_string, db=self.__database_name)

            except Exception as e:
                print("Failed to initiate graphconfig: ", e)

    def uploading_orx(self, address, db="neo4j"):  # uploading OWL, RDF, and XML #i am trying to
        query_string = (
                "call n10s.rdf.import.fetch('" + address + "','RDF/XML'," + "{" + "verifyUriSyntax: false" + "}" + ")")
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query_string))
            print("Sucessfully uploaded XML/RDF/OWL file ")
        except Exception as e:
            print("Upload failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

    def uploading_ttl(self, address, db=None):  # uploading Turtle files
        query_string = (
                "call n10s.rdf.import.fetch(" + f'{address}' + ',"Turtle",{verifyUriSyntax: false})')
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query_string))
            print("Sucessfully uploaded TTL file ")
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):  # query commands of choice.
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response


def upload_to_neo4j(uri, user, pwd, database_name):
    a = Neo4j_connection(uri, user, pwd, database_name)
    a.uploading_orx("../output_files/ontology_template.rdf", "neo4j")
