from runregistry.runregistry import get_run, get_runs, get_dataset_names_of_run, get_dataset, get_datasets, get_lumisections, get_oms_lumisections, get_lumisection_ranges, get_oms_lumisection_ranges, get_joint_lumisection_ranges
import pytest


def test_get_run():
    run_number = 328762
    run = get_run(run_number=run_number)
    # print(run)
    assert run['run_number'] == run_number
    # Non existent run:
    run_number = 8888888888
    run = get_run(run_number=run_number)
    assert run == None


def test_get_runs():
    # Gets runs between run number 309000 and 310000
    filter_run = {
        'run_number': {
            '>': 309000,
            '<': 310000
        }
    }
    runs = get_runs(filter=filter_run)
    assert len(runs) > 0
    # Gets runs that contain lumisections that classified DT as GOOD AND lumsiections that classified hcal as STANDBY
    filter_run = {
        'dt': 'GOOD',
        'hcal': 'STANDBY'
    }
    runs = get_runs(filter=filter_run)
    assert len(runs) > 0


def test_get_dataset_names_of_run():
    dataset_names = get_dataset_names_of_run(run_number=321777)


def test_get_dataset():
    run_number = 328762
    dataset_name = '/Express/Commissioning2018/DQM'
    dataset = get_dataset(run_number=run_number, dataset_name=dataset_name)
    print(dataset)
    assert dataset['run_number'] == run_number
    assert dataset['name'] == dataset_name


def test_get_datasets():
    pass


def test_get_lumisections():
    run_number = 328762
    dataset_name = '/Express/Commissioning2018/DQM'
    lumisections = get_lumisections(run_number, dataset_name)
    assert len(lumisections) > 0


def test_get_oms_lumisections():
    run_number = 328762
    lumisections = get_oms_lumisections(run_number)
    assert len(lumisections) > 0


def test_get_lumisection_ranges():
    run_number = 328762
    dataset_name = '/Express/Commissioning2018/DQM'
    lumisections = get_lumisection_ranges(run_number, dataset_name)
    assert len(lumisections) > 0


def test_get_oms_lumisection_ranges():
    run_number = 328762
    dataset_name = '/Express/Commissioning2018/DQM'
    lumisections = get_lumisection_ranges(run_number, dataset_name)
    assert len(lumisections) > 0


def test_get_joint_lumisection_ranges():
    run_number = 328762
    dataset_name = '/Express/Commissioning2018/DQM'
    lumisections = get_joint_lumisection_ranges(run_number, dataset_name)
    print(lumisections)
    assert len(lumisections) > 0
