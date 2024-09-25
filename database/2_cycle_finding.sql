CREATE TYPE stack_item AS (
    current_node character varying,
    path text[],
    total_cost double precision
);

CREATE OR REPLACE FUNCTION find_cycles(curr_graph_id varchar(64))
RETURNS TABLE(cycle_path text[]) AS
$$
DECLARE
    stack stack_item[] = '{}';
    stack_item stack_item;
    current_node character varying;
    path text[] = '{}';
    next_node character varying;
    cycle_start character varying;
BEGIN
    FOR current_node IN
        SELECT node_id FROM nodes WHERE graph_id = curr_graph_id ORDER BY node_id
    LOOP
        stack = stack || (ROW(current_node, ARRAY[current_node], 0.0)::stack_item);
    END LOOP;

    WHILE array_length(stack, 1) > 0 LOOP
        -- Pop the top element from the stack
        stack_item = stack[array_upper(stack, 1)];
        stack = array_remove(stack, stack_item);
        current_node = stack_item.current_node;
        path = stack_item.path;

        -- Explore neighbours of the current node
        FOR next_node IN
            SELECT to_node FROM edges WHERE from_node = current_node AND graph_id = curr_graph_id
        LOOP
            -- Check if we've seen this node in the current path
            IF next_node = ANY(path) THEN
                -- Remove the nodes from before the cycle started
                WHILE path[1] != next_node LOOP
                    path = path[2:];
                END LOOP;
                -- Rotate the cycle to start from the lexicographically smallest node
                -- Get the smallest node id in the cycle
                SELECT min(node) FROM unnest(path) AS node
                    INTO cycle_start;
                -- Move first node to the end of the path array until cycle_start is at the beginning
                WHILE path[1] != cycle_start LOOP
                    path = path[2:] || path[1];
                END LOOP;
                -- Return the sorted path
                RETURN QUERY SELECT path;
            ELSE
                -- Push the next node onto the stack with the updated path
                stack = stack || (ROW(next_node, path || next_node, 0.0)::stack_item);
            END IF;
        END LOOP;
    END LOOP;

    RETURN;
END;
$$ LANGUAGE plpgsql;

-- Usage:
-- SELECT DISTINCT cycle_path FROM find_cycles('g13') ORDER BY cycle_path;
