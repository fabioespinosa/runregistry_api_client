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
