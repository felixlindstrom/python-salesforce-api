Python Salesforce API
=====================

[![Build Status](https://travis-ci.org/felixlindstrom/python-salesforce-api.svg?branch=master)](https://travis-ci.org/felixlindstrom/python-salesforce-api)

This project aims to provide an easy to use, highly flexible and testable solution for communicating with Salesforce
through its REST and SOAP api.

Content
-------

- [Simple Usage](#simple-usage)
- [Authentication](#authentication)
- [Record management](#record-management)
  - [Insert](#insert)
  - [Upsert](#upsert)
  - [Update](#update)
  - [Get](#get)
  - [Delete](#delete)
- [Quering SObjects](#querying-sobjects)
- [Bulk](#bulk)
- [Tooling](#tooling)
- [Deploying](#deploying)
- [Retrieving](#retrieving)
- [Additional features](#additional-features)


Simple usage
------------

Creating a new connection / client is as simple as this:
```python
from salesforce_api import Salesforce
client = Salesforce(
    username='test@example.com',
    password='my-password',
    security_token='password-token'
)
```

Authentication
--------------
To get started in the simples of ways, you would do the following

```python
from salesforce_api import Salesforce
client = Salesforce(username='test@example.com',
                    password='my-password',
                    security_token='password-token')
```

If you are trying to connect to a sandbox, you have to specify this using the `is_sandbox` argument.
```python
from salesforce_api import Salesforce
client = Salesforce(username='test@example.com',
                    password='my-password',
                    security_token='password-token',
                    is_sandbox=True)
```

If for some reason the login-url differs from the standard prod/test login urls, you can specify the login url. This can be useful if you are using a mock-server, for example. This will override the `is_sandbox` argument.
```python
from salesforce_api import Salesforce
client = Salesforce(username='test@example.com',
                    password='my-password',
                    security_token='password-token',
                    domain='login.example.com')
```

The examples so far would use the SOAP API for authenticating. If you want to authenticate using an app, that's easy engough. The login-url and sandbox-arguments applies here as well.
```python
from salesforce_api import Salesforce
client = Salesforce(username='test@example.com',
                    password='my-password',
                    client_id='123',
                    client_secret='my-secret')
```

If you already have an OAuth access token, obtained elsewhere, you can just as easily create a new client.
```python
from salesforce_api import Salesforce
client = Salesforce(access_token='access-token-here',
                    domain='access-token-domain')
```

If you want to explicitly use one or the other methods of authenticating, you can do that as well
```python
from salesforce_api import Salesforce, login
client = Salesforce(login.oauth2(username='test@example.com',
                                 password='my-password',
                                 client_id='123',
                                 client_secret='my-secret'))
```

If you want to use a specific version of the Salesforce API, you can specify this:
```python
from salesforce_api import Salesforce
client = Salesforce(access_token='access-token-here',
                    domain='access-token-domain',
                    api_version='51.0')
```

Record management
-----------------

Wokring with records is easy. All SObject-related methods are exposed through the `sobjects`-property on the client.

The data returned from the different calls is the decoded data from the raw response.

##### Insert
Example
```python
client.sobjects.Contact.insert({'LastName': 'Example', 'Email': 'test@example.com'})
```
Returns
```
{"id":"0031l000007rU3vAAE","success":true,"errors":[]}
```

##### Get
Example
```python
client.sobjects.Contact.get('0031l000007rU3vAAE')
```
Returns
```
{
    "attributes": {
        "type": "Contact",
        "url": "/services/data/v44.0/sobjects/Contact/0031l000007rU3vAAE"
    },
    "Id": "0031l000007rU3vAAE",
    "LastName": "Example",
    "FirstName": "Test",
    ...
}
```

##### Update
Example
```python
client.sobjects.Contact.update('0031l000007rU3vAAE', {'FirstName': 'Felix', 'LastName': 'Lindstrom'})
```
Returns
```python
True
```

##### Upsert
Example
```python
client.sobjects.Contact.upsert('customExtIdField__c', '11999', {'FirstName': 'Felix', 'LastName': 'Lindstrom'})
```
Returns
```python
True
```

##### Delete
Example
```python
client.sobjects.Contact.delete('0031l000007rU3vAAE')
```
Returns
```python
True
```

##### Metadata
Example
```python
client.sobjects.Contact.metadata()
```
Returns
```
{
    'objectDescribe': {
        'activateable': False,
        'createable': True,
        'custom': False,
        ...
        'urls': {
            'compactLayouts': '/services/data/v44.0/sobjects/Contact/describe/compactLayouts',
            'rowTemplate': '/services/data/v44.0/sobjects/Contact/{ID}',
            'approvalLayouts': '/services/data/v44.0/sobjects/Contact/describe/approvalLayouts',
            ...
        }
    },
    'recentItems': []
}
```

##### Describe
Example
```python
client.sobjects.Contact.describe()
```
Returns
```
{
    ...
}
```

Querying SObjects
-------------

The Salesforce API is great at returning large amounts of data, so the pagination that Salesforce implements for the result of your queries is taken cared of automagically when querying for data.

Example
```python
client.sobjects.query("SELECT Id, FirstName, LastName FROM Contact WHERE FirstName='Felix'")
```
Return
```
[{
    'attributes': {
        'type': 'Contact',
        'url': '/services/data/v44.0/sobjects/Contact/0031l000007Jia4AAC'
    },
    'Id': '0031l000007Jia4AAC',
    'FirstName': 'Felix',
    'LastName': 'Lindstrom'
}, ...]
``` 

Bulk
----

This module implements the Bulk V2 API. Basically, it allows you to think less and do more.

Note that the correct permission-set might be needed on the user, see https://success.salesforce.com/issues_view?id=a1p3A000000BMPFQA4

##### Bulk Insert
Example
```python
client.bulk.insert('Contact', [
    {'LastName': 'Lindstrom', 'Email': 'test@example.com'},
    {'LastName': 'Something else', 'Email': 'test@example.com'}
])
```
Returns
```python
[<SuccessResultRecord record_id="0031l000007rU5rAAE" success="True" />,
 <SuccessResultRecord record_id="0031l000007rU5sAAE" success="True" />]
```

##### Bulk Insert
Example
```python
client.bulk.insert('Contact', [
    {'LastName': 'Lindstrom', 'Email': 'test@example.com'},
    {'LastName': 'Something else', 'Email': 'test@example.com'}
])
```
Returns
```python
[<SuccessResultRecord record_id="0031l000007rU5rAAE" success="True" />,
 <SuccessResultRecord record_id="0031l000007rU5sAAE" success="True" />]
```

##### Bulk Upsert
Example
```python
client.bulk.upsert('Contact', [
    {'LastName': 'Lindstrom', 'Email': 'test@example.com', 'MyId__c': 1},
    {'LastName': 'Something else', 'Email': 'test@example.com', 'MyId__c': 2}
], external_id_field='MyId__c')
```
Returns
```python
[<SuccessResultRecord record_id="0031l000007rU5rAAE" success="True" />,
 <SuccessResultRecord record_id="0031l000007rU5sAAE" success="True" />]
```

##### Bulk Update
Example
```python
client.bulk.update('Contact', [
    {'LastName': 'Lindstrom', 'Email': 'test@example.com'},
    {'LastName': 'Something else', 'Email': 'test@example.com'}
])
```
Returns
```python
[<SuccessResultRecord record_id="0031l000007rU5rAAE" success="True" />,
 <SuccessResultRecord record_id="0031l000007rU5sAAE" success="True" />]
```

##### Bulk Delete
Example
```python
client.bulk.delete('Contact', ['0031l000007rU5rAAE', '0031l000007rU5sAAE'])
```
Returns
```python
[<SuccessResultRecord record_id="0031l000007rU5rAAE" success="True" />,
 <SuccessResultRecord record_id="0031l000007rU5sAAE" success="True" />]
```

##### Failed requests
Example (_Given that the records no longer exists_)
```python
client.bulk.update('Contact', ['0031l000007rU5rAAE', '0031l000007rU5sAAE'])
```
Returns
```python
[<FailResultRecord record_id="0031l000007rU5rAAE" success="False" error="ENTITY_IS_DELETED:entity is deleted:--" />,
 <FailResultRecord record_id="0031l000007rU5sAAE" success="False" error="ENTITY_IS_DELETED:entity is deleted:--" />]
```

##### Manual managing bulk job
By using the api above, the library hides the uploading and waiting for the bulk-process to get processed.

In some cases you might want to handle this differently. Perhaps you want to upload bunch of records to be inserted and then forget about the process. This can be done by creating a job and managing it by yourself.
```python
bulk_job = client.bulk.create_job(OPERATION.INSERT, 'Contact')
bulk_job.upload([
    {'LastName': 'Lindstrom', 'Email': 'test@example.com'},
    {'LastName': 'Something else', 'Email': 'test@example.com'}
])
while not bulk_job.is_done():
    time.sleep(5)
```

Tooling
-------

##### Execute Apex
Example
```python
client.tooling.execute_apex("System.debug('Test');")
```
Return on success
```python
<SuccessfulApexExecutionResult line="-1" column="-1" compiled="True" success="True" compile_problem="None" exception_stack_trace="None" exception_message="None" />
```
Return on failure
```
<FailedApexExecutionResult line="1" column="13" compiled="False" success="False" compile_problem="Unexpected token '('." exception_stack_trace="None" exception_message="None" />
```

Deploying
---------
Deploying an existing package
```python
from salesforce_api.models.deploy import Options


deployment = client.deploy.deploy('/path/to/file.zip')
deployment.wait()
result = deployment.get_status()

```

Only validating
```python
from salesforce_api.models.deploy import Options


deployment = client.deploy.deploy('/path/to/file.zip', Options(checkOnly=True))
deployment.wait()
result = deployment.get_status()

```

Validating running specific tests
```python
from salesforce_api.models.deploy import Options


deployment = client.deploy.deploy('/path/to/file.zip', Options(
    checkOnly=True,
    testLevel='RunSpecifiedTests',
    runTests=[
        'TesterIntegrationApplicationTest',
        'TesterIntegrationProcessTest'
    ]
))
deployment.wait()
result = deployment.get_status()
```

Canceling a deployment as soon as it fails
```python
from salesforce_api.models.deploy import Options


deployment = client.deploy.deploy('/path/to/file.zip', Options(checkOnly=True))

while not deployment.is_done():
    if deployment.has_failed():
        deployment.cancel()
        break

```

Retrieving
----------
Example
```python
from salesforce_api.models.shared import Type


# Decide what you want to retrieve
types = [
    Type('ApexTrigger'),
    Type('ApexClass', ['MyMainClass', 'AnotherClass'])
]

# Create retrievement-job
retrievement = client.retrieve.retrieve(types)

# Wait for the job to finish
retrievement.wait()

# Write the resulting zip-archive to a file
open('retrieve.zip', 'wb').write(retrievement.get_zip_file().read())
```

Additional features
-------------------

If for some reason you need to specify how the client communicates with Salesforce, you can create the requests-session yourself and pass it to the client upon creation. This would, for example, allow you proxy your requests:
```python
import requests
from salesforce_api import Salesforce


session = requests.Session()
session.proxies.update({'https': 'https://my-proxy.com/'})
session.headers.update({'User-Agent': 'My-User-Agent'})

client = Salesforce(username='test@example.com',
                    password='my-password',
                    security_token='password-token',
                    session=session)
```