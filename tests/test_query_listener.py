import io
import json

import pytest

import src.query_service.query_listener as queries
from sample_data import json_samples


def test_get_graph_id(monkeypatch):
    expected_graph_id = "graph 72"
    mock_file_content = f" {expected_graph_id} \t\n"
    mock_file_stream = io.StringIO(mock_file_content)
    monkeypatch.setattr("builtins.open", lambda *args, **kwargs: mock_file_stream)

    graph_id = queries.get_graph_id()
    assert graph_id == expected_graph_id


def test_get_query_type_and_nodes_paths():
    # Input query with "paths" type
    query = {"paths": {"start": "a", "end": "d"}}
    query_type, start_node, end_node = queries.get_query_type_and_nodes(query)

    assert query_type == "paths"
    assert start_node == "a"
    assert end_node == "d"


def test_get_query_type_and_nodes_cheapest():
    # Input query with "cheapest" type
    query = {"cheapest": {"start": "a", "end": "b"}}
    query_type, start_node, end_node = queries.get_query_type_and_nodes(query)

    assert query_type == "cheapest"
    assert start_node == "a"
    assert end_node == "b"


def test_get_query_type_and_nodes_invalid():
    # Invalid query without "paths" or "cheapest"
    query = {}

    with pytest.raises(KeyError):  # Expecting a KeyError for missing keys
        queries.get_query_type_and_nodes(query)


#
# # Mocking the get_graph_id function
# def mock_get_graph_id():
#     return "test_graph_id"
#
#
# @pytest.fixture
# def setup_test_db(postgresql):
#     """
#     This fixture will set up the necessary schema and data for testing.
#     It will create the tables and populate some data.
#     """
#     # Create the necessary tables
#     with postgresql.cursor() as cur:
#         cur.execute("""
#             CREATE TABLE graphs (
#                 graph_id VARCHAR(64) PRIMARY KEY,
#                 name VARCHAR(255)
#             );
#             CREATE TABLE nodes (
#                 node_id VARCHAR(64) NOT NULL,
#                 graph_id VARCHAR(64) NOT NULL,
#                 PRIMARY KEY (node_id, graph_id)
#             );
#             CREATE TABLE edges (
#                 edge_id VARCHAR(64) NOT NULL,
#                 from_node VARCHAR(64) NOT NULL,
#                 to_node VARCHAR(64) NOT NULL,
#                 cost DOUBLE PRECISION NOT NULL,
#                 graph_id VARCHAR(64) NOT NULL,
#                 PRIMARY KEY (edge_id, graph_id)
#             );
#         """)
#         cur.execute("""
#             INSERT INTO graphs (graph_id, name) VALUES
#                 ('test_graph_id', 'Test Graph');
#
#             INSERT INTO nodes (node_id, graph_id) VALUES
#                 ('a', 'test_graph_id'),
#                 ('b', 'test_graph_id'),
#                 ('c', 'test_graph_id');
#
#             INSERT INTO edges (edge_id, from_node, to_node, cost, graph_id) VALUES
#                 ('e1', 'a', 'b', 1.0, 'test_graph_id'),
#                 ('e2', 'b', 'c', 1.5, 'test_graph_id'),
#                 ('e3', 'a', 'c', 2.0, 'test_graph_id');
#         """)
#         postgresql.commit()
#
#
# def test_process_queries(monkeypatch, postgresql, setup_test_db):
#     # Mocking the get_graph_id function
#     monkeypatch.setattr("src.query_service.query_listener.get_graph_id", mock_get_graph_id)
#
#     # Example queries to be processed
#     the_queries = {
#         "queries": [
#             {"paths": {"start": "a", "end": "b"}},
#             {"paths": {"start": "b", "end": "c"}},
#         ]
#     }
#
#     # Run the process_queries function using the temporary PostgreSQL
#     results = queries.process_queries(the_queries)
#
#     # Assert that the results are as expected
#     assert results[('a', 'b', 'paths')] == [('a', 'b', 1.0)]  # Expected path from a to b
#     assert results[('b', 'c', 'paths')] == [('b', 'c', 1.5)]  # Expected path from b to c


def test_tidy_up_results():
    mock_results = {
        ("a", "b", "paths"): [[["a", "b"], 1.0], [["a", "x", "b"], 2.5]],
        ("b", "c", "cheapest"): [[["b", "c"], 1.5]]
    }
    expected_tidy_results = [
        ("paths", "a", "b", [["a", "b"], ["a", "x", "b"]]),
        ("cheapest", "b", "c", ["b", "c"])
    ]
    tidy_results = queries.tidy_up_results(mock_results)

    assert tidy_results == expected_tidy_results


def test_format_paths_result():
    # Mock input: start and end nodes with paths (including costs)
    start = "a"
    end = "b"
    mock_paths = [[["a", "b"], 1.0], [["a", "x", "b"], 2.5]]
    expected_result = ("paths", "a", "b", [["a", "b"], ["a", "x", "b"]])

    result = queries.format_paths_result(start, end, mock_paths)

    assert result == expected_result


def test_format_cheapest_result():
    # Mock input: start and end nodes with paths (including costs)
    start = "a"
    end = "b"
    mock_paths = [[["a", "b"], 1.0], [["a", "x", "b"], 2.5], [["a", "y", "b"], 0.8]]
    expected_result = ("cheapest", "a", "b", ["a", "y", "b"])

    result = queries.format_cheapest_result(start, end, mock_paths)
    assert result == expected_result


def test_format_cheapest_result_no_paths():
    # Test case with no paths provided
    start = "a"
    end = "b"
    mock_paths_empty = []
    expected_result_empty = ("cheapest", "a", "b", False)

    result_empty = queries.format_cheapest_result(start, end, mock_paths_empty)
    assert result_empty == expected_result_empty


def test_format_results_to_json():
    # Mock input: list of results
    mock_results = [
        ("paths", "a", "b", [["a", "b"], ["a", "x", "b"]]),
        ("cheapest", "b", "c", ["b", "c"]),
        ("cheapest", "b", "x", False)
    ]
    expected_json = json.dumps({
        "answers": [
            {
                "paths": {
                    "from": "a",
                    "to": "b",
                    "paths": [["a", "b"], ["a", "x", "b"]]
                }
            },
            {
                "cheapest": {
                    "from": "b",
                    "to": "c",
                    "paths": ["b", "c"]
                }
            },
            {
                "cheapest": {
                    "from": "b",
                    "to": "x",
                    "paths": False
                }
            }
        ]
    }, indent=2)

    result_json = queries.format_results_to_json(mock_results)
    assert result_json == expected_json


def test_verify_correct_query_format_valid_paths():
    # Valid query with "paths"
    query = {
        "queries": [
            {"paths": {"start": "a", "end": "b"}}
        ]
    }
    is_valid = queries.verify_correct_query_format(query)
    assert is_valid is True


def test_verify_correct_query_format_valid_cheapest():
    # Valid query with "cheapest"
    query = {
        "queries": [
            {"cheapest": {"start": "a", "end": "b"}}
        ]
    }
    is_valid = queries.verify_correct_query_format(query)
    assert is_valid is True


def test_verify_correct_query_format_invalid_no_queries():
    # Invalid query without "queries" key
    query = {}
    is_valid = queries.verify_correct_query_format(query)
    assert is_valid is False


def test_verify_correct_query_format_invalid_not_list():
    # Invalid query with "queries" key not a list
    query = {
        "queries": {"cheapest": {"start": "a", "end": "b"}}
    }
    is_valid = queries.verify_correct_query_format(query)
    assert is_valid is False


def test_verify_correct_query_format_invalid_not_dict():
    # Invalid query with query not a dictionary
    query = {
        "queries": [
            ("paths", {"start": "a", "end": "b"})
        ]
    }
    is_valid = queries.verify_correct_query_format(query)
    assert is_valid is False


def test_verify_correct_query_format_invalid_paths_and_cheapest():
    # Invalid query with both "paths" and "cheapest" in the same query
    query = {
        "queries": [
            {"paths": {"start": "a", "end": "b"}, "cheapest": {"start": "a", "end": "b"}}
        ]
    }
    is_valid = queries.verify_correct_query_format(query)
    assert is_valid is False


def test_verify_correct_query_format_missing_path_end():
    # Invalid query with missing "end"
    query = {
        "queries": [
            {"paths": {"start": "a"}}
        ]
    }
    is_valid = queries.verify_correct_query_format(query)
    assert is_valid is False


def test_verify_correct_query_format_missing_path_start():
    # Invalid query with missing "start"
    query = {
        "queries": [
            {"paths": {"end": "b"}}
        ]
    }
    is_valid = queries.verify_correct_query_format(query)
    assert is_valid is False


def test_verify_correct_query_format_missing_cheapest_end():
    # Invalid query with missing "end"
    query = {
        "queries": [
            {"cheapest": {"start": "a"}}
        ]
    }
    is_valid = queries.verify_correct_query_format(query)
    assert is_valid is False


def test_verify_correct_query_format_missing_cheapest_start():
    # Invalid query with missing "start"
    query = {
        "queries": [
            {"cheapest": {"end": "b"}}
        ]
    }
    is_valid = queries.verify_correct_query_format(query)
    assert is_valid is False


def test_verify_correct_query_format_invalid_query_type():
    # Invalid query with unknown query type
    query = {
        "queries": [
            {"unknown": {"start": "a", "end": "b"}}
        ]
    }
    is_valid = queries.verify_correct_query_format(query)
    assert is_valid is False


def test_verify_valid_json_good():
    expected_result = json.loads(json_samples["valid json"])
    result = queries.verify_valid_json(json_samples["valid json"])
    assert result == expected_result


def test_verify_valid_json_bad():
    result = queries.verify_valid_json(json_samples["incomplete"])
    assert result is None


def test_receive_and_send_query_valid(monkeypatch, capsys):
    query_str = '{"queries": [{"paths": {"start": "a", "end": "b"}}]}'
    monkeypatch.setattr("sys.stdin.read", lambda: query_str)

    mock_results = {("a", "b", "paths"): [[["a", "b"], 1.0]]}
    monkeypatch.setattr(queries, "process_queries", lambda q: mock_results)

    # Run the function
    queries.receive_and_send_query()
    captured = capsys.readouterr()
    expected_output = json.dumps({
        "answers": [{"paths": {"from": "a", "to": "b", "paths": [["a", "b"]]}}]
    }, indent=2)

    assert expected_output == captured.out.strip()


def test_receive_and_send_query_invalid_format(monkeypatch, capsys):
    query_str = '{"queries": [{"paths": {"start": "a"}}]}'  # Missing "end" field
    monkeypatch.setattr("sys.stdin.read", lambda: query_str)

    # Run the function
    queries.receive_and_send_query()
    captured = capsys.readouterr()
    expected_error = "Invalid format. Please try again. Valid format looks like: " \
                     '{"queries": [{"paths": {"start": "node id","end": "node id"}}, ' \
                     '{"cheapest": {"start": "node id", "end": "node id"}}]}'
    assert expected_error == captured.out.strip()


def test_receive_and_send_query_invalid_json(monkeypatch, capsys):
    query_str = '{"queries": [{"paths": "start": "a", "end": "b"}'  # Malformed JSON
    monkeypatch.setattr("sys.stdin.read", lambda: query_str)

    # Run the function
    queries.receive_and_send_query()
    captured = capsys.readouterr()
    expected_error = "Invalid format. Please try again. Valid format looks like: " \
                     '{"queries": [{"paths": {"start": "node id","end": "node id"}}, ' \
                     '{"cheapest": {"start": "node id", "end": "node id"}}]}'
    assert expected_error == captured.out.strip()
