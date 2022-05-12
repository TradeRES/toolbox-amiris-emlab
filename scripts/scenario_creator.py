from typing import Dict, List

from fameio.source.loader import load_yaml
from ruamel.yaml import YAML


class ScenarioCreator:
    """Class holding routines to create an AMIRIS scenario"""

    def __init__(self, scenario_file_path: str) -> None:
        self.load_scenario(scenario_file_path)

    def load_scenario(self, scenario_file_path: str) -> None:
        """Load a scenario skeleton from yaml"""
        self.scenario = load_yaml(scenario_file_path)

    def add_traderes_db_data(self, data: Dict) -> None:
        """Add common scenario data that can be extracted from TradeRES DB"""
        predefined_plant_builders = self.get_agents_by_type(
            "PredefinedPlantBuilder"
        )
        for plant_builder in predefined_plant_builders:
            prototype = plant_builder["Attributes"]["Prototype"]
            specific_emissions = self.get_specific_emissions_by_fuel(
                prototype["FuelType"]
            )
            prototype["SpecificCo2EmissionsInTperMWH"] = specific_emissions

            specific_emissions = self.get_specific_emissions_by_fuel(
                prototype["FuelType"]
            )
            prototype["SpecificCo2EmissionsInTperMWH"] = specific_emissions


    def get_agents_by_type(self, agent_type: str) -> List[Dict]:
        """Return list of agents of given type"""
        return [
            agent
            for agent in self.scenario["Agents"]
            if agent["Type"] == agent_type
        ]

    # TODO: Replace with (TradeRES) DB queries / extraction
    def get_specific_emissions_by_fuel(self, db: dict, fuel: str) -> float:
        """Return specific emissions for given fuel"""
        return db["specific_emissions"][fuel]
