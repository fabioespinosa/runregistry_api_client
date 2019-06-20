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
2.  providing the user certificate in the conventional path (first `~\private\` and second `~\.globus\`).
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

TODO: finish way to insert certificate

## Usage

### Get a single run (get_run):

```python
import runregistry
runregistry.get_run(run_number=328762)
```

### Query several runs (get_runs):

```python
import runregistry
runregistry.get_runs(run_number={
    'or': [328762, 323555, 323444]
})
```

Apply a custom filter (run_numbers between 309000 and 310000 which had at least one GOOD dt lumisection)

```python
import runregistry
runregistry.get_runs(
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

Do note that we use dt-dt ('dt' twice) this is due to the fact that there are multiple workspaces, the first 'dt' states we are in dt workspace, the second 'dt' states we want column 'dt'. So the syntax for status flags is {workspace}-{column}. If we wanted runs the strip column from tracker workspace to be GOOD, the query would look like this:

```python
import runregistry
runregistry.get_runs(
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

When using 'like' or 'notlike' operator, you must surround your query with percentage signs, see example below.

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
        'run_number': 327604,
        'dataset_name':"/PromptReco/HICosmics18A/DQM"
    )
```

### Get datasets

```python
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

### Handling the response

When filtering runs, the attributes from the response get divided into those belonging to OMS and those belonging to RR (to see which belong to which, see the tables below, or go through a response).

Those that belong to OMS are inside "oms_attributes".

Those that belong to RR are inside "rr_attributes".

### Attributes available to query

According to the type of attribute (number, string, boolean), see the Operator table above to see which types of operators can be applied to querying

Oms Attributes:

| Attribute                |  Type   | Belongs to |
| ------------------------ | :-----: | :--------: |
| run_number               | number  |    OMS     |
| energy                   | number  |    OMS     |
| l1_key                   | string  |    OMS     |
| b_field                  | number  |    OMS     |
| hlt_key                  | string  |    OMS     |
| l1_menu                  | string  |    OMS     |
| l1_rate                  | number  |    OMS     |
| duration                 | number  |    OMS     |
| end_lumi                 | number  |    OMS     |
| end_time                 |  date   |    OMS     |
| sequence                 | string  |    OMS     |
| init_lumi                | number  |    OMS     |
| clock_type               | string  |    OMS     |
| start_time               |  date   |    OMS     |
| fill_number              | number  |    OMS     |
| l1_hlt_mode              | string  |    OMS     |
| last_update              |  date   |    OMS     |
| ls_duration              | number  |    OMS     |
| stable_beam              | boolean |    OMS     |
| trigger_mode             | string  |    OMS     |
| cmssw_version            | string  |    OMS     |
| recorded_lumi            | number  |    OMS     |
| delivered_lumi           | number  |    OMS     |
| tier0_transfer           | boolean |    OMS     |
| l1_key_stripped          | string  |    OMS     |
| fill_type_party1         | string  |    OMS     |
| fill_type_party2         | string  |    OMS     |
| hlt_physics_rate         | number  |    OMS     |
| hlt_physics_size         | number  |    OMS     |
| fill_type_runtime        | string  |    OMS     |
| hlt_physics_counter      | number  |    OMS     |
| l1_triggers_counter      | number  |    OMS     |
| l1_hlt_mode_stripped     | string  |    OMS     |
| hlt_physics_throughput   | number  |    OMS     |
| initial_prescale_index   | number  |    OMS     |
| beams_present_and_stable | boolean |    OMS     |

RR Attributes:

| Attribute   |  Type   | Belongs to |
| ----------- | :-----: | :--------: |
| class       | string  |     RR     |
| state       | string  |     RR     |
| significant | boolean |     RR     |
| stop_reason | string  |     RR     |

RR offline Status Attributes:

| Attribute |  Type  | Belongs to |
| --------- | :----: | :--------: |
| dt        | string |     RR     |
| es        | string |     RR     |
| cms       | string |     RR     |
| csc       | string |     RR     |
| hlt       | string |     RR     |
| l1t       | string |     RR     |
| pix       | string |     RR     |
| rpc       | string |     RR     |
| ecal      | string |     RR     |
| hcal      | string |     RR     |
| lumi      | string |     RR     |
| ctpps     | string |     RR     |
| l1tmu     | string |     RR     |
| strip     | string |     RR     |
| castor    | string |     RR     |
| l1tcalo   | string |     RR     |

For Offline status flags, filtering is also available. The Attribute is composed by {workspace}-{column}. So for example if we want to query for GOOD tracker-strip datasets of runs between 309000 and 310000, we would do it like this:

```python
import runregistry
datasets = runregistry.get_datasets(filter={
    'tracker-strip':'GOOD'
    'run_number': {'and': [{'>': 309000}, {'<': 310000}]},
})
```

## Troubleshooting

## Support

If you have any questions, or the client is not working properly feel free to drop me an email at [f.e@cern.ch](mailto:f.e@cern.ch). Or through skype at fabioe24, i'm also available in mattermost.
