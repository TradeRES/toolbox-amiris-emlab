"""
Module defines a wrapper class for Spine DB API for easy adding of data

File provided through Spine Demo by VTT, with additions made by Jim Hommes.
29-6-2021
"""
import logging

from sqlalchemy.exc import ArgumentError as SQLAlchemyArgumentError
from spinedb_api import DatabaseMapping, DiffDatabaseMapping
from spinedb_api.exception import (
    SpineDBAPIError, SpineDBVersionError
)
from spinedb_api import import_functions
from spinedb_api import export_functions
from spinedb_api.helpers import create_new_spine_database
from spinedb_api.parameter_value import from_database


def _handle_errors(errors: list):
    """
    Log all thrown errors provided to this function as they occur.
    :param errors:
    :return:
    """
    for e in errors:
        logging.warning(e)


class SpineDB(object):
    """
    Class for working with a Spine database, especially when adding data
    """

    def __init__(self, url: str, mode='r', create=False):
        """
        Open Spine database at url for modifying

        Raises:
            RuntimeError: Could not open database
        """
        if mode == 'r' and not create:
            self._open_db_reading(url)
        elif mode == 'w' and not create:
            self._open_db_writing(url)
        elif create:
            self._create_db(url)

    def _open_db_reading(self, url: str):
        """
        Open Spine DB at url for reading
        """
        try:
            self._db_map = DatabaseMapping(url)
        except SpineDBVersionError:
            logging.error(f"Wrong Spine DB version in {url}")
            raise RuntimeError
        except SpineDBAPIError:
            logging.error(f"Could not open db at {url} for reading")
            raise RuntimeError

    def _open_db_writing(self, url: str):
        """
        Open Spine DB at url
        """
        try:
            self._db_map = DiffDatabaseMapping(url)
        except SpineDBVersionError:
            logging.error(f"Wrong Spine DB version in {url}")
            raise RuntimeError
        except SpineDBAPIError:
            logging.error(f"Could not open db at {url} for writing")
            raise RuntimeError

    def _create_db(self, url: str):
        """
        Create Spine DB at url
        """
        logging.info(f"Creating a new Spine DB at '{url}'")
        try:
            create_new_spine_database(url)
        except SQLAlchemyArgumentError as e:
            raise RuntimeError(e)
        except SpineDBAPIError as e:
            raise RuntimeError(e)
        else:
            self._open_db_writing(url)

    def import_object_classes(self, class_name) -> int:
        """
        Add object classes from a list of class name and description tuples
        Example::

            class_name = ['new_object_class', ('another_object_class', 'description', 123456)]
            import_object_classes(class_name)

        Returns:
            n_imported (int): Number of improrted entities
        """
        n_imported, errors = import_functions.import_object_classes(
            self._db_map, class_name)
        if errors:
            _handle_errors(errors)
        return n_imported

    def import_objects(self, objects) -> int:
        """
        Add objects of specific class from a list of class name and object name tuples

        Returns:
            n_imported (int): Number of improrted entities
        """
        n_imported, errors = import_functions.import_objects(
            self._db_map, objects)
        if errors:
            _handle_errors(errors)
        return n_imported

    def import_object_parameter_values(self, object_parameter_values) -> int:
        """
        Import object parameter values from a list of object class name, object name, parameter name and value tuples
        Example::

            object_parameter_values = [('object_class_name', 'object_name', 'parameter_name', 123.4),
                    ('object_class_name', 'object_name', 'parameter_name2',
                        '{"type":"time_series", "data": [1,2,3]}')}
                    ('object_class_name', 'object_name', 'parameter_name',
                        '{"type":"time_series", "data": [1,2,3]}'}, 'alternative')]
            import_object_parameter_values(db_map, data)

        Args:
        object_parameter_values (List[List/Tuple]): list/set/iterable of lists/tuples with
            object_class_name, object name, parameter name, (deserialized) parameter value,
            optional name of an alternative
        Returns:
            n_imported (int): Number of improrted entities
        """
        n_imported, errors = import_functions.import_object_parameter_values(
            self._db_map, object_parameter_values
        )
        if errors:
            _handle_errors(errors)
        return n_imported

    def import_object_groups(self, object_groups) -> int:
        """
        Add objects of specific class from a list of class name and object name tuples

        Returns:
            n_imported (int): Number of improrted entities
        """
        n_imported_members, errors = import_functions.import_object_groups(
            self._db_map, object_groups)
        if errors:
            _handle_errors(errors)
        return n_imported_members

    def import_relationship_classes(self, class_description) -> int:
        """
        Imports relationship classes.

         Example::

            class_description = [
                ('new_rel_class', ['object_class_1', 'object_class_2']),
                ('another_rel_class', ['object_class_3', 'object_class_4'], 'description'),
            ]
            import_relationship_classes(class_description)

        Returns:
            n_imported (int): Number of improrted entities
        """
        n_imported, errors = import_functions.import_relationship_classes(
            self._db_map, class_description
        )
        if errors:
            _handle_errors(errors)
        return n_imported

    def import_relationships(self, relationships) -> int:
        """
        Import relationships from a list of relationship name and object name list tuples

        Example::

        relationships = [('relationship_class_name', ('object_name1', 'object_name2'))]
        import_relationships(relationships)

        Returns:
            n_imported (int): Number of improrted entities
        """
        n_imported, errors = import_functions.import_relationships(
            self._db_map, relationships
        )
        if errors:
            _handle_errors(errors)
        return n_imported

    def import_relationship_parameter_values(self, relationship_parameter_values) -> int:
        """
        Import relationship parameter values from a list of relationship name,
        object name list, parameter name and value tuples

        Returns:
            n_imported (int): Number of improrted entities
        """
        n_imported, errors = import_functions.import_relationship_parameter_values(
            self._db_map, relationship_parameter_values
        )
        if errors:
            _handle_errors(errors)
        return n_imported

    def import_alternatives(self, data) -> int:
        """
        Imports alternatives.

        Example:

            data = ['new_alternative', ('another_alternative', 'description')]

        Args:
            data (Iterable): an iterable of alternative names,
                or of lists/tuples with alternative names and optional descriptions

        Returns:
            tuple of int and list: Number of successfully inserted alternatives, list of errors
        """
        n_imported, errors = import_functions.import_alternatives(self._db_map, data)
        if errors:
            _handle_errors(errors)
        return n_imported

    def import_data(self, data) -> int:
        """
        Import data

        Args:
            data (dict): Dictionary mapping entity types to definitions

        Returns:
            n_imported (int): Number of improrted entities
        """
        n_imported, errors = import_functions.import_data(self._db_map, **data)
        if errors:
            _handle_errors(errors)
        return n_imported

    def export_data(self) -> dict:
        """
        This function exports all data from the SpineDB. Should be used with consequent use of import_ functions.

        :return: Dict with all data.
        """
        try:
            _data_dict = export_functions.export_data(self._db_map)
            return _data_dict
        except Exception as e:
            _handle_errors([e])
            logging.warning(e)

    def commit(self, message):
        """
        Commit current changes
        """
        try:
            self._db_map.commit_session(message)
        except SpineDBAPIError as e:
            logging.warning(e)

    """
    Additions from this point made by Jim Hommes.
    """

    def close_connection(self):
        """
        Close the connection to the SpineDB. Necessary use through Spine as when an exception is thrown, Spine does not
        automatically close the connection.
        """
        self._db_map.connection.close()

    def query_object_parameter_values_by_object_class(self, object_class_name):
        """
        When not all data is required, this function can be used to query all parameter values for a certain
        object class.

        :param object_class_name: Name of the object class.
        :return: Dict with object_class_name, object_name, parameter_name, parameter_value and alternative
        """
        subquery = self._db_map.object_parameter_value_sq
        return [{'object_class_name': value_row.object_class_name,
                 'object_name': value_row.object_name,
                 'parameter_name': value_row.parameter_name,
                 'parameter_value': from_database(value_row.value, value_row.type),
                 'alternative': value_row.alternative_name}
                for value_row
                in self._db_map.query(subquery).filter(subquery.c.object_class_name == object_class_name).all()]

    def query_object_parameter_values_by_object_classes(self, object_class_name_list):
        """
        Practically same function as query_object_parameter_values_by_object_class but multiple object classes
        can be specified.

        :param object_class_name_list: List of object class names.
        :return: Dict with object_class_name, object_name, parameter_name, parameter_value and alternative
        """
        subquery = self._db_map.object_parameter_value_sq
        return [{'object_class_name': value_row.object_class_name,
                 'object_name': value_row.object_name,
                 'parameter_name': value_row.parameter_name,
                 'parameter_value': value_row.value,
                 'alternative': value_row.alternative_name}
                for value_row
                in self._db_map.query(subquery).filter(subquery.c.object_class_name.in_(object_class_name_list)).all()]

    def query_object_parameter_values_by_object_class_and_object_name(self, object_class_name, object_name):
        """
        When not all data is required, this function can be used to query all parameter values for a certain
        object class and object name. Handy for objects with only one value.

        :param object_class_name: Name of the object class.
        :param object_name: Name of the object.
        :return: Dict with object_class_name, object_name, parameter_name, parameter_value and alternative
        """
        subquery = self._db_map.object_parameter_value_sq
        return [{'object_class_name': value_row.object_class_name,
                 'object_name': value_row.object_name,
                 'parameter_name': value_row.parameter_name,
                 'parameter_value': from_database(value_row.value, value_row.type),
                 'alternative': value_row.alternative_name}
                for value_row
                in self._db_map.query(subquery).filter(subquery.c.object_class_name == object_class_name).filter(subquery.c.object_name == object_name).all()]
