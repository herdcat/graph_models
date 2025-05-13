import json
from neo4j import GraphDatabase

def get_aura_neo4j_client(uri, user, password):
    """
    Returns a Neo4j client connected to the Aura instance.

    :param uri: The URI of the Neo4j Aura instance (e.g., "neo4j+s://<your-database-id>.databases.neo4j.io")
    :param user: The username for authentication
    :param password: The password for authentication
    :return: A Neo4j driver instance
    """
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver

class ObjectifyLanguageArabic:
    """
    This class processes a JSON file representing a graph structure and generates Cypher statements for Neo4j.
    The expected json structure is like root.voice.tense.person.gender.number
    """
    def __init__(self, json_file):
        self.json_file = json_file
        self.graph_data = self.load_json()
        self.cypher_statements = []

    def load_json(self):
        with open(self.json_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_root(self):
        return list(self.graph_data)[0]
    
    def get_voices(self):
        return list(self.graph_data[self.get_root()].keys())
    
    def get_tenses(self, voice):
        return [x for x in self.graph_data[self.get_root()][voice].keys() if "participle" not in x.lower() and "masdar" not in x.lower()]
    
    def get_participles(self, voice):
        return [x for x in self.graph_data[self.get_root()][voice].keys() if "participle" in x.lower()]
    
    def get_persons(self, voice, tense):
        return list(self.graph_data[self.get_root()][voice][tense].keys())
    
    def get_genders(self, voice, tense, person):
        return list(self.graph_data[self.get_root()][voice][tense][person].keys())
    
    def get_numbers(self, voice, tense, person, gender):
        return list(self.graph_data[self.get_root()][voice][tense][person][gender].keys())
    
    def get_participle_numbers(self, voice, tense, gender):
        return list(self.graph_data[self.get_root()][voice][tense][gender].keys())
    
    def get_conjugated_verb(self, voice, tense, person, gender, number):
        return self.graph_data[self.get_root()][voice][tense][person][gender][number]
    
    def get_participle_conjugated_verb(self, voice, tense, gender, number):
        return self.graph_data[self.get_root()][voice][tense][gender][number]
    
    def get_masdar_conjugated_verb(self, voice, tense):
        return self.graph_data[self.get_root()][voice][tense]['default']
    
    def get_masdar_conjugated_alternatives(self, voice, tense):
        return self.graph_data[self.get_root()][voice][tense]['alternates']
    
    def create_root_cypher(self):
        root = self.get_root()
        cypher = f"MERGE (n:Root {{name: '{root}'}})"
        # self.cypher_statements.append(cypher)
        return cypher
    
    def create_voice_cypher(self, voice):
        root = self.get_root()
        cypher = f"""MERGE (v:Voice {{name: '{voice}', root: '{root}'}})
        MERGE (r:Root {{name: '{root}'}})
        MERGE (r)-[:VOICED_AS]->(v)
        """
        return cypher
    
    def create_tense_cypher(self, voice, tense):
        root = self.get_root()
        cypher = f"""MERGE (t:Tense {{name: '{tense}', voice: '{voice}', root: '{root}'}})
        MERGE (v:Voice {{name: '{voice}', root: '{root}'}})
        MERGE (v)-[:TENSED_AS]->(t)
        """
        return cypher
    
    def create_person_cypher(self, voice, tense, person):
        root = self.get_root()
        cypher = f"""MERGE (p:Person {{name: '{person}', voice: '{voice}', tense: '{tense}', root: '{root}'}})
        MERGE (t:Tense {{name: '{tense}', voice: '{voice}', root: '{root}'}})
        MERGE (t)-[:PERSONED_AS]->(p)
        """
        return cypher
    
    def create_gender_cypher(self, voice, tense, person, gender):
        root = self.get_root()
        cypher = f"""MERGE (g:Gender {{name: '{gender}', voice: '{voice}', tense: '{tense}', person: '{person}', root: '{root}'}})
        MERGE (p:Person {{name: '{person}', voice: '{voice}', tense: '{tense}', root: '{root}'}})
        MERGE (p)-[:GENDERED_AS]->(g)
        """
        return cypher
    
    def create_participle_gender_cypher(self, voice, tense, gender):
        root = self.get_root()
        cypher = f"""MATCH (t:Tense {{name: '{tense}', voice: '{voice}', root: '{root}'}})
        MERGE (g:Gender {{name: '{gender}', voice: '{voice}', tense: '{tense}',  root: '{root}'}})
        MERGE (t)-[:GENDERED_AS]->(g)
        """
        return cypher
    
    def create_participle_number_cypher(self, voice, tense, gender, number):
        root = self.get_root()
        cypher = f"""MERGE (n:Number {{name: '{number}', voice: '{voice}', tense: '{tense}', gender: '{gender}', root: '{root}'}})
        MERGE (g:Gender {{name: '{gender}', voice: '{voice}', tense: '{tense}', root: '{root}'}})
        MERGE (g)-[:NUMBERED_AS]->(n)
        """
        return cypher
    
    def create_participle_conjugated_verb_cypher(self, voice, tense, gender, number, conjugated_verb):
        root = self.get_root()
        cypher = f"""MERGE (c:ConjugatedVerb {{name: '{conjugated_verb}', voice: '{voice}', tense: '{tense}', gender: '{gender}', number: '{number}', root: '{root}'}})
        MERGE (n:Number {{name: '{number}', voice: '{voice}', tense: '{tense}', gender: '{gender}', root: '{root}'}})
        MERGE (n)-[:CONJUGATED_AS]->(c)
        """
        return cypher
    
    def create_masdar_conjugated_verb_cypher(self, voice, tense, conjugated_verb, conjugated_alternatives):
        root = self.get_root()
        cypher = f"""MERGE (c:ConjugatedVerb {{name: '{conjugated_verb}', voice: '{voice}', tense: '{tense}', root: '{root}'}})
        SET c.alternatives = {conjugated_alternatives}
        MERGE (t:Tense {{name: '{tense}', voice: '{voice}', root: '{root}'}})
        MERGE (t)-[:CONJUGATED_AS]->(c)
        """
        return cypher
    
    def create_number_cypher(self, voice, tense, person,gender, number):
        root = self.get_root()
        cypher = f"""MERGE (n:Number {{name: '{number}', voice: '{voice}', tense: '{tense}', person: '{person}', gender: '{gender}', root: '{root}'}})
        MERGE (g:Gender {{name: '{gender}', voice: '{voice}', tense: '{tense}', person: '{person}', root: '{root}'}})
        MERGE (g)-[:NUMBERED_AS]->(n)
        """
        return cypher
    
    def create_conjugated_verb_cypher(self, voice, tense, person, gender, number, conjugated_verb):
        root = self.get_root()
        cypher = f"""MERGE (c:ConjugatedVerb {{name: '{conjugated_verb}', voice: '{voice}', tense: '{tense}', person: '{person}', gender: '{gender}', number: '{number}', root: '{root}'}})
        MERGE (n:Number {{name: '{number}', voice: '{voice}', tense: '{tense}', person: '{person}', gender: '{gender}', root: '{root}'}})
        MERGE (n)-[:CONJUGATED_AS]->(c)
        """
        return cypher
    
    def run_create_all(self):
        connector = GraphDatabase.driver("bolt://localhost:7687", auth=None)
        with connector.session() as session:
            session.run(self.create_root_cypher())
            for voice in self.get_voices():
                session.run(self.create_voice_cypher(voice))
                for tense in self.get_tenses(voice):
                    session.run(self.create_tense_cypher(voice, tense))
                    for person in self.get_persons(voice, tense):
                        session.run(self.create_person_cypher(voice, tense, person))
                        for gender in self.get_genders(voice, tense, person):
                            session.run(self.create_gender_cypher(voice, tense, person, gender))
                            for number in self.get_numbers(voice, tense, person, gender):
                                session.run(self.create_number_cypher(voice, tense, person, gender, number))
                                conjugated_verb = self.get_conjugated_verb(voice, tense, person, gender, number=number)
                                session.run(self.create_conjugated_verb_cypher(voice, tense, person, gender, number, conjugated_verb))
                for participle in self.get_participles(voice):
                    session.run(self.create_tense_cypher(voice, participle))
                    session.run(self.create_participle_gender_cypher(voice, tense, gender))
                    for number in self.get_participle_numbers(voice, participle, gender):
                        session.run(self.create_participle_number_cypher(voice, participle, gender, number))
                        participle_verb = self.get_participle_conjugated_verb(voice, participle, gender, number)
                        session.run(self.create_participle_conjugated_verb_cypher(voice, participle, gender, number, participle_verb))
                try:
                    for tense in ['masdar']:
                        session.run(self.create_tense_cypher(voice, tense))
                        try:
                            conjugated_verb = self.get_masdar_conjugated_verb(voice, tense)
                            alternate_conjugations = self.get_masdar_conjugated_alternatives(voice, tense)
                            session.run(self.create_masdar_conjugated_verb_cypher(voice, tense, conjugated_verb, alternate_conjugations))
                        except KeyError as e:
                            print(f"KeyError while processing masdar conjugations for voice '{voice}' and tense '{tense}': {e}")
                        except Exception as e:
                            print(f"Unexpected error while processing masdar conjugations for voice '{voice}' and tense '{tense}': {e}")
                except Exception as e:
                    print(f"Unexpected error while processing masdar tense for voice '{voice}': {e}")
                        # session.run(self.create_person_cypher(voice, participle, person))
# create_commands = []
ola= ObjectifyLanguageArabic("./new_structure.json")
ola.run_create_all()
