import json
from typing import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from AutoFetcher.DutCacher import DutCacher
from AutoFetcher.AsyncCacher.Consumer import AsyncConsumer
from AutoFetcher.AsyncCacher.Producer import AsyncProducer
from AutoFetcher.AllExceptions import AutoFetchException
from AutoFetcher.TopoFetcher.Parser import TopoParser
from AutoFetcher.TopoFetcher.Plotter import TopoPlotter
from AutoFetcher.TopoFetcher.Processor import *

import pyeapi
import pyeapi.eapilib


class DutGrabber:
    def __init__(self, dut_list: list[str], single_task: Callable[[str, 'DutGrabber'], str],
                 local_db: str = None, create_schema: bool = False):
        """

        :param dut_list: The list of DUTs from DutFetcher or custom list.
        :param single_task: The user defined task in form of method to filter affected DUTs. A callable that processes
            a single device. The callable should accept the device name (str) and the DutGrabber instance, which
            provides methods to interact with the device.
        :param local_db: The sqlite database path as string from local machine (default it's None)
        :param create_schema: Boolean param that command the program whether to create schema automatically or not.
            (default it's False)
        """
        self.dutList = dut_list
        self.singleTaskHandler = single_task
        self.local_db = local_db
        self.create_schema = create_schema
        self.__host = None
        self.__queue_name = None
        self.__caching = False
        self.__consumer: AsyncConsumer = None
        self.__username: str = 'admin'
        self.__password: str = ''
        self.__result: list = None
        self.__patch_pyeapi_ciphers()

    def __patch_pyeapi_ciphers(self):
        try:
            import pyeapi.eapilib
        except ImportError:
            return
        connect_orig = pyeapi.eapilib.HttpsConnection.connect

        def connect(self):
            self._context.set_ciphers('DEFAULT@SECLEVEL=2')
            return connect_orig(self)

        pyeapi.eapilib.HttpsConnection.connect = connect

    def __fetch_dut(self, some_free_dut: str):
        result = self.singleTaskHandler(some_free_dut, self)
        return {
            "reason": result,
            "dut": some_free_dut
        }

    def enable_caching(self, host: str, queue_name: str, caching: bool = True):
        self.__caching = caching
        self.__host = host
        self.__queue_name = queue_name
        if self.__caching:
            # Just for cleaning the database for the first time
            # when user enable the caching
            DutCacher(self.local_db, clean_up=True)

    def set_authentication(self, username: str, password: str):
        self.__username = username
        self.__password = password

    def find_topology(self, file_path: str, result: list = None):
        topo_parser = TopoParser(file_path)
        local_result = None
        if result is None:
            local_result = self.__result
        else:
            local_result = result

        for result in local_result:
            if isinstance(result.get("reason"), dict):
                topo_parser.parse_api_json(result.get("reason"))
                topo_parser.make_graph(result.get("dut"))

        g1 = topo_parser.get_graph()
        topo_parser.reset_graph()

        topo_parser.parse_yaml(file_path)
        topo_parser.make_graph()
        g2 = topo_parser.get_graph()

        return {
            "similarity_score": compare_graphs(g1, g2),
            "isomorphic_sub_graph": find_isomorphic_sub_graphs(g1, g2)
        }

    def execute_to_dut(self, device: str, commands=None):
        if commands is None:
            commands = ["show version detail"]
        try:
            results = []
            commands_not_cached = []
            final_results = []
            if not self.__caching:
                conn_to_dut = pyeapi.connect(host=f"{device}", username=self.__username, password=self.__password)
                results = conn_to_dut.execute(commands)
                final_results = results.get("result")
            else:
                # clean_up is set to false because we don't want to run delete query from each thread
                local_dut_cacher = DutCacher(self.local_db, clean_up=False)
                for command in commands:
                    cache = local_dut_cacher.get_cache(device, command)
                    if cache is not None:
                        results.append(json.loads(cache))
                    else:
                        commands_not_cached.append(command)
                        results.append("Fill")
                conn_to_dut = pyeapi.connect(host=f"{device}", username=self.__username, password=self.__password)
                not_cached_results = conn_to_dut.execute(commands_not_cached)
                last_fill = 0
                for result in results:
                    if result == "Fill":
                        if last_fill < len(not_cached_results):
                            AsyncProducer.create_and_publish(self.__host, self.__queue_name, {
                                "Device": device,
                                "Command": commands_not_cached[last_fill],
                                "Output": not_cached_results["result"][last_fill]
                            })
                            final_results.append(not_cached_results["result"][last_fill])
                            last_fill += 1
                    else:
                        final_results.append(result)
            return final_results
        except Exception as e:
            print(f"Error of type {type(e)} while executing commands {commands} to DUT {device}: {e}")
            raise AutoFetchException(f"[AUTO-FETCH] Exception of type {type(e)} : {e}")

    def fast_fetch_dut_with(self, all_free_dut: list[str], max_threads: int = 10):
        """
        This function can be used by users to execute multithreaded
        program that filters the DUT according to the callable
        **`self.singleTaskHandler`**

        Later, user can filter the results on their own.

        :param all_free_dut: The list of DUTs
        :param max_threads: The max threads that user might want. Default is `10`.
        :return: The mixed results. A list of results got from all threads.
        """
        result_collector = []
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            tasks = {executor.submit(self.__fetch_dut, dut_name): dut_name for dut_name in all_free_dut}
            for task in as_completed(tasks):
                result = task.result()
                if result:
                    result_collector.append(result)
        self.__result = result_collector
        return result_collector

    def fast_fetch_dut(self, max_threads: int = 10):
        """
        This function can be used by users to execute multithreaded
        program that filters the DUT according to the callable
        **`self.singleTaskHandler`**

        Later, user can filter the results on their own.

        :param max_threads: The max threads that user might want. Default is `10`.
        :return: The mixed results. A list of results got from all threads.
        """
        return self.fast_fetch_dut_with(self.dutList, max_threads)

    def fast_fetch_result_with(self, all_free_dut: list[str], max_threads: int = 10):
        """
        This function can be used by users to execute multithreaded
        program that filters the DUT according to the callable
        **`self.singleTaskHandler`** and you can pass the list of
        DUTs if you want.

        It is assumed that the callable **`self.singleTaskHandler`**
        returns the result of form string.

        :param all_free_dut: The list of DUTs
        :param max_threads: The max threads that user might want. Default is `10`.
        :return: The combined result.
        """
        mixed_results = self.fast_fetch_dut_with(all_free_dut, max_threads)
        return self.combine_results(mixed_results)

    def fast_fetch_result(self, max_threads: int = 10):
        """
        This function can be used by users to execute multithreaded
        program that filters the DUT according to the callable
        **`self.singleTaskHandler`.**

        It is assumed that the callable **`self.singleTaskHandler`**
        returns the result of form string.

        :param max_threads: The max threads that user might want. Default is `10`.
        :return: The combined result.
        """
        mixed_results = self.fast_fetch_dut_with(self.dutList, max_threads)
        return self.combine_results(mixed_results)

    @staticmethod
    def combine_results(mixed_results: list[{}]):
        """
        This function can be used by users to combine the mixed results
        of form `{'reason': <value>, 'dut': <value>}`
        that they might have received from the individual threads.

        :param mixed_results: The list of mixed results from each thread
        :return: The dictionary containing combined result
        """
        merged_result = defaultdict(list)
        for dut_info in mixed_results:
            merged_result[str(dut_info['reason'])].append(dut_info['dut'])
        return dict(merged_result)
