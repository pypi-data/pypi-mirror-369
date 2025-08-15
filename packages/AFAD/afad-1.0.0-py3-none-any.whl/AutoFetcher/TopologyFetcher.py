import json

from networkx import Graph

from AutoFetcher.DutFetcher import DutFetcher
from AutoFetcher.DutGrabber import DutGrabber
from AutoFetcher.TopoFetcher import *

from pathlib import Path

from concurrent.futures import ThreadPoolExecutor, as_completed


class TopologyFetcher:
    def __init__(self, tac_server: str, tac_host: str, tac_host_password: str, yaml_file_path: str = None):
        #  credentials for Art Server (Must be passed with const., modifiable)
        self.__tac_server = tac_server
        self.__tac_host = tac_host
        self.__tac_host_password = tac_host_password

        # credentials for DUTs (Default one, modifiable)
        self.__dut_user = "admin"
        self.__dut_user_password = ""

        # parameters for thread setup
        self.__max_parent_threads = 20
        self.__max_child_threads = 40

        # parameters for output management
        self.__default_output_path = ""
        self.__graph_capture = False

        # core requirements for TopologyFetcher
        self.yaml_file_path = yaml_file_path
        self.__all_valid_pools = []
        self.__dut_fetcher: DutFetcher = None
        self.__topo_parser: TopoParser = TopoParser(self.yaml_file_path)
        self.__yaml_graph = None
        self.__result = None

        # dut_grabber will be initiated per thread (not defining here)
        self.default_setup()
        self.yaml_file_path: Graph = None

    @staticmethod
    def __fetch_lldp_neighbors(device: str, grabber: DutGrabber):
        try:
            show_lldp_output = grabber.execute_to_dut(device, ["show lldp neighbors"])
            return show_lldp_output[0]
        except Exception as e:
            return f"[AUTO-FETCH] Exception while getting device neighbours : {e}"

    def __find_match_for(self, pool_name: str):
        # PHASE - 1 - Get the api response for designated command ======================================================
        # fetch all the devices in the pool (network call)
        all_duts_in_pool = self.__dut_fetcher.fetch_duts(f"Art list --domain=all --pool={pool_name}")
        # fetch "show lldp neighbors" command's output (creation of child processes, parallel network call)
        local_dut_grabber = DutGrabber(all_duts_in_pool, self.__fetch_lldp_neighbors)
        local_dut_grabber.set_authentication(self.__dut_user, self.__dut_user_password)
        result = local_dut_grabber.fast_fetch_dut(max_threads=self.__max_child_threads)

        # PHASE - 2 - Save the output from each DUTs for debugging =====================================================
        # save '<pool>-output.json' at self.__default_output_path
        try:
            with open(f'{self.__default_output_path}/{pool_name}-output.json', 'w') as file:
                file.write(json.dumps(result, indent=4))
        except IOError as e:
            print(f"Error while saving file for pool : {pool_name} : {e}")

        # PHASE - 3 - Save the .png file of entire pool's graph structure, if needed ===================================
        for sample in result:
            if isinstance(sample.get("reason"), dict):
                self.__topo_parser.parse_api_json(sample.get("reason"))
                self.__topo_parser.make_graph(sample.get("dut"))

        pool_graph = self.__topo_parser.get_graph()
        self.__topo_parser.reset_graph()

        if self.__graph_capture:
            topo_plotter = TopoPlotter(pool_graph)
            topo_plotter.set_graph(pool_graph)
            topo_plotter.plot_save_graph(f"{self.__default_output_path}/graph-{pool_name}.png")

        # PHASE - 4 - Return the response ==============================================================================
        return {
            "pool": pool_name,
            "similarity_score": compare_graphs(self.__yaml_graph, pool_graph),
            "isomorphic_sub_graph": find_isomorphic_sub_graphs(self.__yaml_graph, pool_graph)
        }

    def __save_final_result_with(self, final_result: dict):
        try:
            with open(f'{self.__default_output_path}/output.json', 'w') as file:
                file.write(json.dumps(final_result, indent=4))
        except IOError as e:
            print(f"Error while saving final output : {e}")

    def __save_final_result(self):
        self.__save_final_result_with(self.__result)

    def default_setup(self):
        self.__dut_fetcher = DutFetcher(
            tac_server=self.__tac_server,
            tac_host=self.__tac_host,
            tac_password=self.__tac_host_password
        )
        self.__all_valid_pools = self.__dut_fetcher.fetch_all_valid_pools()
        self.__topo_parser.parse_yaml()
        self.__topo_parser.make_graph()
        self.__yaml_graph = self.__topo_parser.get_graph()
        self.__topo_parser.reset_graph()

    def set_output_path(self, file_path: str):
        self.__default_output_path = file_path

    def set_credentials(self, tac_server: str, tac_host: str, tac_host_password: str):
        self.__tac_server = tac_server
        self.__tac_host = tac_host
        self.__tac_host_password = tac_host_password

    def set_dut_credentials(self, user: str, user_password: str):
        self.__dut_user = user
        self.__dut_user_password = user_password

    def set_thread_limit(self, max_parents: int, max_child: int):
        self.__max_parent_threads = max_parents
        self.__max_child_threads = max_child

    def change_yaml_file(self, new_yaml_file_path: str):
        self.yaml_file_path = new_yaml_file_path
        self.__topo_parser.parse_yaml(self.yaml_file_path)
        self.__topo_parser.make_graph()
        self.__yaml_graph = self.__topo_parser.get_graph()
        self.__topo_parser.reset_graph()

    def enable_graph_capture(self, enable: bool):
        self.__graph_capture = enable

    def fast_fetch_match_with(self, list_of_pools: list[str], max_parent_threads: int, max_child_threads: int):
        self.set_thread_limit(max_parents=max_parent_threads, max_child=max_child_threads)
        result_collector = []
        with ThreadPoolExecutor(max_workers=self.__max_parent_threads) as executor:
            all_task = {
                executor.submit(self.__find_match_for, pool_name): pool_name for pool_name in list_of_pools
            }
            for task in as_completed(all_task):
                result_of_task = task.result()
                if result_of_task:
                    result_collector.append(result_of_task)
        self.__result = result_collector
        print(self.__result)
        self.__save_final_result()
        return result_collector

    def fast_fetch_match(self):
        self.fast_fetch_match_with(self.__all_valid_pools, self.__max_parent_threads, self.__max_child_threads)
