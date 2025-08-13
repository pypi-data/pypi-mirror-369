# SolveXia Process Automation SDK for Python
[SolveXia Python SDK](https://pypi.org/project/solvexia-sdk/) exists to help create faster and easier integration with SolveXia APIs. 

## Getting started

Any application that is intended to access SolveXia Public API must have authorization credentials that identify the application to SolveXia authorization server.

### Create authorization credentials for you app

1. Navigate to SolveXia API portal from the user dropdown menu.
2. Click "Create new application".
3. Specify the name and callback URL. Click "Create application".
4. If the creation is successful you will see Client Id and Client Secret credentials generated.
5. Copy credentials and store them safely. You will not be able to see Client Secret again unless you generate a new one.
6. Scopes are needed to be set up. To read more about scopes please see [solvexia-api-docs](https://github.com/solvexia/solvexia-api-docs/blob/master/oauth/oauth-scopes.md).

## Install package

```shell
pip3 install solvexia-sdk
```

If you keep to use the latest or any other specific version of the package checkout this repo desired version and run

```shell
python setup.py install
```

### Install SDK from GitHub
An alternative way to install the SDK is to download all the necessary files as a zip from GitHub.

### Creating JSON Authentication File

1. Recall your previously saved client_id, client_secret and scopes
2. Store this information in a JSON file with the following structure along with the environment you are using:
```python
{"client_id": clientId, "client_secret": clientSecret, "env": solvexiaEnvPrefix, "scope": scopes}
```
3. Save this file in the root directory (directory that contains the solvexia_sdk folder).

Note: `solvexiaEnvPrefix` is a prefix of the SolveXia environment you are working with. For example, 
for https://app.solvexia.com the `solvexiaEnvPrefix` will be `app`.

### Importing OAuth Function and Generating an Access Token
SolveXia uses OAuth2.0 as a secure method to generate access tokens for clients so that they can access and use SolveXia's
API calls. Therefore, before we can use any of the functions within the SDK, we must first generate an access token using
our client_id and client_secret. By using the JSON file we created earlier, we can import the api.py file as shown below
to access the solvexia_client class which contains the access token generation functions.

```python
from solvexia_sdk import api
```

We then need to initalise the solvexia_client class by passing the JSON file we created earlier.


```python
client = api.solvexiaClient("JSONFileName")
```

Note: client is just a variable name that represents the initialised solvexiaClient class.

Once our solvexiaClient class has been initialised, we can now generate our access token by calling the get_access_token function.

E.g. Calling the getAccessToken function within the solvexia_client class
```python
client.get_access_token()
```

If no errors are raised, we have now successfully generated our access token and are free to use all the other functions and
API calls within this SDK until the token expires.

### Importing API SDK Files

Within this SDK, SolveXia's API calls are separated into groups based on the type of object they operate on, e.g. datasteps,
process, file, etc.

The first thing we need to do to access these functions is to import them over to our file.
We can do this by following the general syntax:
```python
from solvexia_sdk.foldername import python_file
```
E.g. To import the file API calls and class that are found in the file.py file in the file directory, we do:
```python
from solvexia_sdk.file import file
```

### Initialising Classes

After importing an API SDK file, we must initialise the class specified within that particular file before we can access the
class functions. Make sure to take note of what variable we need to pass in during class initialisation by looking at the 
arguments (besides self) within the class __init__ function.
To do this, we can follow the following general syntax:
```python
classNameVar = fileName.className(anyArgs)
```
E.g. To initialise the file class within file.py, we need to pass in a fileId.
```python
fileClass = file.file("f-5922731")
```

### Calling the Functions within a Class
Now that the class has been initialised, we are free to access any of the functions within that class. The generic
code to do this is as follows:
```python
retObj = classNameVar.class_function(anyArgs)
```
Since most of the functions within this SDK will return a JSON object, generally we want to store that in a variable
so that we can access this information (retObj).

E.g. Calling the getFileMetadata function with an initialised file class called fileClass and storing the response in a 
variable called response.
```python
response = fileClass.get_file_metadata()
```

Reminder: Ensure that for any of the object classes, we must always initialise the class first before we can call 
any functions from within the class.

### Return Value of API Functions
A majority of the API call functions within this SDK will return a JSON object specific to the object. These JSON objects
and their format are explained in depth in SolveXia's API docs.
An alternative to see the structure of the returned JSON object is to print the JSON object that is returned to stdout.

### Additional Arguments for Functions
Some API function calls within this SDK have additional arguments that must be passed through. In most cases, these are 
either additional ids, an object instance or file/filepath.

### Structure of Object Instance Docs
[File Objects](https://github.com/solvexia/solvexia-api-docs/blob/master/file/file_schemas.md/#upload-session)  
[Process Run Objects](https://github.com/solvexia/solvexia-api-docs/blob/master/process_runs/process_runs_schemas.md)  
[Process Objects](https://github.com/solvexia/solvexia-api-docs/blob/master/processes/schemas.md)  
[Datasteps Objects](https://github.com/solvexia/solvexia-api-docs/blob/master/steps/datastep_schemas.md)  
[Table Objects](https://github.com/solvexia/solvexia-api-docs/blob/master/tables/tables_schemas.md)  

### Example of Uploading and Downloading a File
```python
from solvexia_sdk import api
from solvexia_sdk.file import file

client = api.solvexiaClient("auth.json")
client.get_access_token()
fileTest = file.file("f-5940022")
fileTest.upload_file("uploadFile.csv")
response = fileTest.download_file()
with open("output.csv", "wb") as f:
    f.write(response.content)
```

### Example of Uploading a File Using 25MB Chunks and Downloading
```python
from solvexia_sdk import api
from solvexia_sdk.file import file

client = api.solvexiaClient("auth.json")
client.get_access_token()
fileTest = file.file("f-5940022")
fileTest.upload_file_by_chunks(25000000, "uploadFile.csv")
response = fileTest.download_file()
with open("output.csv", "wb") as f:
    f.write(response.content)
```

### Example of Creating a Process Run and Running it
```python
from solvexia_sdk import api
from solvexia_sdk.process import process
from solvexia_sdk.processrun import processrun

client = api.solvexiaClient("auth.json")
client.get_access_token()
processTest = process.process("p-37817")
response = processTest.create_process_run("newProcessRun")
processRunTest = processrun.processRuns(response["id"])
processRunTest.start_process_run()

```  

### How to push to PyPI

1. Ensure that all the packages you wish to include are included in the packages line in the setup.py file
2. Update the version number in the setup.py if package has already been uploaded to PyPI before and you just wish to update it
3. Install twine using `pip3 install twine`
4. Build the package by running the command: `python3 setup.py sdist bdist_wheel`
5. You can upload to TestPyPI to ensure everything works using: `twine upload --repository testpypi dist/*`
5. Upload the package to the official PyPI using twine: `twine upload dist/*`
6. Both times, you will be asked to enter your PyPI username and password

## Issues

Please raise all issues associated with this package [here](https://github.com/solvexia/solvexia-python-sdk/issues). 
The more information you provide in the description, the faster we are able to address it.

## License

GNU General Public License v3.0 or later.