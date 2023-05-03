from spinedb_api import DatabaseMapping, from_database

def erase_bids_class():
    # todo finish this if bids are being erased then the awarded capapcity of CM should also be saved.
    url = r"sqlite:///C:\toolbox-amiris-emlab\.spinetoolbox\items\emlabdb\EmlabDB.sqlite"
    db_map = DatabaseMapping(url)
    try:
        subquery = db_map.object_parameter_value_sq
        statuses = {row.object_id: from_database(row.value, row.type) for row in db_map.query(subquery).filter(subquery.c.parameter_name == "Id")}
        removable_object_ids = {object_id for object_id, status in statuses.items() if status == "new"}
        db_map.cascade_remove_items(object=removable_object_ids)
        print("removed awaiting bids")
        print(removable_object_ids)
        db_map.commit_session("Removed unacceptable objects.")
    finally:
        db_map.connection.close()

#erase_bids_class()
def erase_new_ungrouped_plants():
    url = r"sqlite:///C:\toolbox-amiris-emlab\.spinetoolbox\items\emlabdb\EmlabDB.sqlite"
    db_map = DatabaseMapping(url)
    print("here")
    try:
        subquery = db_map.object_parameter_value_sq
        id_plants = {row.object_id: from_database(row.value, row.type) for row in db_map.query(subquery).filter(subquery.c.parameter_name == "Id")}
        removable_object_ids = {object_id for object_id, id_plant in id_plants.items() if id_plant == "delete"}

        db_map.cascade_remove_items(object=removable_object_ids)
        print("removed plants")
        print(removable_object_ids)
        db_map.commit_session("Removed unacceptable objects.")
    finally:
        db_map.connection.close()

erase_new_ungrouped_plants()