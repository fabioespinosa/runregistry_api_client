[![Build Status](https://travis-ci.org/fabioespinosa/runregistry_api_client.svg?branch=master)](https://travis-ci.org/fabioespinosa/runregistry_api_client)

# Run Registry Client

Python client to retrieve and query data from [CMS Run Registry](https://cmsrunregistry.web.cern.ch).

## Installation

```bash
pip install runregistry
```

## Python version and Virtual env

Python version>=3.6 is required for this package.

To use python 3.6 in lxplus: https://cern.service-now.com/service-portal/article.do?n=KB0000730
A virtual environment is also required, if you are in lxplus you should run the following commands:

```bash
virtualenv venv
source venv/bin/activate
```

## Authentication (Prerequisite)

You must provide a way for the client to access a [Grid user certificate](https://ca.cern.ch/ca/).

You can either do this in 3 possible ways:

1.  Provide the certificate manually (explained below).
2.  providing a **passwordless** user certificate in the conventional path (first `~/private/` and second `~/.globus/`) (explained below).
3.  Setting your own path where you store the certificate in an environment variable: `CERN_CERTIFICATE_PATH`

### Provide the certificate manually

1. Download a grid user certificate from [here](https://ca.cern.ch/ca/).
2. Convert it into public and private key (**The certificates have to be passwordless**.
   ):

```bash
mkdir -p ~/private
# For next commands Import Password is blank, PEM passphrase needs to be set
openssl pkcs12 -clcerts -nokeys -in myCertificate.p12 -out ~/private/usercert.pem
openssl pkcs12 -nocerts -in myCertificate.p12 -out ~/private/userkey.tmp.pem
openssl rsa -in ~/private/userkey.tmp.pem -out ~/private/userkey.pem
```

If you are in lxplus, everything should be done at this point since the package will first look for `~/private/` and the above commands will set up the certificate in `~/private/`.

If you want to continue providing the certificate manually, you will have to modify the commands above with -out into a folder you remember.

Then use the client in the following way:

```python
import runregistry
run = runregistry.get_run(run_number=328762, cert=(cert, key) )
```

where cert and key are paths to the usercert.pem and userkey.pem generated above.

## Usage

### Get a single run (get_run):

```python
import runregistry
run = runregistry.get_run(run_number=328762)
```

### Query several runs (get_runs):

```python
import runregistry
runs = runregistry.get_runs(filter={
   'run_number':{
      'or': [328762, 323555, 323444]
    }
})
```

Apply a custom filter (run_numbers between 309000 and 310000 which had at least one GOOD dt lumisection)

```python
import runregistry
runs = runregistry.get_runs(
    filter={
        'run_number': {
            'and':[
                {'>': 309000},
                {'<': 310000}
            ]
        },
        'dt-dt': 'GOOD'
    }
)
```

Do note that we use `dt-dt` ('dt' twice) this is due to the fact that there are multiple workspaces, the first 'dt' states we are in dt workspace, the second 'dt' states we want column 'dt'. So the syntax for status flags is `{workspace}-{column}`. If we wanted runs with the strip column from tracker workspace to have at least 1 lumisection GOOD, the query would look like this:

```python
import runregistry
runs = runregistry.get_runs(
    filter={
        'run_number': {
            'and':[
                {'>': 309000},
                {'<': 310000}
            ]
        },
        'tracker-strip': 'GOOD'
    }
)
```

Depending on the attribute you can use different operators:

#### Operators

| Attribute |       Supported operators       |
| --------- | :-----------------------------: |
| number    | '=', '>', '<', '>=', '<=', '<>' |
| String    |        =, like, notlike         |
| Boolean   |         = (true, false)         |
| date      | '=', '>', '<', '>=', '<=', '<>' |

When using `like` or `notlike` operator, you must surround your query with percentage signs, see example below.

When filtering for triplet attributes (anything that is GOOD/BAD/STANDBY...) you must not use any String values, the only value allowed is strict equality '=' and is set by default. The values allowed are GOOD, BAD, STANDBY, NOTSET, EXCLUDED and EMPTY.

You can combine the filters as well:

```python
import runregistry
runs = runregistry.get_runs(
    filter={
        'run_number': {
            'and':[
                {'>': 309000},
                {'<': 310000}
            ]
        },
        'hlt_key': {
            'like': '%commissioning2018%'
        }
        'significant': {
            '=': True
        }
    }
)
```

If by observing the Network Requests in RR web application, you want to use the same filters observed by the network request. Just passs `ignore_filter_transformation=True` to any query.

Example (run_numbers between 309000 and 310000 which had at least one GOOD dt lumisection):

```python
import runregistry
runs = runregistry.get_runs(
    filter={
        'run_number': {
            'and':[
                {'>': 309000},
                {'<': 310000}
            ]
        },
        # Remember! this will only work if you pass ignore_filter_transformation=True (please read above what this means), otherwise use the other examples
        'oms_attributes.hlt_key': {
            'like': '%commissioning2018%'
        },
        'triplet_summary.dt-dt.GOOD': {
            '>': 0
        }
    },
    ignore_filter_transformation=True
)
```

Also, if by observing the Network Requests in RR web application, you want to obtain the data as it is seen in the network requests. Just `compress_attributes=False`, for example:

```python
import runregistry
runs = runregistry.get_runs(
    filter={
        'run_number': {
            'and':[
                {'>': 309000},
                {'<': 310000}
            ]
        },
        'dt': 'GOOD'
    },
    compress_attributes=False
)
```

querying by comments and cause is not yet possible

### Get dataset

```python
import runregistry
dataset = runregistry.get_dataset(
        run_number=327604,
        dataset_name="/PromptReco/HICosmics18A/DQM"
    )
```

### Get datasets

```python
import runregistry
datasets = runregistry.get_datasets(
    filter={
        'run_number': {
            'and':[
                {'>': 309000},
                {'<': 310000}
            ]
        }
    }
)
```

### Get Lumisections

#### Get the array of lumisections

You can query the lumisections of a run (or dataset), you will need the run number and the dataset name (when querying for a run, the dataset name must be 'online')

```python
import runregistry
# lumisections = runregistry.get_lumisections(run_number, dataset_name)
lumisections = runregistry.get_lumisections(327743, "/PromptReco/HICosmics18A/DQM")
```

The response will be an array of lumisections which will contain `{workspace}-{column}: {"status":"Either GOOD/BAD/STANDBY...", "comment": "a comment made for the range", "cause":"a common repeated cause"}`

To get OMS data: use the OMS API. You should only use Run Registry for data that RR is responsible for.
However if you still want to access OMS lumisections, you can do so like this:

Previous Run Registry allowed you to change OMS (in that time WBM) attributes per dataset, if you need certain dataset lumisections you can provide the name of the RR dataset in the second argument:

```python
import runregistry
# oms_lumisections = runregistry.get_oms_lumisections(run_number, dataset_name)
oms_lumisections = get_oms_lumisections(327743, 'online')
# If you want to get particular dataset that is not online for OMS lumisections:
dataset_oms_lumisections = get_oms_lumisections(327743, '/PromptReco/HICosmics18A/DQM')
```

#### Get lumisection ranges

Usually there will be runs/datasets which contain an enormous amount of lumisections (some even more than 5000), therefore it can be heavy on the API to query for these type of lumisections.

A query to retrieve ranges is also possible, you can do it like this:

```python
import runregistry
# lumisections = runregistry.get_lumisection_ranges(run_number, dataset_name)
lumisections = runregistry.get_lumisection_ranges(327743, "/PromptReco/HICosmics18A/DQM")
```

You will receive an array of ranges, that apart from stating the triplets (comment, status and cause) for each column, the array will consist of two more attributes called **start** (lumisection where range starts) and **end** (lumisection where range ends).

### Handling the response

When filtering runs, the attributes from the response get divided into those belonging to OMS and those belonging to RR (to see which belong to which, see the tables below, or go through a response).

Those that belong to OMS are inside "oms_attributes".

Those that belong to RR are inside "rr_attributes".

### Attributes available to query

According to the type of attribute (number, string, boolean), see the Operator table above to see which types of operators can be applied to querying

Oms Attributes:

| Attribute                                                                                  |  Type   | Belongs to |
| ------------------------------------------------------------------------------------------ | :-----: | :--------: |
| run_number                                                                                 | number  |    OMS     |
| energy                                                                                     | number  |    OMS     |
| l1_key                                                                                     | string  |    OMS     |
| b_field                                                                                    | number  |    OMS     |
| hlt_key                                                                                    | string  |    OMS     |
| l1_menu                                                                                    | string  |    OMS     |
| l1_rate                                                                                    | number  |    OMS     |
| duration                                                                                   | number  |    OMS     |
| end_lumi                                                                                   | number  |    OMS     |
| end_time                                                                                   |  date   |    OMS     |
| sequence                                                                                   | string  |    OMS     |
| init_lumi                                                                                  | number  |    OMS     |
| clock_type                                                                                 | string  |    OMS     |
| start_time                                                                                 |  date   |    OMS     |
| fill_number                                                                                | number  |    OMS     |
| l1_hlt_mode                                                                                | string  |    OMS     |
| last_update                                                                                |  date   |    OMS     |
| ls_duration                                                                                | number  |    OMS     |
| stable_beam                                                                                | boolean |    OMS     |
| trigger_mode                                                                               | string  |    OMS     |
| cmssw_version                                                                              | string  |    OMS     |
| recorded_lumi                                                                              | number  |    OMS     |
| delivered_lumi                                                                             | number  |    OMS     |
| tier0_transfer                                                                             | boolean |    OMS     |
| l1_key_stripped                                                                            | string  |    OMS     |
| fill_type_party1                                                                           | string  |    OMS     |
| fill_type_party2                                                                           | string  |    OMS     |
| hlt_physics_rate                                                                           | number  |    OMS     |
| hlt_physics_size                                                                           | number  |    OMS     |
| fill_type_runtime                                                                          | string  |    OMS     |
| hlt_physics_counter                                                                        | number  |    OMS     |
| l1_triggers_counter                                                                        | number  |    OMS     |
| l1_hlt_mode_stripped                                                                       | string  |    OMS     |
| hlt_physics_throughput                                                                     | number  |    OMS     |
| initial_prescale_index                                                                     | number  |    OMS     |
| beams_present_and_stable                                                                   | boolean |    OMS     |
| es_included                                                                                | boolean |    OMS     |
| hf_included                                                                                | boolean |    OMS     |
| daq_included                                                                               | boolean |    OMS     |
| dcs_included                                                                               | boolean |    OMS     |
| dqm_included                                                                               | boolean |    OMS     |
| gem_included                                                                               | boolean |    OMS     |
| trg_included                                                                               | boolean |    OMS     |
| hcal_included                                                                              | boolean |    OMS     |
| tcds_included                                                                              | boolean |    OMS     |
| pixel_included                                                                             | boolean |    OMS     |
| tracker_included                                                                           | boolean |    OMS     |
| \*\_included (be sure to add it to the validation runregistry/attributes if it's not here) | boolean |    OMS     |

RR Run Attributes:

| Attribute   |  Type   | Belongs to |
| ----------- | :-----: | :--------: |
| class       | string  |     RR     |
| state       | string  |     RR     |
| significant | boolean |     RR     |
| stop_reason | string  |     RR     |

RR Dataset Attributes:

| Attribute     |  Type  | Belongs to |
| ------------- | :----: | :--------: |
| dataset_name  | string |     RR     |
| dt_state      | string |     RR     |
| csc_state     | string |     RR     |
| hlt_state     | string |     RR     |
| l1t_state     | string |     RR     |
| rpc_state     | string |     RR     |
| tau_state     | string |     RR     |
| btag_state    | string |     RR     |
| ecal_state    | string |     RR     |
| hcal_state    | string |     RR     |
| lumi_state    | string |     RR     |
| muon_state    | string |     RR     |
| ctpps_state   | string |     RR     |
| castor_state  | string |     RR     |
| egamma_state  | string |     RR     |
| global_state  | string |     RR     |
| jetmet_state  | string |     RR     |
| tracker_state | string |     RR     |

The dt_state, csc_state and so on, are the workspace OFFLINE states of the datasets, they can be either OPEN, SIGNOFF or COMPLETED.

For Offline and Online status flags, filtering is also available. The Attribute is composed by `{workspace}-{column}`. So for example if we want to query for GOOD tracker-strip datasets of runs between 309000 and 310000, we would do it like this:

```python
import runregistry
datasets = runregistry.get_datasets(filter={
    'tracker-strip':'GOOD'
    'run_number': {'and': [{'>': 309000}, {'<': 310000}]},
})
```

## Generating JSONs

In order to generate JSONs (like the golden json) you must send the configuration of the attributes you wish the generated json to satisfy (in json-logic) TODO: make manual.

The json logic below generates a json file for all datasets that belong to era A,B, C, D, E, F, G, H, I from year 2018, and also

```python
import runregistry
json_logic = {
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
generated_json = runregistry.generate_json(json_logic)
```

## Running Tests

```
pytest --cov .
````

## Troubleshooting

### Support

If you have any questions, or the client is not working properly feel free to drop me an email at [f.e@cern.ch](mailto:f.e@cern.ch). Or through skype at fabioe24, i'm also available in mattermost.

### To update PIP package

```bash
python setup.py sdist bdist_wheel
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
````

## FAQ

### Does this work with Python 2.7?

No.
