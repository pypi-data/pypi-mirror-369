import os
import warnings
import xml.etree.ElementTree as et
from typing import Optional

from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.scenario.lanelet import LaneletNetwork

from commonroad_sumo.interface.util import NetError
from commonroad_sumo.sumo_config import DefaultConfig


class ScenarioWrapper:
    def __init__(self):
        self.scenario_name: str = ""
        self.net_file: str = ""
        self.cr_map_file: str = ""
        self.sumo_cfg_file = None
        self.ego_start_time: int = 0
        self.sumo_net = None
        self._lanelet_network: LaneletNetwork = None
        self._initial_scenario = None
        self.planning_problem_set = None
        self._route_planner = None

    def initialize(
        self,
        scenario_name: str,
        sumo_cfg_file: str,
        cr_map_file: str,
        ego_start_time: int = None,
    ) -> None:
        """
        Initializes the ScenarioWrapper.

        :param scenario_name: the name of the scenario
        :param sumo_cfg_file: the .sumocfg file
        :param cr_map_file: the commonroad map file
        :param ego_start_time: the start time of the ego vehicle

        """
        self.scenario_name = scenario_name
        self.sumo_cfg_file = sumo_cfg_file
        self.net_file = self._get_net_file(self.sumo_cfg_file)
        self.cr_map_file = cr_map_file
        self.ego_start_time = ego_start_time
        self.initial_scenario, self.planning_problem_set = CommonRoadFileReader(
            self.cr_map_file
        ).open()
        if len(self.planning_problem_set.planning_problem_dict) == 0:
            self.planning_problem_set = None

    @classmethod
    def init_from_scenario(
        cls,
        config: DefaultConfig,
        scenario_path: str,
        ego_start_time: Optional[int] = None,
        cr_map_file=None,
    ) -> "ScenarioWrapper":
        """
        Initializes the ScenarioWrapper according to the given scenario_name/ego_start_time and returns the ScenarioWrapper.
        :param config: config file for the initialization, contain scenario_name.
        :param scenario_path: path to the scenario folder
        :param ego_start_time: the start time of the ego vehicle.
        :param cr_map_file: path to commonroad map, if not in scenario folder

        """
        assert isinstance(
            config, DefaultConfig
        ), f"Expected type DefaultConfig, got {type(config)}"

        obj = cls()
        scenario_path = (
            config.scenarios_path
            if config.scenarios_path is not None
            else scenario_path
        )
        sumo_cfg_file = os.path.join(scenario_path, config.scenario_name + ".sumo.cfg")
        if cr_map_file is None:
            cr_map_file = os.path.join(scenario_path, config.scenario_name + ".cr.xml")

        obj.initialize(config.scenario_name, sumo_cfg_file, cr_map_file, ego_start_time)
        return obj

    def _get_net_file(self, sumo_cfg_file: str) -> str:
        """
        Gets the net file configured in the cfg file.

        :param sumo_cfg_file: SUMO config file (.sumocfg)

        :return: net-file specified in the config file
        """
        if not os.path.isfile(sumo_cfg_file):
            raise ValueError(
                "File not found: {}. Maybe scenario name is incorrect.".format(
                    sumo_cfg_file
                )
            )
        tree = et.parse(sumo_cfg_file)
        file_directory = os.path.dirname(sumo_cfg_file)
        # find net-file
        all_net_files = tree.findall("*/net-file")
        if len(all_net_files) != 1:
            raise NetError(len(all_net_files))
        return os.path.join(file_directory, all_net_files[0].attrib["value"])

    def get_rou_file(self) -> str:
        """
        Gets the net file configured in the cfg file.

        :param sumo_cfg_file: SUMO config file (.sumocfg)

        :return: net-file specified in the config file
        """
        if not os.path.isfile(self.sumo_cfg_file):
            raise ValueError(
                "File not found: {}. Maybe scenario name is incorrect.".format(
                    self.sumo_cfg_file
                )
            )
        tree = et.parse(self.sumo_cfg_file).find("input")
        file_directory = os.path.dirname(self.sumo_cfg_file)
        # find net-file
        rou_files = tree.find("route-files").get("value").split(",")
        if len(rou_files) > 1:  # filtering for vehicles route file
            for r in rou_files:
                if "vehicle" in r:
                    rou_file = r
        else:
            rou_file = rou_files[0]

        rou_path = os.path.join(file_directory, rou_file)
        if not os.path.isfile(rou_path):
            return None

        # correction for duplicate edge id bug -- issue#14
        # print("applying duplicate edge correction")
        tree_routes_orig = et.parse(rou_path)
        tree_routes = tree_routes_orig.getroot()
        file_did_change = False
        for vehicle in tree_routes.findall("vehicle"):
            edges = list(map(str, vehicle.find("route").get("edges").split(" ")))
            edges_corr = []
            route_did_change = False

            for ind in range(len(edges) - 1):
                if edges[ind + 1] != edges[ind]:
                    edges_corr.append(edges[ind])
                else:
                    route_did_change = True
                    file_did_change = True
            edges_corr.append(edges[-1])

            if route_did_change:  # overwrite file
                edges_str = " ".join(map(str, edges_corr))
                vehicle.find("route").set("edges", edges_str)

        if file_did_change:
            warnings.warn("Route file had to be corrected and is overwritten.")
            tree_routes_orig.write(rou_path)

        return rou_path  # original or corrected one
