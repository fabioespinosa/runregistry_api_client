import os
import json
import requests
from cernrequests import get_sso_cookies, certs
from runregistry.utils import transform_to_rr_run_filter, transform_to_rr_dataset_filter
import urllib3

# Silence unverified HTTPS warning:
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
PAGE_SIZE = 50

cert = "certs/usercert.pem"
key = "certs/userkey.pem"
api_url = "https://cmsrunregistry.web.cern.ch/api"
if os.getenv("ENVIRONMENT") == "development":
    api_url = "http://localhost:9500"
    cert = "certs/usercert.pem"
    key = "certs/userkey.pem"


def _get_cookies(url, **kwargs):
    """
    Gets the cookies required to query RR API
    :return: the cookies required to query Run Registry API. In particular 'connect.sid' is the one we are interested in
    """
    if os.getenv("ENVIRONMENT") == "development":
        return None
    cert = kwargs.pop("cert", None)
    # If no certificate provided, cernrequests will look in default paths:
    cert = cert if cert else certs.default_user_certificate_paths()
    if cert == ("", ""):
        raise Exception(
            'No certificate passed, pass one in a tuple as cert=(cert,key), to authenticate your request. Or place them in your /private folder on AFS under the names of "usercert.pem" and "userkey.pem", please read authentication on README.md for more details'
        )
    ca_bundle = certs.where()
    cookies = get_sso_cookies(url, cert)
    return cookies


def _get_page(
    url, page=0, data_type="runs", ignore_filter_transformation=False, **kwargs
):
    """
    :param ignore_filter_transformation: If user knows how the filter works (by observing http requests on RR website), and wants to ignore the suggested transformation to query API, user can do it by setting ignore_filter_transformation to True
    :param filter: The filter to be transformed into RR syntax, and then sent for querying
    :return: A page in Run registry
    """
    headers = {"Content-type": "application/json"}
    cookies = _get_cookies(url, **kwargs)
    query_filter = kwargs.pop("filter", {})
    if data_type == "runs" and not ignore_filter_transformation:
        query_filter = transform_to_rr_run_filter(run_filter=query_filter)
    elif data_type == "datasets" and not ignore_filter_transformation:
        query_filter = transform_to_rr_dataset_filter(dataset_filter=query_filter)
    if os.getenv("ENVIRONMENT") == "development":
        print(url)
        print(query_filter)
    payload = json.dumps(
        {
            "page": page,
            "filter": query_filter,
            "page_size": kwargs.pop("page_size", PAGE_SIZE),
            "sortings": kwargs.pop("sortings", []),
        }
    )
    return requests.post(url, cookies=cookies, headers=headers, data=payload).json()


def get_dataset_names_of_run(run_number, **kwargs):
    """
    Gets the existing dataset names of a run_number 
    :return: Array of dataset names of the specified run_number
    """
    url = "{}/get_all_dataset_names_of_run/{}".format(api_url, run_number)
    cookies = _get_cookies(url, **kwargs)
    return requests.get(url, cookies=cookies, verify=False).json()


def get_run(run_number, **kwargs):
    """
    Gets all the info about a particular run
    :param run_number: run_number of specified run
    """
    run = get_runs(filter={"run_number": run_number}, **kwargs)
    if len(run) != 1:
        return None
    return run[0]


def get_runs(limit=40000, compress_attributes=True, **kwargs):
    """
    Gets all runs that match the filter given in 
    :param compress_attributes: Gets the attributes inside rr_attributes:* and the ones in the DatasetTripletCache (The lumisections insdie the run/dataset) and spreads them over the run object
    :param filter: the filter applied to the runs needed
    """
    url = "{}/runs_filtered_ordered".format(api_url)
    initial_response = _get_page(url=url, data_type="runs", page=0, **kwargs)
    if "err" in initial_response:
        raise ValueError(initial_response["err"])

    resource_count = initial_response["count"]
    page_count = initial_response["pages"]
    runs = initial_response["runs"]
    if resource_count > limit:
        print(
            "ALERT: The specific run registry api request returns more runs than the limit({}), consider passing a greater limit to get_runs(limit=number) to get the whole result.".format(
                limit
            )
        )
    if resource_count > 10000:
        print(
            "WARNING: fetching more than 10,000 runs from run registry. you probably want to pass a filter into get_runs, or else this will take a while."
        )
    if resource_count > 20000 and "filter" not in kwargs:
        print(
            "ERROR: For run registry queries that retrieve more than 20,000 runs, you must pass a filter into get_runs, an empty filter get_runs(filter={}) works"
        )
        return None
    for page_number in range(1, page_count):
        additional_runs = _get_page(
            page=page_number, url=url, data_type="runs", **kwargs
        )
        runs.extend(additional_runs.get("runs"))
        if len(runs) >= limit:
            runs = runs[:limit]
            break

    if compress_attributes:
        compressed_runs = []
        for run in runs:
            compressed_run = {
                "oms_attributes": run["oms_attributes"],
                **run["rr_attributes"],
                "lumisections": run["DatasetTripletCache"]["triplet_summary"],
                **run,
            }
            del compressed_run["rr_attributes"]
            del compressed_run["DatasetTripletCache"]
            compressed_runs.append(compressed_run)
        return compressed_runs

    return runs


def get_dataset(run_number, dataset_name="online", **kwargs):
    """
    Gets information about the dataset specified by run_number and dataset_name
    :param run_number:  The run number of the dataset
    :param dataset_name: The name of the dataset. 'online' is the dataset of the online run. These are Run Registry specific dataset names e.g. online, /PromptReco/Collisions2018D/DQM, /Express/Collisions2018/DQM 
    """
    dataset = get_datasets(
        filter={"run_number": run_number, "dataset_name": dataset_name}, **kwargs
    )
    if len(dataset) != 1:
        return None
    return dataset[0]


def get_datasets(limit=40000, compress_attributes=True, **kwargs):
    """
    Gets all datasets that match the filter given
    :param compress_attributes: Gets the attributes inside rr_attributes:* and the ones in the DatasetTripletCache (The lumisections insdie the run/dataset) and spreads them over the run object
    """
    url = "{}/datasets_filtered_ordered".format(api_url)
    initial_response = _get_page(url=url, data_type="datasets", page=0, **kwargs)
    if "err" in initial_response:
        raise ValueError(initial_response["err"])

    resource_count = initial_response["count"]
    page_count = initial_response["pages"]
    datasets = initial_response["datasets"]
    if resource_count > limit:
        print(
            "ALERT: The specific api request returns more datasets than the limit({}), consider passing a greater limit to get_datasets(limit=number) to get the whole result.".format(
                limit
            )
        )
    if resource_count > 10000:
        print(
            "WARNING: fetching more than 10,000 datasets. you probably want to pass a filter into get_datasets, or else this will take a while."
        )
    if resource_count > 20000 and "filter" not in kwargs:
        print(
            "ERROR: For queries that retrieve more than 20,000 datasets, you must pass a filter into get_datasets, an empty filter get_datasets(filter={}) works"
        )
        return None
    for page_number in range(1, page_count):
        additional_datasets = _get_page(
            page=page_number, url=url, data_type="datasets", **kwargs
        )
        datasets.extend(additional_datasets.get("datasets"))
        if len(datasets) >= limit:
            datasets = datasets[:limit]
            break

    if compress_attributes:
        compressed_datasets = []
        for dataset in datasets:
            compressed_dataset = {
                **dataset["Run"]["rr_attributes"],
                **dataset,
                "lumisections": dataset["DatasetTripletCache"]["triplet_summary"],
            }
            del compressed_dataset["DatasetTripletCache"]
            del compressed_dataset["Run"]
            compressed_datasets.append(compressed_dataset)
        return compressed_datasets
    return datasets


def _get_lumisection_helper(url, run_number, dataset_name="online", **kwargs):
    """
    Puts the headers, and cookies for all other lumisection methods
    """
    headers = {"Content-type": "application/json"}
    cookies = _get_cookies(url, **kwargs)
    payload = json.dumps({"run_number": run_number, "dataset_name": dataset_name})
    return requests.post(url, cookies=cookies, headers=headers, data=payload).json()


def get_lumisections(run_number, dataset_name="online", **kwargs):
    """
    Gets the Run Registry lumisections of the specified dataset
    """
    url = "{}/lumisections/rr_lumisections".format(api_url)
    return _get_lumisection_helper(url, run_number, dataset_name, **kwargs)


def get_oms_lumisections(run_number, dataset_name="online", **kwargs):
    """
    Gets the OMS lumisections saved in RR database
    """
    url = "{}/lumisections/oms_lumisections".format(api_url)
    return _get_lumisection_helper(url, run_number, dataset_name, **kwargs)


def get_lumisection_ranges(run_number, dataset_name="online", **kwargs):
    """
    Gets the lumisection ranges of the specified dataset
    """
    url = "{}/lumisections/rr_lumisection_ranges".format(api_url)
    return _get_lumisection_helper(url, run_number, dataset_name, **kwargs)


def get_oms_lumisection_ranges(run_number, **kwargs):
    """
    Gets the OMS lumisection ranges of the specified dataset (saved in RR database)
    """
    url = "{}/lumisections/oms_lumisection_ranges".format(api_url)
    return _get_lumisection_helper(url, run_number, dataset_name="online", **kwargs)


def get_joint_lumisection_ranges(run_number, dataset_name="online", **kwargs):
    """
    Gets the lumisection ranges of the specified dataset, breaken into RR breaks and OMS ranges
    """
    url = "{}/lumisections/joint_lumisection_ranges".format(api_url)
    return _get_lumisection_helper(url, run_number, dataset_name, **kwargs)

