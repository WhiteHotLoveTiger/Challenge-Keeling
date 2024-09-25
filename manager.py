from src.downloader import setup


def run_setup():
    """Call the graph data setup function."""
    print("Running initial graph data setup...", flush=True)
    setup.set_up_graph_data()


def wait_for_queries():
    """Keep container idle but up."""
    print("Waiting for queries...", flush=True)
    input()


if __name__ == "__main__":
    run_setup()
    wait_for_queries()
