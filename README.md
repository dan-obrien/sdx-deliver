# sdx-deliver
[![Build Status](https://github.com/ONSdigital/sdx-deliver/workflows/Build/badge.svg)](https://github.com/ONSdigital/sdx-deliver) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/0d8f1899b0054322b9d0ec8f2bd62d86)](https://www.codacy.com/app/ons-sdc/sdx-deliver?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ONSdigital/sdx-deliver&amp;utm_campaign=Badge_Grade)
 
The SDX-Deliver service is responsible for ensuring that all SDX outputs are delivered to DAP. This is done by
encrypting and storing data into a GCP Bucket. It then notifies DAP of the data's location. Metadata is provided for
validation once decrypted downstream.

## Process

SDX-Deliver is flask application made up of **five** endpoints. As a request is made to the service, metadata 
is extracted and the data is then stored within a google bucket. The metadata is used to 
construct a PubSub message to: `dap-topic`. This notifies DAP that a new submission is in the bucket.
##### note:
**SEFT** submissions are already encrypted as they come through SDX and therefore require no additional encryption 
before being stored

## Getting started
Install pipenv:
```shell
$ pip install pipenv
```

Create a virtualenv and install dependencies
```shell
$ make build
```

**Testing**:
Install all test requirements and run tests:
```shell
$ make test
```

**Running**:
ensure you have installed all requirements with above `make build` command then:
```shell
$ make start
```

## GCP

### PubSub

Once a submission has been successfully encrypted and stored in the Bucket. A message is published to the `dap-topic`.

**Message Structure Example:**
```python
dap_message: Message {
  data: b'{"version": "1", "files": [{"name": "087bfc03-8698...'
  ordering_key: ''
  attributes: {
    "gcs.bucket": "ons-sdx-sandbox-outputs",
    "gcs.key": "dap/087bfc03-8698-4137-a3ac-7a596b9beb2b",
    "tx_id": "087bfc03-8698-4137-a3ac-7a596b9beb2b"
  }
}
```
**Message Data field Example:**
```python
    data : {
        'version': '1',
        'files': [{
            'name': meta_data.filename,
            'sizeBytes': meta_data.sizeBytes,
            'md5sum': meta_data.md5sum
        }],
        'sensitivity': 'High',
        'sourceName': CONFIG.PROJECT_ID,
        'manifestCreated': get_formatted_current_utc(),
        'description': meta_data.get_description(),
        'dataset': dataset,
        'schemaversion': '1'
    }
```

### Google Storage

All submissions are stored within: `ons-sdx-{project_id}-outputs` in their respective folders. The file-path is
specified in `attributes."gcs.key"`.

### Secret Manager
The gpg key used to encrypt JSON surveys: `dap-public-gpg` is managed by Google Secret Manager. A single API call is 
made on program startup and stored in `ENCRYPTION_KEY`.

## API endpoints

Allows Survey, SEFT and Collate to send data to be stored by deliver


* `POST /deliver/dap` - Stores JSON surveys destined for DAP

* `POST /deliver/legacy` - Stores JSON surveys destined for Legacy downstream

* `POST /deliver/feedback` - Stores JSON Feedback submissions

* `POST /deliver/comments` - Stores zipped spreadsheet (.xls) of comments

* `POST /deliver/seft` - Stores SEFT submissions


##### note: 
deliver runs within the kubernetes cluster and utilises a `kubernetes service`.This assigns the service with an IP 
address and DNS name exposing it to the other services.

## Configuration
| Environment Variable    | Description
|-------------------------|------------------------------------
| PROJECT_ID              | Name of project
| BUCKET_NAME             | Name of the bucket: `{project_id}-outputs`
| BUCKET                  | Bucket client to GCP
| DAP_TOPIC_PATH          | Name of the dap topic: `dap-topic`
| DAP_PUBLISHER           | PubSub publisher client to GCP
| ENCRYPTION_KEY          | Key to encrypt all data
| GPG                     | System GPG key import

## License

Copyright © 2016, Office for National Statistics (https://www.ons.gov.uk)

Released under MIT license, see [LICENSE](LICENSE) for details.
