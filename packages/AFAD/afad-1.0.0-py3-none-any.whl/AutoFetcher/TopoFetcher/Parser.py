import json
import yaml
import networkx as nx

from pathlib import Path


class TopoParser:
    def __init__(self, file_name: str, api_output: dict = None):
        self.__fileName = file_name
        self.__apiOutput = api_output
        self.__lastParsedIsYaml = False
        self.__graph_view = nx.Graph()
        self.__default_topology_output_file: str = 'topology-output.json'
        self.parsedData = None

    def get_graph(self):
        return self.__graph_view

    def reset_graph(self):
        self.__graph_view = nx.Graph()

    def parse_yaml(self, file_name: str = None):
        self.__lastParsedIsYaml = True
        if file_name is None:
            file = self.__fileName
        else:
            file = file_name
        with Path(file).open('r') as local_file:
            self.parsedData = yaml.safe_load(local_file)

    def parse_api_json(self, output: dict):
        self.__lastParsedIsYaml = False
        self.parsedData = output["lldpNeighbors"]

    def make_graph(self, device: str = "root"):
        if self.__lastParsedIsYaml:
            if "links" in self.parsedData.keys():
                for link_values in self.parsedData["links"]:
                    devices_int = link_values["connection"]
                    if len(devices_int) == 2:
                        devices = []
                        interfaces = []
                        for str_tuple in devices_int:
                            values = str_tuple.split(":")
                            devices.append(values[0])
                            interfaces.append(values[1])
                        self.__graph_view.add_edge(
                            devices[0], devices[1],
                            int_a=interfaces[0],
                            int_b=interfaces[1]
                        )
                    else:
                        print(f"[TOPO-FETCHER] Skipping malformed link : {link_values}")
            else:
                # Possibly older version/variant of YAML Format...
                for node_info in self.parsedData["nodes"]:
                    node_name = list(node_info.keys())[0]
                    node_neighbors = node_info[node_name].get("neighbors")
                    if node_neighbors is not None:
                        for neighbor in node_neighbors:
                            self.__graph_view.add_edge(
                                node_name, neighbor.get('neighborDevice'),
                                int_a=neighbor.get("port"),
                                int_b=neighbor.get("neighborPort")
                            )

        else:
            for neighbors in self.parsedData:
                self.__graph_view.add_edge(
                    device, neighbors["neighborDevice"],
                    int_a=neighbors["port"],
                    int_b=neighbors["neighborPort"]
                )

    def save_parsed(self, file_path: str):
        try:
            with Path(file_path).open('w') as file:
                file.write(json.dumps(self.parsedData))
        except IOError as e:
            print(f"[TOPO-FETCHER] Error while writing to file : {e}")
