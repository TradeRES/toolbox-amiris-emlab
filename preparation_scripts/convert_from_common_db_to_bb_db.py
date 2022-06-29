from enum import IntEnum, unique
import sys
from spinedb_api import DatabaseMapping, DiffDatabaseMapping, export_data, import_data


@unique
class P(IntEnum):
    CLASS = 0
    OBJECT = 1
    NAME = 2
    X = 3
    ALTERNATIVE = 4


in_url = sys.argv[1]
out_url = sys.argv[2]
in_db = DatabaseMapping(in_url)
out_db = DiffDatabaseMapping(out_url)

parameters_gnu = {"apparent_power": "unitSizeMVA", "capacity": "capacity", 
                  "capacity_value": "availabilityCapacityMargin", "conversion_coefficient": "conversionCoeff",
                  "fom_cost": "fomCosts", "inertia": "inertia",
                  "investment_cost": "invCosts", "ramp_limit": "maxRampDown",
                  "subunit_capacity": "unitSize", "vom_cost": "vomCosts"}
parameters_gnu2 = {"ramp_limit": "maxRampUp"}
source_relationship_class_gnu = "node__unit__io"
link_relationship_class_gnu = "commodity__node"
target_relationship_class_gnu = "grid__node__unit__io"

parameters_fn = {"capacity_factor": "capacityFactor"}
source_object_class_fn = "flow"
link_relationship_class_fn = "flow__unit"
link_relationship_class2_fn = "node__unit__io"
target_relationship_class_fn = "flow__node"

    
def add_relationship_dimension(source_relationship_class, link_relationship_class, target_relationship_class):
    subquery = in_db.wide_relationship_class_sq
    class_row = in_db.query(subquery).filter(subquery.c.name == link_relationship_class).first()
    subquery = in_db.wide_relationship_sq

    # Create a dictionary that links the new dimension to one of the old dimensions
    target_objects = {}
    for relationship_row in in_db.query(subquery).filter(subquery.c.class_id == class_row.id):
        target, source = relationship_row.object_name_list.split(",")
        target_objects[source] = target

    data = export_data(in_db)

    # Add the entities from the source class to a list
    x_to_move = []
    for value in data["relationships"]:
        if value[P.CLASS] == source_relationship_class:
            x_to_move.append(value[P.OBJECT])

    # Extend the dimensions of the entities and add to a list 
    moved_values = []
    for object1, object2, object3 in x_to_move:
        object_add = target_objects[object1]
        moved_values.append((target_relationship_class, (object_add, object1, object2, object3)))
        
    data.setdefault("relationships", []).extend(moved_values)
    import_data(out_db, **data)

def add_parameter_dimension(parameters, source_relationship_class, link_relationship_class, target_relationship_class):
    subquery = in_db.wide_relationship_class_sq
    class_row = in_db.query(subquery).filter(subquery.c.name == link_relationship_class).first()
    subquery = in_db.wide_relationship_sq

    # Create a dictionary that links the new dimension to one of the old dimensions
    target_objects = {}
    for relationship_row in in_db.query(subquery).filter(subquery.c.class_id == class_row.id):
        target, source = relationship_row.object_name_list.split(",")
        target_objects[source] = target

    data = export_data(in_db)

    # Add the parameter values from the source class to a list
    x_to_move = []
    for value in data["relationship_parameter_values"]:
        if value[P.CLASS] == source_relationship_class and value[P.NAME] in parameters:           
            x_to_move.append((value[P.OBJECT], parameters[value[P.NAME]], value[P.X], value[P.ALTERNATIVE]))

    # Add the previous parameter values to a list with the extended relationship dimensions
    moved_values = []
    for (object1, object2, object3), new_parameter, x, alternative in x_to_move:
        object_add = target_objects[object1]
        moved_values.append((target_relationship_class, (object_add, object1, object2, object3), new_parameter, x, alternative))

    data.setdefault("relationship_parameter_values", []).extend(moved_values)
    import_data(out_db, **data)
    
def add_dimension_2links(source_object_class, link_relationship_class, link_relationship_class2, target_relationship_class):
    subquery = in_db.wide_relationship_class_sq
    class_row = in_db.query(subquery).filter(subquery.c.name == link_relationship_class).first()
    subquery = in_db.wide_relationship_sq

    # Create a dictionary that links a temporary dimension to the old dimension
    target_objects_temp = {}
    for relationship_row in in_db.query(subquery).filter(subquery.c.class_id == class_row.id):
        target, source = relationship_row.object_name_list.split(",") #flow, unit
        target_objects_temp[source] = target #target_objects_temp[unit] = flow
        
    subquery = in_db.wide_relationship_class_sq
    class_row = in_db.query(subquery).filter(subquery.c.name == link_relationship_class2).first()
    subquery = in_db.wide_relationship_sq

    # Create a dictionary that links the new dimension to the old dimension
    target_objects = {}
    for relationship_row in in_db.query(subquery).filter(subquery.c.class_id == class_row.id):
        target, source, dummy = relationship_row.object_name_list.split(",") #node, unit
        if source in target_objects_temp:
            target_objects[target_objects_temp[source]] = target #target_objects[flow] = node

    data = export_data(in_db)

    # Add the entities from the source class to a list
    x_to_move = []
    for value in data["objects"]:
        if value[P.CLASS] == source_object_class:
            x_to_move.append(value[P.OBJECT])

    # Extend the dimensions of the entities and add to a list 
    moved_values = []
    for object1 in x_to_move:
        object_add = target_objects[object1]
        moved_values.append((target_relationship_class, (object1, object_add)))

    data.setdefault("relationships", []).extend(moved_values)
    import_data(out_db, **data)
    
def add_parameter_dimension_2links(parameters, source_object_class, link_relationship_class, link_relationship_class2, target_relationship_class):
    subquery = in_db.wide_relationship_class_sq
    class_row = in_db.query(subquery).filter(subquery.c.name == link_relationship_class).first()
    subquery = in_db.wide_relationship_sq

    # Create a dictionary that links a temporary dimension to the old dimension
    target_objects_temp = {}
    for relationship_row in in_db.query(subquery).filter(subquery.c.class_id == class_row.id):
        target, source = relationship_row.object_name_list.split(",") #flow, unit
        target_objects_temp[source] = target #target_objects_temp[unit] = flow
        
    subquery = in_db.wide_relationship_class_sq
    class_row = in_db.query(subquery).filter(subquery.c.name == link_relationship_class2).first()
    subquery = in_db.wide_relationship_sq

    # Create a dictionary that links the new dimension to the old dimension
    target_objects = {}
    for relationship_row in in_db.query(subquery).filter(subquery.c.class_id == class_row.id):
        target, source, dummy = relationship_row.object_name_list.split(",") #node, unit
        if source in target_objects_temp:
            target_objects[target_objects_temp[source]] = target #target_objects[flow] = node

    data = export_data(in_db)

    # Add the parameter values from the source class to a list
    x_to_move = []
    for value in data["object_parameter_values"]:
        if value[P.CLASS] == source_object_class and value[P.NAME] in parameters:           
            x_to_move.append((value[P.OBJECT], parameters[value[P.NAME]], value[P.X], value[P.ALTERNATIVE]))

    # Add the previous parameter values to a list with the extended relationship dimensions 
    moved_values = []
    for object1, new_parameter, x, alternative in x_to_move:
        object_add = target_objects[object1]
        moved_values.append((target_relationship_class, (object1, object_add), new_parameter, x, alternative))

    data.setdefault("relationship_parameter_values", []).extend(moved_values)
    import_data(out_db, **data)

def main():
    try:       
        #grid__node__unit__io relationships and parameters
        add_relationship_dimension(source_relationship_class_gnu, link_relationship_class_gnu, target_relationship_class_gnu)
        add_parameter_dimension(parameters_gnu, source_relationship_class_gnu, link_relationship_class_gnu, target_relationship_class_gnu)
        add_parameter_dimension(parameters_gnu2, source_relationship_class_gnu, link_relationship_class_gnu, target_relationship_class_gnu)
        
        #flow__node relationships and parameters
        add_dimension_2links(source_object_class_fn, link_relationship_class_fn, link_relationship_class2_fn, target_relationship_class_fn)
        add_parameter_dimension_2links(parameters_fn, source_object_class_fn, link_relationship_class_fn, link_relationship_class2_fn, target_relationship_class_fn)
        
        out_db.commit_session(f"Importing data from the common database.")
    finally:
        in_db.connection.close()
        out_db.connection.close()

main()