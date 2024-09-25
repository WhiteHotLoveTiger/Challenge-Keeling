# Tucows Code Challenge - Alex Keeling

This is Alex Keeling's submission for the Tucows Backend Software Engineer Code Challenge. This submission uses mainly Python with some Bash glue and some PL/pgsql.

## Set up

Use Docker to get the project running:

```bash
$ docker compose up
```
There are three containers:

- **xml-server** - An nginx server serving sample XML files. Files come from `sample_graph_data/`
- **db** - A PostGres server. The schema and functions come from `database/`
- **graph-info** - Where our Python code runs. Code is located in `src/` and `tests/`

## Usage

Once you run `docker compose up`, The `graph-info` container will satisfy ***Challenge Requirement 1*** by downloading an XML file with graph data from the `xml-server` container. The specific endpoint is set in `compose.yaml` as the `GRAPH_DATA_ENDPOINT` environment variable for the `graph-info` image. The code for this is located in `src/downloader/setup.py`. The function `set_up_graph_data()` starts this process.

Once we have the file, we move on to ***Challenge Requirement 2***. Still in `src/downloader/setup.py`, the XML is parsed and and verified for correctness. I made use of the standard library's `xml.etree.ElementTree` to parse the XML, because we're not doing any complex operations, and we assume the XML is coming from a trusted source. If we needed better performance or more complex handling of XML, I'd consider a library like `LXML`, or `defusedxml` if we didn't trust the source.

Finally the graph data is sent to the database container `db` for insertion. 

Note: I'm using the `psycopg2-binary` for simplicity with this project, but in a real application, I'd set things up to build `psycopg2` and do some work to still keep the container sizes small.

Our database schema can be seen in `database/1_init_db.sql`. This normalized model satisfies ***Challenge Requirement 3***. See the file for details, but in brief, we have three tables:

- graphs
  - graph_id
  - name
- nodes
  - node_id
  - name
  - graph_id
- edges
  - edge_id
  - from_node
  - to_node
  - cost
  - graph_id

All fields are varchars except `cost`, which is a double. Please see the schema file for keys and other details.

Along with `database/1_init_db.sql`, the `postgres` container is also loaded with `database/2_cycle_finding.sql`. This file creates the PL/pgsql function `find_cycles()` to meet ***Challenge Requirement 4***. To run it, connect to the database, either using a tool like pgAdmin with the connection info in `compose.yaml` (db: graphs, user: postgres, password: password, port: 55432) or via the command line:

```bash
$ docker exec -it postgres psql -U postgres
```
Make sure to connect to the `graphs` database:
```
postgres=# \c graphs
```
And try the function:
```sql
graphs=# graphs=# SELECT DISTINCT cycle_path FROM find_cycles('g13') ORDER BY cycle_path;
 cycle_path
------------
 {a,b,c}
 {a,d,c}
 {a,d,e,c}
 {b}
 {b,c}
 {c}
 {c,d}
 {c,d,e}
(8 rows)
```
`find_cycles()` has a single `graph_id` parameter. Not sure which `graph_id`s are available? You can check:
```sql
graphs=# SELECT * from public.graphs;
 graph_id |                 name
----------+--------------------------------------
 g13      | Graph with Multiple Paths and Cycles
(1 row)
```

This brings us to ***Challenge Requirement 5***: handling JSON on stdin & stdout. In the `graph-info` container where the Python code runs, we started off with parsing and inserting the graph data, but when it was done, it kept the container up (via the container's `manager.py` file, called from the Dockerfile's `CMD`).
By keeping the container up, it's very responsive to queries about paths and cheapest routes (though not strictly needed). `graph-info` hosts a Python module called `query_service` which handles incoming JSON, querying the DB, and responding. You can call it like this:
```bash
$ cat sample_query_data/sample_query_2.json | docker exec -i graph_info python src/query_service/query_listener.py
```
But for convenience, there's a bash wrapper script you can use:
```bash
$ cat sample_query_data/sample_query_2.json | ./query.sh
``` 
This returns a pretty-printed JSON response. It can be a lot of lines! If you need it shortened up, try `jq --compact-output`:
```bash
$ cat sample_query_data/sample_query_2.json | ./query.sh | jq --compact-output
{"answers":[{"paths":{"from":"a","to":"d","paths":[["a","d"]]}},{"cheapest":{"from":"a","to":"d","path":["a","d"]}},{"paths":{"from":"a","to":"c","paths":[["a","d","c"],["a","d","e","c"],["a","b","c"]]}},{"cheapest":{"from":"a","to":"c","path":["a","b","c"]}}]}
``` 
The `query_service` reads from stdin and parses the input as JSON. I simply used the built-in `json.loads()` module for converting JSON to a string. Once it's in a `dict`, it's easy to work with, and similarly, when it's time to send the response, I build it up as a Python object and send it back using `json.dumps()`. This library is built-in and easy to use. I don't see any need for a more specialized or performant library.

Once it has a complete JSON document, the `query_service` pulls out the details for each query and calls the PL/pgsql function, `find_all_paths()`. This is defined in `database/3_path_finding.sql`. 

Try it manually if you like:
```sql
graphs=# SELECT * FROM find_all_paths('a', 'c', 'g13');
   path    | total_cost
-----------+------------
 {a,d,c}   |        2.5
 {a,d,e,c} |        2.5
 {a,b,c}   |          2
(3 rows)
```
It returns both the paths and the cost of each path, so that we can use the result for both find all paths as well as finding the cheapest path. See the details in the SQL file, but this function does a Depth First Search through the nodes in the given graph, skipping nodes it's seen before to avoid cycles, and stopping when it end the node it's looking for, and adding a path to the results. Because it keeps track of the cost as it goes, it returns all the details needed for both a *paths* query as well as a *cheapest* query.

In fact, on the Python side, I don't bother calling the database a second time if we've got both a *paths* and *cheapest* query with the same set of nodes. I just reuse the data from the first call, and pull out the relevant data for the requested query.

## Tests
To run the tests, you can use pytest:
```bash
$ python -m pytest
```
You may need to create/enter the virtual environment first, and install the requirements:
```bash
$ python -m venv .venv
$ . ./.venv/bin/activate
(.venv) $ pip install -r requirements.txt
(.venv) $ python -m pytest
```

## Done is better than perfect
There are lots of areas that could be improved with more time and a better understanding 
of which aspects of the project are most important to the clients. It's working, but given 
more time, I'd look into:

### Improving the PL/pgsql functions
I've done lots of modeling and SQL statements before, but this project was my first time 
using PL/pgsql. I read a tutorial, glanced through the documentation and a couple videos, and had 
some assistance from ChatGPT. It's working, but I'd like to practice it more to be able to 
write it more idiomatically. As well, I've heard there are options to write tests for it, 
but I didn't invest time in that area for this challenge.

### More test coverage
The unit testing coverage isn't terrible, but I don't have proper tests for the functions 
which connect to the PostGres database. There are different options here for how to proceed,
and I'd like to explore them more.

I'd also like to clean up and better organize the tests. The test files started small and 
grew quickly. I'd like to refactor them to be more readable. Perhaps into a few classes, or
maybe more files.

### More robust error handling
I've done some error handling, but I'd like to do more. 

### Tidier Dockerfiles
Docker is working, but the main image where Python runs is just grabbing everything in the 
project directory. I'd like to clean this up and just pull in what's needed.

### Secrets management
Because this is a toy project, I've just put the postgres password in plaintext in the 
docker compose file. In a real project, I'd use a secrets manager or some other method to
keep it secure.

