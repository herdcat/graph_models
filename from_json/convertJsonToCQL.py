import json

def generate_cypher_queries(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    queries = []
    node_counter = 0

    def process_node(node, parent_id=None):
        nonlocal node_counter
        node_id = f"node{node_counter}"
        node_counter += 1

        label = node.get("label", "Node")
        value = node.get("value", "")
        lineage = node.get("lineage", {})
        lineage_properties = ", ".join([f"{key}: '{value}'" for key, value in lineage.items()])
        queries.append(f"MERGE ({node_id}:{label} {{name: '{value}'{', ' + lineage_properties if lineage_properties else ''}}})")

        if parent_id:
            queries.append(f"MERGE ({parent_id})-[:HAS_CHILD]->({node_id})")

        children = node.get("children", [])
        for child in children:
            process_node(child, node_id)

    process_node(data)
    return queries

def write_cypher_to_file(queries, output_file):
    with open(output_file, 'w') as file:
        for query in queries:
            file.write(query + ";\n")

if __name__ == "__main__":
    input_json = "labeled_nested_conjugations.json"
    output_cypher = "create_graph.cypher"

    cypher_queries = generate_cypher_queries(input_json)
    write_cypher_to_file(cypher_queries, output_cypher)

    print(f"Cypher queries have been written to {output_cypher}")