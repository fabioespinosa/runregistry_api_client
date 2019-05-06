[![Build Status](https://travis-ci.org/fabioespinosa/runregistry_api_client.svg?branch=master)](https://travis-ci.org/fabioespinosa/runregistry_api_client)

# Run Registry Client

Python client to retrieve and query data from [CMS Run Registry](https://cmsrunregistry.web.cern.ch).

## Installation

```bash
pip install runregistry
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
openssl pkcs12 -clcerts -nokeys -in myCertificate.p12 -out ~/private/usercert.pem
openssl pkcs12 -nocerts -in myCertificate.p12 -out ~/private/userkey.tmp.pem
openssl rsa -in ~/private/userkey.tmp.pem -out ~/private/userkey.pem
```

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

Apply a custom filter (run_numbers between 309000 and 310000 which had at least one GOOD dt lumisection):

```python
import runregistry
runregistry.get_runs(
    filter={
        'run_number': {
            'and':[
                '>': 309000,
                '<': 310000
            ]
        },
        'dt': 'GOOD'
    }
)
```

Depending on the attribute you can use different operators:

| Attribute     |       Supported operators       |
| ------------- | :-----------------------------: |
| Integer/float | '=', '>', '<', '>=', '<=', '<>' |
| String        |        =, like, notlike         |
| Boolean       |         = (true, false)         |

When using 'like' or 'notlike' operator, you must surround your query with percentage signs, see example below.

When filtering for triplet attributes (anything that is GOOD/BAD/STANDBY...) you must not use any String values, the only value allowed is strict equality '=' and is set by default.

You can combine the filters as well:

```python
import runregistry
runregistry.get_runs(
    filter={
        'run_number': {
            'and':[
                '>': 309000,
                '<': 310000
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
runregistry.get_runs(
    filter={
        'run_number': {
            '>': 309000, '<': 310000
        },
        'oms_attributes.hlt_key': {
            'like': '%commissioning2018%'
        },
        'triplet_summary.dt_triplet.GOOD': {
            '>': 0
        }
    },
    ignore_filter_transformation=True
)
```

Also, if by observing the Network Requests in RR web application, you want to obtain the data as it is seen in the network requests. Just `compress_attributes=False`, for example:

```python
import runregistry
runregistry.get_runs(
    filter={
        'run_number': {
            'and':[
                '>': 309000,
                '<': 310000
            ]
        },
        'dt': 'GOOD'
    },
    compress_attributes=False
)
```

querying by comments and cause is not yet possible
