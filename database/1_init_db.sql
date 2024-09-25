-- \c graphs;

CREATE TABLE public.graphs
(
    graph_id character varying(64) NOT NULL,
    name character varying(255) NOT NULL,
    PRIMARY KEY (graph_id)
);
COMMENT ON TABLE public.graphs IS 'Holds a reference for each graph.';
COMMENT ON COLUMN public.graphs.graph_id IS 'The unique identifier for the graph.';
COMMENT ON COLUMN public.graphs.name IS 'The name of the graph.';


CREATE TABLE public.nodes
(
    node_id character varying(64) NOT NULL,
    name character varying(255),
    graph_id character varying NOT NULL,
    CONSTRAINT "Node is unique to graph" PRIMARY KEY (node_id, graph_id),
    CONSTRAINT "Graph reference" FOREIGN KEY (graph_id)
        REFERENCES public.graphs (graph_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
);
COMMENT ON TABLE public.nodes IS 'Details for each node.';
COMMENT ON CONSTRAINT "Node is unique to graph" ON public.nodes IS 'The unique identifier for the node.';
COMMENT ON CONSTRAINT "Graph reference" ON public.nodes IS 'Each node must belong to a graph.';
COMMENT ON COLUMN public.nodes.node_id IS 'The unique identifier for the node (for a given graph).';
COMMENT ON COLUMN public.nodes.name IS 'The name of the node.';
COMMENT ON COLUMN public.nodes.graph_id IS 'The graph the node belongs to.';


CREATE TABLE public.edges
(
    edge_id character varying(64) NOT NULL,
    from_node character varying(64) NOT NULL,
    to_node character varying(64) NOT NULL,
    cost double precision NOT NULL,
    graph_id character varying NOT NULL,
    CONSTRAINT "Edge is unique to graph" PRIMARY KEY (edge_id, graph_id),
    CONSTRAINT "From-Node reference" FOREIGN KEY (from_node, graph_id)
        REFERENCES public.nodes (node_id, graph_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT "To-Node Reference" FOREIGN KEY (to_node, graph_id)
        REFERENCES public.nodes (node_id, graph_id) MATCH SIMPLE
        ON UPDATE CASCADE
        ON DELETE CASCADE
);
COMMENT ON TABLE public.edges IS 'Details for each edge.';
COMMENT ON CONSTRAINT "Edge is unique to graph" ON public.edges IS 'The unique identifier for the edge.';
COMMENT ON CONSTRAINT "From-Node reference" ON public.edges IS 'Each from_node must reference a node in the same graph.';
COMMENT ON CONSTRAINT "To-Node Reference" ON public.edges IS 'Each to_node must reference a node in the same graph.';
COMMENT ON COLUMN public.edges.edge_id IS 'The unique identifier for the edge.';
COMMENT ON COLUMN public.edges.from_node IS 'The node the edge starts from.';
COMMENT ON COLUMN public.edges.to_node IS 'The node the edge ends at.';
COMMENT ON COLUMN public.edges.cost IS 'The cost of traversing the edge.';
COMMENT ON COLUMN public.edges.graph_id IS 'The graph the edge belongs to.';
