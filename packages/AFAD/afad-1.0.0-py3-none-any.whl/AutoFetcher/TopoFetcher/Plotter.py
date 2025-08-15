import matplotlib.pyplot as plt
import networkx as nx


class TopoPlotter:
    def __init__(self, graph: nx.Graph):
        self.graph: nx.Graph = graph
        self.__default_topology_image_file = 'graph.png'

    def set_topology_image_file_path(self, path: str):
        self.__default_topology_image_file = path

    def get_graph(self):
        return self.graph

    def set_graph(self, graph: nx.Graph):
        self.graph = graph

    def plot_graph(self, show: bool = False):
        plt.clf()
        nx.draw(self.graph, with_labels=True)
        if show:
            plt.show()
        else:
            plt.savefig(self.__default_topology_image_file)

    def plot_show_graph(self):
        self.plot_graph(True)

    def plot_save_graph(self, filepath: str):
        self.__default_topology_image_file = filepath
        self.plot_graph()
