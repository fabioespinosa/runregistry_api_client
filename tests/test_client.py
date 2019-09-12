import os
import pytest
import json


from runregistry.runregistry import (
    get_run,
    get_runs,
    get_dataset_names_of_run,
    get_dataset,
    get_datasets,
    get_lumisections,
    get_oms_lumisections,
    get_lumisection_ranges,
    get_oms_lumisection_ranges,
    get_joint_lumisection_ranges,
    generate_json,
)


common_run_number = 327743
common_dataset_name = "/PromptReco/HICosmics18A/DQM"


def test_with_local_certificate():
    # if os.getenv("ENVIRONMENT") == "development":
    # For this test to pass you must include cert and key in certs/ folder:
    cert = "certs/usercert.pem"
    key = "certs/userkey.pem"
    run = get_run(run_number=common_run_number, cert=(cert, key))
    assert run["run_number"] == common_run_number
    lumisections = get_oms_lumisections(run_number=common_run_number, cert=(cert, key))
    assert len(lumisections) > 0
    # else:
    #     pass


def test_get_run():
    run_number = 328762
    run = get_run(run_number=328762)
    # print(run)
    assert run["run_number"] == run_number
    # Non existent run:
    run_number = 8888888888
    run = get_run(run_number=run_number)
    assert run == None


def test_get_runs():
    # Gets runs between run number 309000 and 310000
    filter_run = {"run_number": {"and": [{">": 309000}, {"<": 310000}]}}
    runs = get_runs(filter=filter_run)
    assert len(runs) > 0
    # Gets runs that contain lumisections that classified DT as GOOD AND lumsiections that classified hcal as STANDBY
    filter_run = {
        "run_number": {"and": [{">": 309000}, {"<": 310000}]},
        "dt-dt": "GOOD"
        # 'hcal': 'STANDBY'
    }

    runs = get_runs(filter=filter_run)
    assert len(runs) > 0
    runs = []

    filter_run = {
        "run_number": {"and": [{">": 309000}, {"<": 310000}]},
        "tracker-strip": "GOOD",
    }
    runs = get_runs(filter=filter_run)
    print(json.dumps(runs))
    assert len(runs) > 0


def test_get_runs_with_ignore_filter():
    filter_run = {
        "run_number": {"and": [{">": 309000}, {"<": 310000}]},
        "oms_attributes.hlt_key": {"like": "%commissioning2018%"},
        "triplet_summary.dt-dt.GOOD": {">": 0},
    }
    runs = get_runs(filter=filter_run, ignore_filter_transformation=True)
    assert len(runs) > 0


def test_get_runs_not_compressed():
    runs = get_runs(
        filter={"run_number": {"and": [{">": 309000}, {"<": 310000}]}, "dt-dt": "GOOD"},
        compress_attributes=False,
    )
    assert len(runs) > 0


def get_runs_with_combined_filter():
    runs = get_runs(
        filter={
            "run_number": {
                "and": [{">": 309000}, {"<": 310000}]
                # },
                # 'hlt_key': {
                #     'like': '%commissioning2018%'
                # },
                # 'significant': {
                #     '=': True
            }
        }
    )
    assert len(runs) > 0


def test_get_dataset_names_of_run():
    dataset_names = get_dataset_names_of_run(run_number=321777)
    assert len(dataset_names) > 0


def test_get_dataset():
    dataset = get_dataset(
        run_number=common_run_number, dataset_name=common_dataset_name
    )
    assert dataset["run_number"] == common_run_number
    assert dataset["name"] == common_dataset_name


def test_get_datasets():
    datasets = get_datasets(
        filter={"run_number": {"and": [{">": 309000}, {"<": 310000}]}}
    )
    assert len(datasets) > 0


def test_get_lumisections():
    lumisections = get_lumisections(common_run_number, common_dataset_name)
    assert len(lumisections) > 0


def test_get_oms_lumisections():
    lumisections = get_oms_lumisections(common_run_number)
    assert len(lumisections) > 0
    dataset_lumisections = get_oms_lumisections(common_run_number, common_dataset_name)
    assert len(dataset_lumisections) > 0


def test_get_lumisection_ranges():
    lumisections = get_lumisection_ranges(common_run_number, common_dataset_name)
    assert len(lumisections) > 0


def test_get_oms_lumisection_ranges():
    lumisections = get_lumisection_ranges(common_run_number, common_dataset_name)
    assert len(lumisections) > 0


def test_get_joint_lumisection_ranges():
    lumisections = get_joint_lumisection_ranges(common_run_number, common_dataset_name)
    assert len(lumisections) > 0


def test_get_collisions18():
    runs = get_runs(filter={"class": "Collisions18"})
    assert len(runs) > 0


def test_get_datasets_with_filter():
    datasets = get_datasets(
        filter={
            "run_number": {"and": [{">": 309000}, {"<": 310000}]},
            "tracker-strip": "GOOD",
        }
    )
    assert len(datasets) > 0


def test_generate_json():
    json_logic = """
        {
        "and": [
            {
                "or": [
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018A/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018B/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018C/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018D/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018E/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018F/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018G/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018H/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018I/DQM"]}
                ]
            },
            { ">=": [{ "var": "run.oms.energy" }, 6000] },
            { "<=": [{ "var": "run.oms.energy" }, 7000] },
            { ">=": [{ "var": "run.oms.b_field" }, 3.7] },
            { "in": [ "25ns", { "var": "run.oms.injection_scheme" }] },
            { "==": [{ "in": [ "WMass", { "var": "run.oms.hlt_key" }] }, false] },

            { "==": [{ "var": "lumisection.rr.dt-dt" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.csc-csc" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.l1t-l1tmu" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.l1t-l1tcalo" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.hlt-hlt" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.tracker-pixel" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.tracker-strip" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.tracker-track" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.ecal-ecal" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.ecal-es" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.hcal-hcal" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.muon-muon" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.jetmet-jetmet" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.lumi-lumi" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.dc-lowlumi" }, "BAD"] },

            { "==": [{ "var": "lumisection.oms.cms_active" }, true] },
            { "==": [{ "var": "lumisection.oms.bpix_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.fpix_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.tibtid_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.tecm_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.tecp_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.tob_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.ebm_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.ebp_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.eem_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.eep_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.esm_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.esp_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.hbhea_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.hbheb_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.hbhec_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.hf_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.ho_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.dtm_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.dtp_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.dt0_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.cscm_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.cscp_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.rpc_ready" }, true] },
            { "==": [{ "var": "lumisection.oms.beam1_present" }, true] },
            { "==": [{ "var": "lumisection.oms.beam2_present" }, true] },
            { "==": [{ "var": "lumisection.oms.beam1_stable" }, true] },
            { "==": [{ "var": "lumisection.oms.beam2_stable" }, true] }
        ]
    }
    """
    final_json = generate_json(json_logic)
    assert final_json is not None
    json_logic2 = {
        "and": [
            {
                "or": [
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018A/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018B/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018C/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018D/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018E/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018F/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018G/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018H/DQM"]},
                    {"==": [{"var": "dataset.name"}, "/PromptReco/Collisions2018I/DQM"]}
                ]
            },
            { ">=": [{ "var": "run.oms.energy" }, 6000] },
            { "<=": [{ "var": "run.oms.energy" }, 7000] },
            { ">=": [{ "var": "run.oms.b_field" }, 3.7] },
            { "in": [ "25ns", { "var": "run.oms.injection_scheme" }] },
            { "==": [{ "in": [ "WMass", { "var": "run.oms.hlt_key" }] }, False] },

            { "==": [{ "var": "lumisection.rr.dt-dt" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.csc-csc" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.l1t-l1tmu" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.l1t-l1tcalo" }, "GOOD"] },
            { "==": [{ "var": "lumisection.rr.hlt-hlt" }, "GOOD"] },

            { "==": [{ "var": "lumisection.oms.bpix_ready" }, True] }
        ]
    }
    final_json2 = generate_json(json_logic2)


    assert final_json2 is not None

test_generate_json()