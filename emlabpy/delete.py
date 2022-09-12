from spinedb_api import DatabaseMapping, from_database

def erase_bids_class():
    # todo finish this if bids are being erased then the awarded capapcity of CM should also be saved.
    url = r"sqlite:///C:\Users\isanchezjimene\Documents\TraderesCode\toolbox-amiris-emlab\.spinetoolbox\items\emlabdb\EmlabDB.sqlite"
    db_map = DatabaseMapping(url)
    def class_id_for_name(name):
        return db_map.query(db_map.entity_class_sq).filter(db_map.entity_class_sq.c.name == name).first().id
    # try:
    #     id_to_remove = class_id_for_name("Bids")
    #     db_map.cascade_remove_items(**{"object_class": {id_to_remove}})
    #     db_map.commit_session("Removed ")
    # finally:
    #     db_map.connection.close()
    try:
        subquery = db_map.object_parameter_value_sq
        statuses = {row.object_id: from_database(row.value, row.type) for row in db_map.query(subquery).filter(subquery.c.parameter_name == "status")}
        removable_object_ids = {object_id for object_id, status in statuses.items() if status == "Awaiting"}
        db_map.cascade_remove_items(object=removable_object_ids)
        print("removed awaiting bids")
        db_map.commit_session("Removed unacceptable objects.")
    finally:
        db_map.connection.close()
erase_bids_class()