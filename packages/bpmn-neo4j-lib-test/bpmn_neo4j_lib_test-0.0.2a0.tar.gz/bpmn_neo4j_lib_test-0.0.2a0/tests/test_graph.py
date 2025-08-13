from bpmn_neo4j.transformers.graph_transformer import GraphTransformer

def test_dummy():
    sample_json = {
        "activities": [],
        "events": [],
        "gateways": [],
        "flows": [],
        "pools": [],
        "lanes": []
    }

    transformer = GraphTransformer(sample_json)
    cypher_list = transformer.transform()

    # Pastikan hasilnya list of string
    assert isinstance(cypher_list, list)
    assert all(isinstance(q, str) for q in cypher_list)
