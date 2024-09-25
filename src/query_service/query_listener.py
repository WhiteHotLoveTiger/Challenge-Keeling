import json
import sys

import psycopg2

from src.db_connection.postgres import get_db_connection


def get_graph_id():
    with open("graph_id.txt", "r") as file:
        return file.read().strip()


def get_query_type_and_nodes(query):
    if "paths" in query:
        query_type = "paths"
    else:
        query_type = "cheapest"
    return query_type, query[query_type]["start"], query[query_type]["end"]


def process_queries(queries):
    graph_id = get_graph_id()
    results = {}

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for query in queries["queries"]:
                query_type, start, end = get_query_type_and_nodes(query)
                other_query_type = "cheapest" if query_type == "paths" else "paths"

                if (start, end, query_type) in results:
                    continue
                if (start, end, other_query_type) in results:
                    # Don't hit DB again for the same set of nodes. Both query types
                    # share the same results, we just pull out different info.
                    results[(start, end, query_type)] = results[(start, end, other_query_type)]
                    continue
                else:
                    try:
                        cur.execute("SELECT * FROM find_all_paths(%s, %s, %s);",
                                    (start, end, graph_id))
                        paths = cur.fetchall()
                        results[(start, end, query_type)] = paths
                    except psycopg2.Error as e:
                        print(f"Database error: {e}")
                        return None
    return results


def tidy_up_results(results):
    """Clean up the results to make them easier to work with."""
    tidy_results = []
    for (start, end, query_type), paths in results.items():
        if query_type == "paths":
            tidy_result = format_paths_result(start, end, paths)
        else:
            tidy_result = format_cheapest_result(start, end, paths)
        tidy_results.append(tidy_result)
    # tidy_results looks like:
    # [ ("paths", "a", "c", [["a","b","c"], ["a","c"], ...]), ("cheapest", "a", "c", ["a","c"]), ... ]
    return tidy_results

def format_paths_result(start, end, paths):
    paths_list = [path[0] for path in paths]  # Drop the cost info
    return "paths", start, end, paths_list

def format_cheapest_result(start, end, paths):
    # Sort paths by the cost (second element of each path tuple)
    sorted_list = sorted(paths, key=lambda x: x[1])
    # The cheapest path is the first one in the sorted list
    # If there are no paths, we return False
    cheapest_path = sorted_list[0][0] if sorted_list else False
    return "cheapest", start, end, cheapest_path


def format_results_to_json(results):
    formatted_results = {"answers": []}
    for result in results:
        query_type, start, end, data = result
        formatted_result = {
            query_type: {"from": start, "to": end, "paths": data}
        }
        formatted_results["answers"].append(formatted_result)

    return json.dumps(formatted_results, indent=2)


def verify_correct_query_format(queries):
    if "queries" not in queries:
        return False
    if not isinstance(queries["queries"], list):
        return False
    for query in queries["queries"]:
        if not isinstance(query, dict):
            return False
        if "paths" not in query and "cheapest" not in query:
            return False
        if "paths" in query and "cheapest" in query:
            return False
        if "paths" in query and ("start" not in query["paths"] or "end" not in query["paths"]):
            return False
        if "cheapest" in query and ("start" not in query["cheapest"] or "end" not in query["cheapest"]):
            return False
    return True

def verify_valid_json(query):
    try:
        return json.loads(query)
    except json.decoder.JSONDecodeError:
        return None


def receive_and_send_query():
    query_str = sys.stdin.read()
    query = verify_valid_json(query_str)

    if not query or not verify_correct_query_format(query):
        print("Invalid format. Please try again. Valid format looks like: "
              '{"queries": [{"paths": {"start": "node id","end": "node id"}}, '
              '{"cheapest": {"start": "node id", "end": "node id"}}]}', flush=True)
        return

    results = process_queries(query)
    tidy_results = tidy_up_results(results)
    result = format_results_to_json(tidy_results)
    print(result, flush=True)



if __name__ == "__main__":
    receive_and_send_query()
