import json

from runregistry.attributes import (
    run_table_attributes,
    run_triplet_attributes,
    run_rr_attributes,
    run_oms_attributes,
    dataset_table_attributes,
    dataset_attributes,
    dataset_other_attributes,
    dataset_triplet_attributes,
)


def transform_to_rr_run_filter(run_filter):
    """
    Transforms a filter to a compatible filter that RR back end understands.
    :param run_filter: a filter that the user inputs into the api client
    :return: returns a filter that runregistry back end understands.
    """
    if run_filter == None:
        return {}
    transformed_filter = {}
    for key, value in run_filter.items():
        # If the value is not a dictionary (it is not in the form {'=': 323455}), so we assume the user just wanted simple '=', so we transform it from {'run_number': 323455} to {'run_number': {'=': 323455}}
        if not isinstance(value, dict):
            value = {"=": value}
        # If the user inputs a list of run_numbers in 'or' e.g.: {'run_number': {'or': [333333, 322222, 344444]}},
        # we want to translate it to {'run_number': {'or': [{'=':333333}, {'=':322222}, {'=':344444}]}}
        if isinstance(value, dict) and "or" in value and isinstance(value["or"], list):
            value["or"] = [
                {"=": x} if type(x) in (int, float, str) else x for x in value["or"]
            ]
        if key in run_table_attributes:
            transformed_filter[key] = value
        elif key in run_rr_attributes:
            transformed_filter["rr_attributes." + key] = value
        elif key in run_triplet_attributes:
            if "=" in value and type(value["="]) == str:
                # if it is a string, we know for sure its either GOOD, BAD, STANDBY, ETC...
                value = value["="].upper()
                if value not in (
                    "GOOD",
                    "BAD",
                    "STANDBY",
                    "EXCLUDED",
                    "NOTSET",
                    "EMPTY",
                ):
                    raise Exception(
                        "status must be either GOOD, BAD, STANDBY, EXCLUDED, NOTSET or EMPTY"
                    )
                transformed_filter["triplet_summary." + key + "." + value] = {">": 0}
            # If it is not a string, it must be a filter for comments, or causes:
            # TODO: DO THE FILTER FOR COMMENTS, AND STATUSES
        elif key in run_oms_attributes:
            transformed_filter["oms_attributes." + key] = value
        # If user is performing an arbitrary filter, do not interfere:
        elif (
            key.startswith("rr_attributes")
            or key.startswith("oms_attributes")
            or key.startswith("triplet_summary")
        ):
            transformed_filter[key] = value
        else:
            raise Exception(
                "filter attribute {} not found within the listed attributes in runregistry/attributes.py".format(
                    key
                )
            )
    return transformed_filter


def transform_to_rr_dataset_filter(dataset_filter):
    """
    Transforms a filter to a compatible filter that RR back end understands.
    :param dataset_filter: a filter that the user inputs into the api client
    :return: returns a filter that runregistry back end understands.
    """
    if dataset_filter == None:
        return {}
    transformed_filter = {}
    for key, value in dataset_filter.items():
        # If the value is not a dictionary (it is not in the form {'=': 323455}), so we assume the user just wanted simple '=', so we transform it from {'run_number': 323455} to {'run_number': {'=': 323455}}
        if not isinstance(value, dict) and key not in dataset_table_attributes:
            value = {"=": value}
        # If the user inputs a list of run_numbers in 'or' e.g.: {'run_number': {'or': [333333, 322222, 344444]}},
        # we want to translate it to {'run_number': {'or': [{'=':333333}, {'=':322222}, {'=':344444}]}}
        if isinstance(value, dict) and "or" in value and isinstance(value["or"], list):
            value["or"] = [
                {"=": x} if type(x) in (int, float, str) else x for x in value["or"]
            ]
        if key in dataset_table_attributes:
            if key == "dataset_name":
                # RR uses 'name' as identifier of dataset_name
                key = "name"
            transformed_filter[key] = value
        elif key in dataset_attributes:
            transformed_filter["dataset_attributes." + key] = value
        elif key in dataset_triplet_attributes:
            if type(value["="]) == str:
                # if it is a string, we know for sure its either GOOD, BAD, STANDBY, ETC...
                value = value["="].upper()
            if value not in ("GOOD", "BAD", "STANDBY", "EXCLUDED", "NOTSET", "EMPTY"):
                raise Exception(
                    "status must be either GOOD, BAD, STANDBY, EXCLUDED, NOTSET or EMPTY"
                )
            transformed_filter["triplet_summary." + key + "." + value] = {">": 0}
        else:
            raise Exception(
                "filter attribute {} not found within the listed attributes in runregistry/attributes.py. If this attribute does exist, please make a PR to this client.".format(
                    key
                )
            )
    return transformed_filter
