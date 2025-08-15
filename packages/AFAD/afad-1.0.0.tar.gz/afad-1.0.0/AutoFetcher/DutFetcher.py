from fabric import Connection
import re


class DutFetcher:
    # This can be used to define Regular Expressions
    regularExpressions = {
        "DUT_RE": r"[a-zA-Z]+\d+"
    }

    def __init__(self, tac_server: str, tac_host: str, tac_password: str):
        """

        :param tac_server: The server which has Art Tool.
        :param tac_host: The arista username / hostname which will be authenticated to tac_server.
        :param tac_password: The password for tac_host for authentication.
        """
        self.__tacPassword = tac_password  # Stores the password for auth. of the tac_host
        self.__connection = None  # Store the connection to the tac_server
        self.tacServer = tac_server  # Stores the ip/name of the tac_server
        self.tacHost = tac_host  # Stores the name of the host/user for tac_server
        self.dutList = []  # Stores the list of DUTs processed from the output of last command!
        self.result = "NONE"  # Stores the unprocessed output of last command!
        self.allValidPools = []  # Stores the list of all valid pools
        # self.__find_all_valid_pools()

    def __connect_to_server(self):
        try:
            self.__connection = Connection(host=self.tacServer, user=self.tacHost,
                                           connect_kwargs={"password": f"{self.__tacPassword}"})
        except Exception as e:
            print(f"Error while connecting to Art server : {e}")

    def __fetch_command_output(self, command: str = "Art list --domain=all | greap free"):
        result = None
        try:
            if self.__connection is None:
                self.__connect_to_server()
            result = self.__connection.run(f"{command}", hide=True, warn=True)
        except Exception as e:
            print(f"Error while collecting info from tac server: '{e}' while running command '{command}'")
        finally:
            if result is not None:
                return result.stdout
            else:
                return None

    def __find_all_valid_pools(self, command: str = "Art list --showpools"):
        self.result = self.__fetch_command_output(command)
        self.allValidPools = [pool_name for column_of_pools in self.result.splitlines()[2:] for pool_name in
                              column_of_pools.split()]

    def fetch_all_valid_pools(self, command: str = "Art list --showpools"):
        """
        This method can be used by users to run the command and fetch the
        list of all valid pools.

        :param command: The command that you want to run on Art server.
        :return: Returns the processed output (List of valid pools) from the command's output
        """
        self.__find_all_valid_pools(command)
        return self.allValidPools

    def fetch_duts(self, command: str = "Art list --domain=all | grep free"):
        """
        This method can be used by user to run the command and fetch the
        first column which usually holds the name of the DUT.

        :param command: The command that you want to run on Art server.
        :return: Returns the processed output (List of DUTs) from the command's output
        """
        self.result = self.__fetch_command_output(command)

        # This step is required because, command with "grep" won't have header in output...
        regex_command_containing_grep = r"grep"
        if re.search(regex_command_containing_grep, command):
            self.dutList = [
                line.split()[0]
                for line in self.result.strip().splitlines()
                if line.split()
            ]
        else:
            self.dutList = [
                line.split()[0]
                for line in (self.result or "").strip().splitlines()[3:]
                if line.split()
            ]

        # This step is required to filter extra rows for too long output from 'grab comment'
        self.dutList = [dut_name for dut_name in self.dutList if re.fullmatch(self.regularExpressions["DUT_RE"], dut_name)]
        return self.dutList

    def fetch_result(self, command: str = "Art list --domain=all | grep free"):
        """
        This method can be used by user to run the command and fetch the output directly!

        :param command: The command that you want to run on Art server.
        :return: Returns the actual/unprocessed output of the command
        """
        self.result = self.__fetch_command_output(command)
        return self.result

    def get_dut_list(self):
        return self.dutList

    def get_result(self):
        return self.result
