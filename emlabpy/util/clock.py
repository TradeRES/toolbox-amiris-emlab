"""
This file contains all interactions with the system clock.
A tick is one year.
For the initialization. make current year the start year and the Simulation tick 0
for the increment clock, add a tick to SimulationTick and a year to current year

Ingrid modified 17-2-2022
Jim Hommes - 7-4-2021
"""
import sys
from util.spinedb import SpineDB
from util import globalNames
import csv
import os


def reset_candidate_investable_status():
    class_name = "CandidatePowerPlants"
    candidate_powerplants = [i for i in db.query_object_parameter_values_by_object_class(class_name)]
    for candidate in candidate_powerplants:
        db.import_object_parameter_values([(class_name, candidate["object_name"], "ViableInvestment", bool(1), "0")])


def update_years_file(current_year, lookAhead, final_year):
    fieldnames = ["current", "future", "final"]
    print("updated years file")
    # TODO dont hard code the path, once the spine bug is fixed. then it can be exported to the output folder.
    # the clock is executed in the util folder. So save the results in the parent folder: emlabpy
    complete_path = os.path.join(os.path.dirname(os.getcwd()), globalNames.years_path)
    with open(complete_path, "w") as csvfile:
        csvwriter = csv.writer(csvfile, delimiter="/")
        csvwriter.writerow([current_year, (current_year + lookAhead), final_year])


def main(clock_mode: str) -> int:
    class_name = "Configuration"
    object_name = "SimulationYears"
    object_parameter_value_name = "SimulationTick"

    look_ahead = next(
        int(i["parameter_value"])
        for i in db.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name)
        if i["parameter_name"] == "Look Ahead"
    )
    final_year = next(
        int(i["parameter_value"])
        for i in db.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name)
        if i["parameter_name"] == "End Year"
    )
    reset_candidate_investable_status()
    print("reset power plants status")
    if clock_mode == "initialize_clock":
        print("Initializing clock (tick 0)")
        db.import_object_classes([class_name])
        db.import_objects([(class_name, object_name)])
        db.import_data({"object_parameters": [[class_name, object_parameter_value_name]]})
        db.import_alternatives([str(0)])
        db.import_object_parameter_values([(class_name, object_name, object_parameter_value_name, 0, "0")])
        start_year = next(
            int(i["parameter_value"])
            for i in db.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name)
            if i["parameter_name"] == "Start Year"
        )
        db.import_object_parameter_values([(class_name, object_name, "CurrentYear", start_year, "0")])
        db.import_object_parameter_values([(class_name, object_name, object_parameter_value_name, 0, "0")])

        update_years_file(start_year, look_ahead, final_year)
        db.commit("Clock intialization")
        print("Done initializing clock (tick 0)")
    elif clock_mode == "increment_clock":
        step = next(
            int(i["parameter_value"])
            for i in db.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name)
            if i["parameter_name"] == "Time Step"
        )

        previous_tick = next(
            int(i["parameter_value"])
            for i in db.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name)
            if i["parameter_name"] == object_parameter_value_name
        )

        new_tick = step + previous_tick
        print("Incrementing Clock to " + str(new_tick))

        current_year = next(
            int(i["parameter_value"])
            for i in db.query_object_parameter_values_by_object_class_and_object_name(class_name, object_name)
            if i["parameter_name"] == "CurrentYear"
        )
        updated_year = step + current_year
        db.import_object_parameter_values([(class_name, object_name, object_parameter_value_name, new_tick, "0")])
        db.import_object_parameter_values([(class_name, object_name, "CurrentYear", updated_year, "0")])
        update_years_file(updated_year, look_ahead, final_year)
        db.commit("Clock increment")
        print("Done incrementing clock (tick +" + str(step) + "), resetting invest file and years file")
    else:
        print(f"Mode not implemented: {clock_mode}")
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Needs exactly two arguments: 'database_url' and 'mode'")
        sys.exit(1)

    db_url = sys.argv[1]
    print(f"Connecting to DB {db_url}")
    db = SpineDB(db_url)
    mode = sys.argv[2]

    try:
        exit_code = main(mode)
        if exit_code != 0:
            print(f"Clock.py failed with exit code: {exit_code}")
    finally:
        print("Closing DB Connections...")
        db.close_connection()
