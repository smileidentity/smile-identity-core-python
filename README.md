# SmileIdentityCore

The official Smile Identity library exposes four classes namely; the WebApi class, the IDApi class, the Signature class, and the Utilities class.

The **WebApi Class** allows you as the Partner to validate a user’s identity against the relevant Identity Authorities/Third Party databases that Smile Identity has access to using ID information provided by your customer/user (including photo for compare). It has the following public method:
- submit_job
- get_web_token

The **IDApi Class** lets you perform basic KYC Services including verifying an ID number as well as retrieve a user's Personal Information. It has the following public methods:
- submit_job

The **Signature Class** allows you as the Partner to generate a sec key to interact with our servers. It has the following public methods:
- generate_sec_key

The **Utilities Class** allows you as the Partner to have access to our general Utility functions to gain access to your data. It has the following public methods:
- get_job_status
- validate_id_params
- validate_partner_params
- get_smile_id_services

### Security
We accept 2 forms of security to communicate with our servers. The sec_key is the legacy means of communicating with our servers. This uses the v1 api key. The signature field is our new improved means of signing requests. To calculate a signature you need to generate a v2 api key. Generating a v2 api key does not invalidate existing v1 keys so you can safely upgrade. The library will default to calculating the legacy sec_key so your existing code will continue to behave as expected. To use the new signature form of security pass the boolean signature: true in the options object to any of our classes except Signature, where you would instead call the generate_signature function instead of the generate_sec_key function.

## Documentation

This library requires specific input parameters, for more detail on these parameters please refer to our [documentation for Web API](https://docs.smileidentity.com/products/core-libraries/python).

Please note that you will have to be a Smile Identity Partner to be able to query our services. You can sign up on the [Portal](https://portal.smileidentity.com/signup).

## Installation

View the package on [Pypi](https://pypi.org/project/smile-id-core/).

Add the group, name and version to your application's build file, it will look similar based on your build tool:

```shell
pip install smile-id-core
```

You now may use the classes as follows:

#### WebApi Class

Import the necessary dependant classes for Web Api:

```python
from smile_id_core import WebApi
```

##### submit_job method

Your call to the library will be similar to the below code snippet:
```python
from smile_id_core import WebApi, ServerError

connection = WebApi(
    partner_id="125", 
    call_back_url="default_callback.com", 
    api_key="<the decoded-version of-your-api-key>", 
    sid_server=0
)
partner_params = {
    "user_id": str("uuid4"),
    "job_id": str("uuid4"),
    "job_type": 1,
}
id_info_params = {
    "first_name": "FirstName",
    "middle_name": "LastName",
    "last_name": "MiddleName",
    "country": "NG",
    "id_type": "PASSPORT",
    "id_number": "A00000000",
    "dob": "1989-09-20",
    "phone_number": "",
    "entered": True,
}
image_params = [{"image_type_id": "2", "image": "base6image"}]

options_params = {
    "return_job_status": True,
    "return_history": True,
    "return_images": True,
    "signature": True,
    "use_enrolled_image": True # Perform document verification (job_type 6) for a registered user i.e. use the user’s registered selfie
}

try:
    response = connection.submit_job(partner_params, image_params, id_info_params, options_params, use_validation_api=True)
except ValueError:
    # some of your params entered for a job are not valid or missing
    print("handle ValueError")
except ServerError:
    # Server returned an error
    print("handle ServerError")
except FileNotFoundError:
    # Sent a file which could not be found
    print("handle FileNotFoundError")


```

In the case of a Job Type 5 (_Validate an ID_) you can simply omit the the image_params and options_params keys. 
Remember that the response is immediate, so there is no need to query the job_status. There is also no enrollment so no images are required. 
The response for a job type 5 can be found in the response section below.

```python
response = connection.submit_job(partner_params, None, id_info, None)
```

`use_validation_api` is optional and defaults to true. This will call the smile server and gets all required
input information for a job type and id type and checks if you  have provided required information, else it will throw an exception.

**Response:**

Should you choose to *set return_job_status to false*, the response will be a JSON String containing:
```json
{"success": true, "smile_job_id": smile_job_id}
```

However, if you have *set return_job_status to true (with image_links and history)* then you will receive JSON Object response like below:
```json
{
    "job_success": true,
    "result": {
        "ConfidenceValue": "99",
        "JSONVersion": "1.0.0",
        "Actions": {
            "Verify_ID_Number": "Verified",
            "Return_Personal_Info": "Returned",
            "Human_Review_Update_Selfie": "Not Applicable",
            "Human_Review_Compare": "Not Applicable",
            "Update_Registered_Selfie_On_File": "Not Applicable",
            "Liveness_Check": "Not Applicable",
            "Register_Selfie": "Approved",
            "Human_Review_Liveness_Check": "Not Applicable",
            "Selfie_To_ID_Authority_Compare": "Completed",
            "Selfie_To_ID_Card_Compare": "Not Applicable",
            "Selfie_To_Registered_Selfie_Compare": "Not Applicable"
        },
        "ResultText": "Enroll User",
        "IsFinalResult": "true",
        "IsMachineResult": "true",
        "ResultType": "SAIA",
        "PartnerParams": {
            "job_type": "1",
            "optional_info": "we are one",
            "user_id": "HBBBBBBH57g",
            "job_id": "HBBBBBBHg"
        },
        "Source": "WebAPI",
        "ResultCode": "0810",
        "SmileJobID": "0000001111"
    },
    "code": "2302",
    "job_complete": true,
    "signature": "HKBhxcv+1qaLy\C7PjVtk257dE=|1577b051a4313ed5e3e4d29893a66f966e31af0a2d2f6bec2a7f2e00f2701259",
    "history": [
        {
            "ConfidenceValue": "99",
            "JSONVersion": "1.0.0",
            "Actions": {
                "Verify_ID_Number": "Verified",
                "Return_Personal_Info": "Returned",
                "Human_Review_Update_Selfie": "Not Applicable",
                "Human_Review_Compare": "Not Applicable",
                "Update_Registered_Selfie_On_File": "Not Applicable",
                "Liveness_Check": "Not Applicable",
                "Register_Selfie": "Approved",
                "Human_Review_Liveness_Check": "Not Applicable",
                "Selfie_To_ID_Authority_Compare": "Completed",
                "Selfie_To_ID_Card_Compare": "Not Applicable",
                "Selfie_To_Registered_Selfie_Compare": "Not Applicable"
            },
            "ResultText": "Enroll User",
            "IsFinalResult": "true",
            "IsMachineResult": "true",
            "ResultType": "SAIA",
            "PartnerParams": {
                "job_type": "1",
                "optional_info": "we are one",
                "user_id": "HBBBBBBH57g",
                "job_id": "HBBBBBBHg"
            },
            "Source": "WebAPI",
            "ResultCode": "0810",
            "SmileJobID": "0000001111"
        }
    ],
    "image_links": {
        "selfie_image": "image_link"
    },
    "timestamp": "2019-10-10T12:32:04.622Z",
    "success": true,
    "smile_job_id": "0000001111"
}

```

You can also *view your response asynchronously at the callback* that you have set, it will look as follows:
```json
{
    "job_success": true,
    "result": {
        "ConfidenceValue": "99",
        "JSONVersion": "1.0.0",
        "Actions": {
            "Verify_ID_Number": "Verified",
            "Return_Personal_Info": "Returned",
            "Human_Review_Update_Selfie": "Not Applicable",
            "Human_Review_Compare": "Not Applicable",
            "Update_Registered_Selfie_On_File": "Not Applicable",
            "Liveness_Check": "Not Applicable",
            "Register_Selfie": "Approved",
            "Human_Review_Liveness_Check": "Not Applicable",
            "Selfie_To_ID_Authority_Compare": "Completed",
            "Selfie_To_ID_Card_Compare": "Not Applicable",
            "Selfie_To_Registered_Selfie_Compare": "Not Applicable"
        },
        "ResultText": "Enroll User",
        "IsFinalResult": "true",
        "IsMachineResult": "true",
        "ResultType": "SAIA",
        "PartnerParams": {
            "job_type": "1",
            "optional_info": "we are one",
            "user_id": "HBBBBBBH57g",
            "job_id": "HBBBBBBHg"
        },
        "Source": "WebAPI",
        "ResultCode": "0810",
        "SmileJobID": "0000001111"
    },
    "code": "2302",
    "job_complete": true,
    "signature": "HKBhxcv+1qaLy\C7PjVtk257dE=|1577b051a4313ed5e3e4d29893a66f966e31af0a2d2f6bec2a7f2e00f2701259",
    "history": [
        {
            "ConfidenceValue": "99",
            "JSONVersion": "1.0.0",
            "Actions": {
                "Verify_ID_Number": "Verified",
                "Return_Personal_Info": "Returned",
                "Human_Review_Update_Selfie": "Not Applicable",
                "Human_Review_Compare": "Not Applicable",
                "Update_Registered_Selfie_On_File": "Not Applicable",
                "Liveness_Check": "Not Applicable",
                "Register_Selfie": "Approved",
                "Human_Review_Liveness_Check": "Not Applicable",
                "Selfie_To_ID_Authority_Compare": "Completed",
                "Selfie_To_ID_Card_Compare": "Not Applicable",
                "Selfie_To_Registered_Selfie_Compare": "Not Applicable"
            },
            "ResultText": "Enroll User",
            "IsFinalResult": "true",
            "IsMachineResult": "true",
            "ResultType": "SAIA",
            "PartnerParams": {
                "job_type": "1",
                "optional_info": "we are one",
                "user_id": "HBBBBBBH57g",
                "job_id": "HBBBBBBHg"
            },
            "Source": "WebAPI",
            "ResultCode": "0810",
            "SmileJobID": "0000001111"
        }
    ],
    "image_links": {
        "selfie_image": "image_link"
    },
    "timestamp": "2019-10-10T12:32:04.622Z"
}

```

If you have queried a job type 5 (_Validate an ID_), your response be a JSON String that will contain the following:
```json
{
   "JSONVersion":"1.0.0",
   "SmileJobID":"0000001105",
   "PartnerParams":{
      "user_id":"T6yzdOezucdsPrY0QG9LYNDGOrC",
      "job_id":"FS1kd1dd15JUpd87gTBDapvFxv0",
      "job_type":5
   },
   "ResultType":"ID Verification",
   "ResultText":"ID Number Validated",
   "ResultCode":"1012",
   "IsFinalResult":"true",
   "Actions":{
      "Verify_ID_Number":"Verified",
      "Return_Personal_Info":"Returned"
   },
   "Country":"NG",
   "IDType":"PASSPORT",
   "IDNumber":"A12345",
   "ExpirationDate":"2017-10-28",
   "FullName":"John Doe",
   "DOB":"1900-09-20",
   "Photo":"SomeBase64Image",
   "sec_key":"pjxsx...",
   "timestamp":1570698930193
}
```

##### get_job_status method

Sometimes, you may want to get a particular job status at a later time. You may use the get_job_status function to do this:

You will already have your Web Api or Utilities class initialised as follows:

```python
from smile_id_core import WebApi,Utilities,ServerError
try:
    connection = WebApi("< String partner_id >", "< String default_callback_url >",
                        "< String decoded_version_of_api_key >", "< Integer 0 | | 1 >")
    # OR
    connection = Utilities("< String partner_id >", "< String default_callback_url >",
                           "< String decoded_version_of_api_key >", "< Integer 0 | | 1 >")
except ValueError:
    # some of your params entered for a job are not valid or missing
    print("handle ValueError")
# Thereafter, simply call get_job_status with the correct parameters using the classes we have provided:

# create the stringified json for the partner params using our class (i.e. user_id, job_id, and job_type that you would are querying)
partner_params = {
    "user_id": str(uuid4()),
    "job_id": str(uuid4()),
    "job_type": 1,
}
# create the options - whether you would like to return_history and return_image_links in the job status response
options_params = {
    "return_job_status": True,
    "return_history": True,
    "return_images": True,
    "signature": True # optional param to use the new signature calculation for API Key V2
}
try:
    response = connection.get_job_status(partner_params, options_params)
except ValueError:
    # some of your params entered for a job are not valid or missing
    print("handle ValueError")
except ServerError:
    # Server returned an error
    print("handle ServerError")
```

##### get_web_token method
You may want to use our hosted web integration, and create a session. The `get_web_token` function enables this.

You have your Web Api class initialised as follows:
```python
from smile_id_core import WebApi

connection = WebApi(partner_id, default_callback, api_key, sid_server);
```

Next, you'll need to create your request object. This should take the following
structure:

```json
{
	"user_id": 'user-1', // String: required
	"job_id": 'job-1', // String: required
	"product": 'authentication', // String: required one of 'authentication', 'basic_kyc', 'smartselfie', 'biometric_kyc', 'enhanced_kyc', 'document_verification'
	"callback_url": "https://smileidentity.com/callback" 	// String: required, optional if callback url was set during instantiation of the class
}
```

Thereafter, call `get_web_token` with the correct parameters:
```python
  response = connection.get_web_token(requestParams)
```

**Response**

Your response will return a promise that contains a JSON Object below:
```json
{
	"token": "<token_string>"
}
```

#### ID Api Class

An API that lets you performs basic KYC Services including verifying an ID number as well as retrieve a user's Personal Information

Import the necessary dependant classes for ID Api:

```python
from smile_id_core import IdApi, ServerError
```

##### submit_job method

Your call to the library will be similar to the below code snippet:
```python
from smile_id_core import IdApi, ServerError

partner_params = {
    "user_id": str(uuid4()),
    "job_id": str(uuid4()),
    "job_type": 5,
}

id_info_params = {
    "first_name": "FirstName",
    "middle_name": "LastName",
    "last_name": "MiddleName",
    "country": "NG",
    "id_type": "PASSPORT",
    "id_number": "A00000000",
    "dob": "1989-09-20",
    "phone_number": "",
    "entered": True,
}

option_params = {
    "signature": True # optional param to use the new signature calculation for API Key V2
}
try:
    connection = IdApi("< String partner_id >", "< String decoded_version_of_api_key >", "< Integer 0 | | 1 >")
    response = connection.submit_job(partner_params, id_info_params,option_params)
except ValueError:
    # some of your params entered for a job are not valid or missing
    print("handle ValueError")
except ServerError:
    # Server returned an error
    print("handle ServerError")
  
```
use_validation_api is optional and defaults to true this will call the smile server and gets all required
input information for a job type and id type and checks if you  have provided required information else it will throw an exception

**Response**

Your response will return a JSON String containing the below:
```json
{
   "JSONVersion":"1.0.0",
   "SmileJobID":"0000001105",
   "PartnerParams":{
      "user_id":"T6yzdOezucdsPrY0QG9LYNDGOrC",
      "job_id":"FS1kd1dd15JUpd87gTBDapvFxv0",
      "job_type":5
   },
   "ResultType":"ID Verification",
   "ResultText":"ID Number Validated",
   "ResultCode":"1012",
   "IsFinalResult":"true",
   "Actions":{
      "Verify_ID_Number":"Verified",
      "Return_Personal_Info":"Returned"
   },
   "Country":"NG",
   "IDType":"PASSPORT",
   "IDNumber":"A12345",
   "ExpirationDate":"2017-10-28",
   "FullName":"John Doe",
   "DOB":"1900-09-20",
   "Photo":"SomeBase64Image",
   "sec_key":"pjxsx...",
   "timestamp":1570698930193
}

```

#### Signature Class

##### `generate_sec_key` method

Use the Signature class as follows:
For API Key V1 (Legacy)
```python
from smile_id_core import Signature


signature = Signature("partner_id", "api_key")
signature_dict = signature.generate_sec_key(timestamp)  # where timestamp is optional
```

The response will be a dict:
```json
{
    "sec_key": "<the generated sec key>",
    "timestamp": "<timestamp that you passed in or that was generated>"
}
```
For API Key V2
```python
from smile_id_core import Signature


signature = Signature("partner_id", "api_key")
signature_dict = signature.generate_signature(timestamp)  # where timestamp is optional
```

The response will be a dict:
```json
{
    "signature": "<the generated sec key>",
    "timestamp": "<timestamp that you passed in or that was generated>"
}
```


#### Utilities Class

You may want to receive more information about a job. This is built into Web Api if you choose to set return_job_status as true in the options class. However, you also have the option to build the functionality yourself by using the Utilities class. Please note that if you are querying a job immediately after submitting it, you will need to poll it for the duration of the job.

```python
from smile_id_core import Utilities, ServerError

try:
    connection = Utilities("<partner_id>", "<the decoded-version of-your-api-key>", "<sid_server>")
    job_status = connection.get_job_status("<partner_params>", "<option_params>", "<sec_key_params>")
    print(job_status)
except ValueError:
    # some of your params entered for a job are not valid or missing
    print("handle ValueError")
except ServerError:
    # Server returned an error
    print("handle ServerError")

```

This returns the job status as stringified json data.

```python
from smile_id_core import Utilities

try:
    Utilities.validate_id_params("sid_server<0 for test or 1 for live or a string url>", "id_info_params", "partner_params", "use_validation_api=True")
except ValueError:
    # some of your params entered for a job are not valid or missing
    print("handle ValueError")

```
This will validate id parameters using the smile services endpoint which checks 
the provided user id and partner params. If use_validation_api  is  False it will only do a local
validation to check for country, id type and id number but by default this is  True and will check
against the smile services endpoint and if any key is missing will throw an exception

```python
from smile_id_core import Utilities,ServerError

try:
    Utilities.get_smile_id_services("sid_server<0 for test or 1 for live or a string url>")
except ValueError:
    # some of your params entered for a job are not valid or missing
    print("handle ValueError")
except ServerError:
    # Server returned an error
    print("handle ServerError")

```
This will return the smile services endpoint as a json object and  can then be used  for validation as per requirement

## Development

1. Ensure you have `poetry` installed: https://python-poetry.org/docs#installation
2. After checking out the repo, run `poetry install`  -- this sets up a virtualenvironment and install all required packages.
   1. Run `poetry shell` to activate the virtual environment.
   2. Run `poetry env info` to get details about the virtual environment

## Deployment

This is the https://packaging.python.org/tutorials/packaging-projects/ that you can always reference for history.

#### Testing

Tests are based on `pytest`.

If your virtual environment is active, run `poetry run pytest` from the root of the project to run the tests.

If you are outside the virtual environment, run `poetry run pytest` from the root of the project to run the tests.

#### Deployment

To release a new version:

- Bump the version number in `pyproject.toml` (the version in `smile_id_core/__init__.py` will pick this up)
- Update `changelog.md` with the new version number and the changes made
- Run `poetry build` to build package.
- Ensure your PyPI credentials are propery configured
- Run `poetry publish` to publish package.

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/smileidentity/smile-identity-core-python-3

Please format the code with [black](https://github.com/psf/black) prior to submitting pull requests, by running:
```
poetry run black .
```
from the project's root. 
