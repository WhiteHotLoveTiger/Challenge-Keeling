xml_samples = {
    "valid": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "valid empty cost": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost></cost>
            </node>
        </edges>
        </graph>
        """,
    "valid no cost": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
            </node>
        </edges>
        </graph>
        """,
    "valid neg cost": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>-1.0</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid root tag name": """
        <g>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </g>
        """,
    "invalid graph id": """
        <graph>
        <id></id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid graph name": """
        <graph>
        <id>g0</id>
        <name></name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid no nodes": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes></nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid edges name": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <e>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </e>
        </graph>
        """,
    "invalid dup node id": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
            <node>
                <id>a</id>
                <name>Another name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid multi from": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
                <from>a</from>
            </node>
        </edges>
        </graph>
        """,
    "invalid multi to": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
                <to>a</to>
            </node>
        </edges>
        </graph>
        """,
    "invalid empty string": "",
    "invalid dup graph id": """
        <graph>
        <id>g0</id>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid dup graph name": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid dup nodes": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        <nodes></nodes>
        </graph>
        """,
    "invalid dup node id elem": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid empty node id elem": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id></id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid dup node name": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid empty node name": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name></name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid dup edges": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        <edges></edges>
        </graph>
        """,
    "invalid dup edge id": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid dup edge from": """
    <graph>
    <id>g0</id>
    <name>Name</name>
    <nodes>
        <node>
            <id>a</id>
            <name>A name</name>
        </node>
    </nodes>
    <edges>
        <node>
            <id>e1</id>
            <from>a</from>
            <from>a</from>
            <to>a</to>
            <cost>42</cost>
        </node>
    </edges>
    </graph>
    """,
    "invalid dup edge to": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid dup edge cost": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid empty edge id": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id></id>
                <from>a</from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid empty from": """
        <graph>
        <id>g0</id>
        <name>Name</name>
        <nodes>
            <node>
                <id>a</id>
                <name>A name</name>
            </node>
        </nodes>
        <edges>
            <node>
                <id>e1</id>
                <from></from>
                <to>a</to>
                <cost>42</cost>
            </node>
        </edges>
        </graph>
        """,
    "invalid empty to": """
    <graph>
    <id>g0</id>
    <name>Name</name>
    <nodes>
        <node>
            <id>a</id>
            <name>A name</name>
        </node>
    </nodes>
    <edges>
        <node>
            <id>e1</id>
            <from>a</from>
            <to></to>
            <cost>42</cost>
        </node>
    </edges>
    </graph>
    """,
}

json_samples = {
    "valid json": '{"some": "json"}',
    "incomplete": '{"some": "json"',
}
