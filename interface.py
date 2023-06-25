from neo4j import GraphDatabase

class Interface:
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), encrypted=False)
        self._driver.verify_connectivity()

    def close(self):
        self._driver.close()

    def bfs(self, start_node, last_node):
        self.create_graph_if_not_exists()
        with self._driver.session() as session:
            # Retrieve the start node ID
            result = session.run(
                "MATCH (start) WHERE start.name = toString($start_node_name) RETURN id(start) AS start_node_id",
                start_node_name=start_node
            ).single()
            start_node_id = result["start_node_id"] if result else None

            # Retrieve the end node ID
            result = session.run(
                "MATCH (end) WHERE end.name = toString($end_node_name) RETURN id(end) AS end_node_id",
                end_node_name=last_node
            ).single()
            end_node_id = result["end_node_id"] if result else None

            # Execute BFS with the retrieved start and end node IDs
            if start_node_id is not None and end_node_id is not None:
                result = session.run(
                    """
                    CALL gds.bfs.stream($graph_name, {
                      sourceNode: $start_node_id,
                      targetNodes: [$end_node_id],
                      relationshipTypes: ['TRIP']
                    })
                    YIELD nodeIds, path
                    RETURN [node in nodes(path) | {name: node.name}] as path
                    """,
                    graph_name="taxi-dataset-graph",
                    start_node_id=start_node_id,
                    end_node_id=end_node_id
                ).single()
                
                res = [None]
                res[0] = result
                for node in res[0]['path']:
                    node['name'] = int(node['name'])
                return res


    def pagerank(self, max_iterations, weight_property):
        self.create_graph_if_not_exists()
        with self._driver.session() as session:
            result = session.run(
                """
                CALL gds.pageRank.stream($graph_name, {
                  nodeLabels: ['Location'],
                  relationshipTypes: ['TRIP'],
                  relationshipWeightProperty: $weight_property,
                  maxIterations: $max_iterations,
                  dampingFactor: 0.85
                })
                YIELD nodeId, score
                RETURN gds.util.asNode(nodeId).name AS name, score
                ORDER BY score DESC
                """
                ,graph_name="taxi-dataset-graph", max_iterations=max_iterations, weight_property=weight_property)

            max_pr = result.peek()
            last_record = None
            for record in result:
                last_record = record
            res = [None, None]
            res[0] = dict(max_pr)
            res[0]['name'] = int(res[0]['name'])
            res[1] = dict(last_record)
            res[1]['name'] = int(res[1]['name'])
            return res
            

    def create_graph_if_not_exists(self):
        with self._driver.session() as session:
            result = session.run(
                """
                CALL gds.graph.exists($graph_name)
                  YIELD graphName, exists
                RETURN exists
                """
                ,graph_name="taxi-dataset-graph")
            exists = result.single()[0]
            if not exists:
                query2 = """
                CALL gds.graph.project(
                  'taxi-dataset-graph',
                  'Location',
                  'TRIP',
                  {
                    relationshipProperties: ['distance', 'fare', 'pickup_dt', 'dropoff_dt']
                  }
                )
                """
                session.run(query2)
