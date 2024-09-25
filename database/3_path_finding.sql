CREATE OR REPLACE FUNCTION find_all_paths(
    start_node character varying,
    end_node character varying,
    curr_graph_id varchar(64)
)
RETURNS TABLE(path text[], total_cost double precision) AS
$$
DECLARE
    stack stack_item[] = '{}';  -- Array to store the stack. stack_item type defined in 2_cycle_finding.sql
    stack_item stack_item;
    current_node character varying;
    path text[] = '{}';
    next_node character varying;
    edge_cost double precision;
    total_cost double precision = 0;
BEGIN
    -- Initialize the stack with the starting node and zero cost
    stack = stack || (ROW(start_node, ARRAY[start_node], 0)::stack_item);

    -- Iterate while the stack is not empty
    WHILE array_length(stack, 1) > 0 LOOP
        -- Pop the top element from the stack
        stack_item = stack[array_upper(stack, 1)];
        stack = array_remove(stack, stack_item);
        current_node = stack_item.current_node;
        path = stack_item.path;
        total_cost = stack_item.total_cost;

        -- If we've reached the end node, return the current path and total cost
        IF current_node = end_node THEN
            RETURN QUERY SELECT path, total_cost;
        END IF;

        -- Explore neighbours of the current node
        FOR next_node, edge_cost IN
            SELECT to_node, cost FROM edges
            WHERE from_node = current_node AND graph_id = curr_graph_id
        LOOP
            -- Check if we've seen this node in the current path
            IF next_node = ANY(path) THEN
                CONTINUE;  -- Skip this node to avoid cycles
            END IF;

            -- Push the next node onto the stack with the updated path and total cost
            stack = stack || (ROW(next_node, path || next_node, total_cost + edge_cost)::stack_item);
        END LOOP;
    END LOOP;

    RETURN;
END;
$$ LANGUAGE plpgsql;

-- Usage:
-- SELECT * FROM find_all_paths('a', 'c', 'g13');
--
-- Get the shortest path:
-- SELECT * FROM find_all_paths('a', 'c', 'g13')
-- ORDER BY total_cost ASC
-- LIMIT 1;
