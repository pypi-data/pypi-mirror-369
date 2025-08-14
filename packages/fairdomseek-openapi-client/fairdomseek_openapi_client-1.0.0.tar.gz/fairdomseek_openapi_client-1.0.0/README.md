# Disclaimer

This client has been automatically generated from fairdomseek openapi file definition as following:

```
docker run --rm -v .:/local openapitools/openapi-generator-cli generate -i /local/openapi.yaml -g python -o /local/fairdomseekapiclient

```

# openapi-client
<a name=\"api\"></a>The JSON API to FAIRDOM SEEK is a [JSON API](http://jsonapi.org) specification describing how to read and write to a SEEK instance.

The API is defined in the [OpenAPI specification](https://swagger.io/specification) currently in [version 2](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md)

Example IPython notebooks showing use of the API are available on [GitHub](https://github.com/FAIRdom/api-workshop)

## Policy
<a name=\"Policy\"></a>
A Policy specifies the visibility of an object to people using SEEK. A <a href=\"#projects\">**Project**</a> may specify the default policy for objects belonging to that <a href=\"#projects\">**Project**</a>

The **Policy** specifies the visibility of the object to non-registered people or <a href=\"#people\">**People**</a> not allowed special access.

The access may be one of (in order of increasing \"power\"):

* no_access
* view
* download
* edit
* manage

In addition a **Policy** may give special access to specific <a href=\"#people\">**People**</a>, People working at an <a href=\"#institutions\">**Institution**</a> or working on a <a href=\"#projects\">**Project**</a>.

## License
<a name=\"License\"></a>
The license specifies the license that will apply to any <a href=\"#dataFiles\">**DataFiles**</a>, <a href=\"#models\">**Models**</a>, <a href=\"#sops\">**SOPs**</a>, <a href=\"#documents\">**Documents**</a> and <a href=\"#presentations\">**Presentations**</a> associated with a <a href=\"#projects\">**Project**</a>.

The license can currently be:

* `CC0-1.0` - [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/)
* `CC-BY-4.0` - [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)
* `CC-BY-SA-4.0` - [Creative Commons Attribution Share-Alike 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
* `ODC-BY-1.0` - [Open Data Commons Attribution License 1.0](http://www.opendefinition.org/licenses/odc-by)
* `ODbL-1.0` - [Open Data Commons Open Database License 1.0](http://www.opendefinition.org/licenses/odc-odbl)
* `ODC-PDDL-1.0` - [Open Data Commons Public Domain Dedication and Licence 1.0](http://www.opendefinition.org/licenses/odc-pddl)
* `notspecified` - License Not Specified
* `other-at` - Other (Attribution)
* `other-open` - Other (Open)
* `other-pd` - Other (Public Domain)
* `AFL-3.0` - [Academic Free License 3.0](http://www.opensource.org/licenses/AFL-3.0)
* `Against-DRM` - [Against DRM](http://www.opendefinition.org/licenses/against-drm)
* `CC-BY-NC-4.0` - [Creative Commons Attribution-NonCommercial 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
* `DSL` - [Design Science License](http://www.opendefinition.org/licenses/dsl)
* `FAL-1.3` - [Free Art License 1.3](http://www.opendefinition.org/licenses/fal)
* `GFDL-1.3-no-cover-texts-no-invariant-sections` - [GNU Free Documentation License 1.3 with no cover texts and no invariant sections](http://www.opendefinition.org/licenses/gfdl)
* `geogratis` - [Geogratis](http://geogratis.gc.ca/geogratis/licenceGG)
* `hesa-withrights` - [Higher Education Statistics Agency Copyright with data.gov.uk rights](http://www.hesa.ac.uk/index.php?option=com_content&amp;task=view&amp;id=2619&amp;Itemid=209)
* `localauth-withrights` - Local Authority Copyright with data.gov.uk rights
* `MirOS` - [MirOS Licence](http://www.opensource.org/licenses/MirOS)
* `NPOSL-3.0` - [Non-Profit Open Software License 3.0](http://www.opensource.org/licenses/NPOSL-3.0)
* `OGL-UK-1.0` - [Open Government Licence 1.0 (United Kingdom)](http://reference.data.gov.uk/id/open-government-licence)
* `OGL-UK-2.0` - [Open Government Licence 2.0 (United Kingdom)](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/)
* `OGL-UK-3.0` - [Open Government Licence 3.0 (United Kingdom)](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
* `OGL-Canada-2.0` - [Open Government License 2.0 (Canada)](http://data.gc.ca/eng/open-government-licence-canada)
* `OSL-3.0` - [Open Software License 3.0](http://www.opensource.org/licenses/OSL-3.0)
* `dli-model-use` - [Statistics Canada: Data Liberation Initiative (DLI) - Model Data Use Licence](http://data.library.ubc.ca/datalib/geographic/DMTI/license.html)
* `Talis` - [Talis Community License](http://www.opendefinition.org/licenses/tcl)
* `ukclickusepsi` - UK Click Use PSI
* `ukcrown-withrights` - UK Crown Copyright with data.gov.uk rights
* `ukpsi` - [UK PSI Public Sector Information](http://www.opendefinition.org/licenses/ukpsi)

## ContentBlob
<a name=\"ContentBlob\"></a>
<a name=\"contentBlobs\"></a>
The content of a <a href=\"#dataFiles\">**DataFile**</a>, <a href=\"#documents\">**Document**</a>, <a href=\"#models\">**Model**</a>, <a href=\"#sops\">**SOP**</a> or <a href=\"#presentations\">**Presentation**</a> is specified as a set of **ContentBlobs**.

When a resource with content is created, it is possible to specify a ContentBlob either as:

* A remote ContentBlob with:
  * **URI to the content's location**
  * The original filename for the content
  * The content type of the remote content as a [MIME media type](https://en.wikipedia.org/wiki/Media_type)
* A placeholder that will be filled with uploaded content
  * **The original filename for the content**
  * **The content type of the content as a [MIME media type](https://en.wikipedia.org/wiki/Media_type)**

The creation of the resource will return a JSON document containing ContentBlobs corresponding to the remote ContentBlob and to the ContentBlob placeholder. The blobs contain a URI to their location.

A placeholder can then be satisfied by uploading a file to the location URI. For example by a placeholder such as 

```
\"content_blobs\": [
  {
    \"original_filename\": \"a_pdf_file.pdf\",
    \"content_type\": \"application/pdf\",
    \"link\": \"http://fairdomhub.org/data_files/57/content_blobs/313\"
  }
],
```

may be satisfied by uploading a file to http://fairdomhub.org/data_files/57/content_blobs/313 using the <a href=\"#uploadAssetContent\">uploadAssetContent</a> operation

The content of a resource may be downloaded by first *reading* the resource and then *downloading* the ContentBlobs from their URI.

## Extended Metadata

Some types support [Extended Metadata](https://docs.seek4science.org/tech/extended-metadata), which allows additional attributes to be defined according to an Extended Metadata Type.

Types currently supported are <a href=\"#investigations\">**Investigation**</a>, <a href=\"#studies\">**Study**</a>, <a href=\"#assays\">**Assay**</a>, 
<a href=\"#dataFiles\">**DataFile**</a>, <a href=\"#sops\">**SOP**</a>, <a href=\"#presentations\">**Presentation**</a>,
<a href=\"#documents\">**Document**</a>, <a href=\"#models\">**Model**</a>,
<a href=\"#events\">**Event**</a>, <a href=\"#collections\">**Collection**</a>, <a href=\"#projects\">**Project**</a>

The responses and requests for each of these types include an additional optional attribute _extended_attributes_ which describes

* _extended_metadata_type_id_ - the id of the extended metadata type which can be used to find more details about what its attributes are.
* _attribute_map_ - which is a map of key / value pairs where the key is the attribute name


For example, a Study may have extended metadata, defined by an Extended Metadata Type with id 12, that has attributes for
age, name, and date_of_birth. These could be shown, within its attributes, as:

```
\"extended_attributes\": {
  \"extended_metadata_type_id\": \"12\",
  \"attribute_map\": {
    \"age\": 44,
    \"name\": \"Fred Bloggs\",
    \"date_of_birth\": \"2024-01-01\"
  }
}
```

If you wish to create or update a study to make use of this extended metadata, the request payload would be described the same. 
Upon creation or update there would be a validation check that the attributes are valid.

The API supports listing all available Extended Metadata Types, and inspecting an individual type by its id. For more information see the [Extended Metadata Type definitions](api#tag/extendedMetadataTypes).

This Python package is automatically generated by the [OpenAPI Generator](https://openapi-generator.tech) project:

- API version: 0.3
- Package version: 1.0.0
- Generator version: 7.14.0-SNAPSHOT
- Build package: org.openapitools.codegen.languages.PythonClientCodegen
For more information, please visit [http://groups.google.com/group/seek4science](http://groups.google.com/group/seek4science)

## Requirements.

Python 3.9+

## Installation & Usage
### pip install

If the python package is hosted on a repository, you can install directly using:

```sh
pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git
```
(you may need to run `pip` with root permission: `sudo pip install git+https://github.com/GIT_USER_ID/GIT_REPO_ID.git`)

Then import the package:
```python
import openapi_client
```

### Setuptools

Install via [Setuptools](http://pypi.python.org/pypi/setuptools).

```sh
python setup.py install --user
```
(or `sudo python setup.py install` to install the package for all users)

Then import the package:
```python
import openapi_client
```

### Tests

Execute `pytest` to run the tests.

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

```python

import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to https://fairdomhub.org
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "https://fairdomhub.org"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Configure API key authorization: apiToken
configuration.api_key['apiToken'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['apiToken'] = 'Bearer'

# Configure HTTP basic authorization: basicAuth
configuration = openapi_client.Configuration(
    username = os.environ["USERNAME"],
    password = os.environ["PASSWORD"]
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.AssaysApi(api_client)
    assay_post = openapi_client.AssayPost() # AssayPost | The assay to create. (optional)

    try:
        # Create a new assay
        api_response = api_instance.create_assay(assay_post=assay_post)
        print("The response of AssaysApi->create_assay:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling AssaysApi->create_assay: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *https://fairdomhub.org*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*AssaysApi* | [**create_assay**](docs/AssaysApi.md#create_assay) | **POST** /assays | Create a new assay
*AssaysApi* | [**delete_assay**](docs/AssaysApi.md#delete_assay) | **DELETE** /assays/{id} | Delete an assay
*AssaysApi* | [**list_assays**](docs/AssaysApi.md#list_assays) | **GET** /assays | List assays
*AssaysApi* | [**read_assay**](docs/AssaysApi.md#read_assay) | **GET** /assays/{id} | Fetch an assay
*AssaysApi* | [**update_assay**](docs/AssaysApi.md#update_assay) | **PATCH** /assays/{id} | Update an assay
*CollectionsApi* | [**create_collection**](docs/CollectionsApi.md#create_collection) | **POST** /collections | Create a new collection
*CollectionsApi* | [**create_collection_item**](docs/CollectionsApi.md#create_collection_item) | **POST** /collections/{collection_id}/items | Add a new item to a collection
*CollectionsApi* | [**delete_collection**](docs/CollectionsApi.md#delete_collection) | **DELETE** /collections/{id} | Delete a collection
*CollectionsApi* | [**delete_collection_item**](docs/CollectionsApi.md#delete_collection_item) | **DELETE** /collections/{collection_id}/items/{id} | Remove an item from a collection
*CollectionsApi* | [**list_collection_items**](docs/CollectionsApi.md#list_collection_items) | **GET** /collections/{collection_id}/items | List translation items in a collection
*CollectionsApi* | [**list_collections**](docs/CollectionsApi.md#list_collections) | **GET** /collections | List collections
*CollectionsApi* | [**read_collection**](docs/CollectionsApi.md#read_collection) | **GET** /collections/{id} | Fetch a collection
*CollectionsApi* | [**read_collection_item**](docs/CollectionsApi.md#read_collection_item) | **GET** /collections/{collection_id}/items/{id} | Fetch an item from a collection
*CollectionsApi* | [**update_collection**](docs/CollectionsApi.md#update_collection) | **PATCH** /collections/{id} | Update a collection
*CollectionsApi* | [**update_collection_item**](docs/CollectionsApi.md#update_collection_item) | **PATCH** /collections/{collection_id}/items/{id} | Update an item in a collection
*ContentBlobsApi* | [**download_asset_content**](docs/ContentBlobsApi.md#download_asset_content) | **GET** /{asset_types}/{id}/content_blobs/{blob_id}/download | Download content
*ContentBlobsApi* | [**read_content_blob**](docs/ContentBlobsApi.md#read_content_blob) | **GET** /{asset_types}/{id}/content_blobs/{blob_id} | Fetch information on a content blob
*ContentBlobsApi* | [**upload_asset_content**](docs/ContentBlobsApi.md#upload_asset_content) | **PUT** /{asset_types}/{id}/content_blobs/{blob_id} | Upload content to an existing content blob placeholder
*CreateApi* | [**create_assay**](docs/CreateApi.md#create_assay) | **POST** /assays | Create a new assay
*CreateApi* | [**create_collection**](docs/CreateApi.md#create_collection) | **POST** /collections | Create a new collection
*CreateApi* | [**create_collection_item**](docs/CreateApi.md#create_collection_item) | **POST** /collections/{collection_id}/items | Add a new item to a collection
*CreateApi* | [**create_data_file**](docs/CreateApi.md#create_data_file) | **POST** /data_files | Create a new data file
*CreateApi* | [**create_document**](docs/CreateApi.md#create_document) | **POST** /documents | Create a new document
*CreateApi* | [**create_event**](docs/CreateApi.md#create_event) | **POST** /events | Create a new event
*CreateApi* | [**create_institution**](docs/CreateApi.md#create_institution) | **POST** /institutions | Create a new institution
*CreateApi* | [**create_investigation**](docs/CreateApi.md#create_investigation) | **POST** /investigations | Create a new investigation
*CreateApi* | [**create_model**](docs/CreateApi.md#create_model) | **POST** /models | Create a new model
*CreateApi* | [**create_person**](docs/CreateApi.md#create_person) | **POST** /people | Create a new person
*CreateApi* | [**create_presentation**](docs/CreateApi.md#create_presentation) | **POST** /presentations | Create a new presentation
*CreateApi* | [**create_programme**](docs/CreateApi.md#create_programme) | **POST** /programmes | Create a new programme
*CreateApi* | [**create_project**](docs/CreateApi.md#create_project) | **POST** /projects | Create a new project
*CreateApi* | [**create_sample**](docs/CreateApi.md#create_sample) | **POST** /samples | Create a new sample
*CreateApi* | [**create_sample_type**](docs/CreateApi.md#create_sample_type) | **POST** /sample_types | Create a new sample type
*CreateApi* | [**create_sop**](docs/CreateApi.md#create_sop) | **POST** /sops | Create a new sop
*CreateApi* | [**create_study**](docs/CreateApi.md#create_study) | **POST** /studies | Create a new study
*CreateApi* | [**create_workflow**](docs/CreateApi.md#create_workflow) | **POST** /workflows | Create a new workflow
*DataFilesApi* | [**create_data_file**](docs/DataFilesApi.md#create_data_file) | **POST** /data_files | Create a new data file
*DataFilesApi* | [**delete_data_file**](docs/DataFilesApi.md#delete_data_file) | **DELETE** /data_files/{id} | Delete a data file
*DataFilesApi* | [**list_data_files**](docs/DataFilesApi.md#list_data_files) | **GET** /data_files | List data files
*DataFilesApi* | [**read_data_file**](docs/DataFilesApi.md#read_data_file) | **GET** /data_files/{id} | Fetch a data file
*DataFilesApi* | [**update_data_file**](docs/DataFilesApi.md#update_data_file) | **PATCH** /data_files/{id} | Update a data file
*DeleteApi* | [**delete_assay**](docs/DeleteApi.md#delete_assay) | **DELETE** /assays/{id} | Delete an assay
*DeleteApi* | [**delete_collection**](docs/DeleteApi.md#delete_collection) | **DELETE** /collections/{id} | Delete a collection
*DeleteApi* | [**delete_collection_item**](docs/DeleteApi.md#delete_collection_item) | **DELETE** /collections/{collection_id}/items/{id} | Remove an item from a collection
*DeleteApi* | [**delete_data_file**](docs/DeleteApi.md#delete_data_file) | **DELETE** /data_files/{id} | Delete a data file
*DeleteApi* | [**delete_document**](docs/DeleteApi.md#delete_document) | **DELETE** /documents/{id} | Delete a document
*DeleteApi* | [**delete_event**](docs/DeleteApi.md#delete_event) | **DELETE** /events/{id} | Delete an event
*DeleteApi* | [**delete_institution**](docs/DeleteApi.md#delete_institution) | **DELETE** /institutions/{id} | Delete an institution
*DeleteApi* | [**delete_investigation**](docs/DeleteApi.md#delete_investigation) | **DELETE** /investigations/{id} | Delete an investigation
*DeleteApi* | [**delete_model**](docs/DeleteApi.md#delete_model) | **DELETE** /models/{id} | Delete a model
*DeleteApi* | [**delete_person**](docs/DeleteApi.md#delete_person) | **DELETE** /people/{id} | Delete a person
*DeleteApi* | [**delete_presentation**](docs/DeleteApi.md#delete_presentation) | **DELETE** /presentations/{id} | Delete a presentation
*DeleteApi* | [**delete_programme**](docs/DeleteApi.md#delete_programme) | **DELETE** /programmes/{id} | Delete a programme
*DeleteApi* | [**delete_project**](docs/DeleteApi.md#delete_project) | **DELETE** /projects/{id} | Delete a project
*DeleteApi* | [**delete_sample**](docs/DeleteApi.md#delete_sample) | **DELETE** /samples/{id} | Delete a sample
*DeleteApi* | [**delete_sample_type**](docs/DeleteApi.md#delete_sample_type) | **DELETE** /sample_types/{id} | Delete a sample type
*DeleteApi* | [**delete_sop**](docs/DeleteApi.md#delete_sop) | **DELETE** /sops/{id} | Delete a sop
*DeleteApi* | [**delete_study**](docs/DeleteApi.md#delete_study) | **DELETE** /studies/{id} | Delete a study
*DeleteApi* | [**delete_workflow**](docs/DeleteApi.md#delete_workflow) | **DELETE** /workflows/{id} | Delete a workflow
*DocumentsApi* | [**create_document**](docs/DocumentsApi.md#create_document) | **POST** /documents | Create a new document
*DocumentsApi* | [**delete_document**](docs/DocumentsApi.md#delete_document) | **DELETE** /documents/{id} | Delete a document
*DocumentsApi* | [**list_documents**](docs/DocumentsApi.md#list_documents) | **GET** /documents | List documents
*DocumentsApi* | [**read_document**](docs/DocumentsApi.md#read_document) | **GET** /documents/{id} | Fetch a document
*DocumentsApi* | [**update_document**](docs/DocumentsApi.md#update_document) | **PATCH** /documents/{id} | Update a document
*DownloadApi* | [**download_asset_content**](docs/DownloadApi.md#download_asset_content) | **GET** /{asset_types}/{id}/content_blobs/{blob_id}/download | Download content
*EventsApi* | [**create_event**](docs/EventsApi.md#create_event) | **POST** /events | Create a new event
*EventsApi* | [**delete_event**](docs/EventsApi.md#delete_event) | **DELETE** /events/{id} | Delete an event
*EventsApi* | [**list_events**](docs/EventsApi.md#list_events) | **GET** /events | List events
*EventsApi* | [**read_event**](docs/EventsApi.md#read_event) | **GET** /events/{id} | Fetch an event
*EventsApi* | [**update_event**](docs/EventsApi.md#update_event) | **PATCH** /events/{id} | Update an event
*ExtendedMetadataTypesApi* | [**list_extended_metadata_types**](docs/ExtendedMetadataTypesApi.md#list_extended_metadata_types) | **GET** /extended_metadata_types | List extended metadata types
*ExtendedMetadataTypesApi* | [**read_extended_metadata_type**](docs/ExtendedMetadataTypesApi.md#read_extended_metadata_type) | **GET** /extended_metadata_types/{id} | Fetch an extended metadata type
*InstitutionsApi* | [**create_institution**](docs/InstitutionsApi.md#create_institution) | **POST** /institutions | Create a new institution
*InstitutionsApi* | [**delete_institution**](docs/InstitutionsApi.md#delete_institution) | **DELETE** /institutions/{id} | Delete an institution
*InstitutionsApi* | [**list_institutions**](docs/InstitutionsApi.md#list_institutions) | **GET** /institutions | List institutions
*InstitutionsApi* | [**read_institution**](docs/InstitutionsApi.md#read_institution) | **GET** /institutions/{id} | Fetch an institution
*InstitutionsApi* | [**update_institution**](docs/InstitutionsApi.md#update_institution) | **PATCH** /institutions/{id} | Update an institution
*InvestigationsApi* | [**create_investigation**](docs/InvestigationsApi.md#create_investigation) | **POST** /investigations | Create a new investigation
*InvestigationsApi* | [**delete_investigation**](docs/InvestigationsApi.md#delete_investigation) | **DELETE** /investigations/{id} | Delete an investigation
*InvestigationsApi* | [**list_investigations**](docs/InvestigationsApi.md#list_investigations) | **GET** /investigations | List investigations
*InvestigationsApi* | [**read_investigation**](docs/InvestigationsApi.md#read_investigation) | **GET** /investigations/{id} | Fetch an investigation
*InvestigationsApi* | [**update_investigation**](docs/InvestigationsApi.md#update_investigation) | **PATCH** /investigations/{id} | Update an investigation
*ListApi* | [**list_assays**](docs/ListApi.md#list_assays) | **GET** /assays | List assays
*ListApi* | [**list_collection_items**](docs/ListApi.md#list_collection_items) | **GET** /collections/{collection_id}/items | List translation items in a collection
*ListApi* | [**list_collections**](docs/ListApi.md#list_collections) | **GET** /collections | List collections
*ListApi* | [**list_data_files**](docs/ListApi.md#list_data_files) | **GET** /data_files | List data files
*ListApi* | [**list_documents**](docs/ListApi.md#list_documents) | **GET** /documents | List documents
*ListApi* | [**list_events**](docs/ListApi.md#list_events) | **GET** /events | List events
*ListApi* | [**list_extended_metadata_types**](docs/ListApi.md#list_extended_metadata_types) | **GET** /extended_metadata_types | List extended metadata types
*ListApi* | [**list_institutions**](docs/ListApi.md#list_institutions) | **GET** /institutions | List institutions
*ListApi* | [**list_investigations**](docs/ListApi.md#list_investigations) | **GET** /investigations | List investigations
*ListApi* | [**list_models**](docs/ListApi.md#list_models) | **GET** /models | List models
*ListApi* | [**list_organisms**](docs/ListApi.md#list_organisms) | **GET** /organisms | List organisms
*ListApi* | [**list_people**](docs/ListApi.md#list_people) | **GET** /people | List people
*ListApi* | [**list_presentations**](docs/ListApi.md#list_presentations) | **GET** /presentations | List presentations
*ListApi* | [**list_programmes**](docs/ListApi.md#list_programmes) | **GET** /programmes | List programmes
*ListApi* | [**list_projects**](docs/ListApi.md#list_projects) | **GET** /projects | List projects
*ListApi* | [**list_publications**](docs/ListApi.md#list_publications) | **GET** /publications | List publications
*ListApi* | [**list_sample_attribute_types**](docs/ListApi.md#list_sample_attribute_types) | **GET** /sample_attribute_types | List possible sample attribute types
*ListApi* | [**list_sample_types**](docs/ListApi.md#list_sample_types) | **GET** /sample_types | List sample types
*ListApi* | [**list_sops**](docs/ListApi.md#list_sops) | **GET** /sops | List sops
*ListApi* | [**list_studies**](docs/ListApi.md#list_studies) | **GET** /studies | List studies
*ListApi* | [**list_workflows**](docs/ListApi.md#list_workflows) | **GET** /workflows | List workflows
*ModelsApi* | [**create_model**](docs/ModelsApi.md#create_model) | **POST** /models | Create a new model
*ModelsApi* | [**delete_model**](docs/ModelsApi.md#delete_model) | **DELETE** /models/{id} | Delete a model
*ModelsApi* | [**list_models**](docs/ModelsApi.md#list_models) | **GET** /models | List models
*ModelsApi* | [**read_model**](docs/ModelsApi.md#read_model) | **GET** /models/{id} | Fetch a model
*ModelsApi* | [**update_model**](docs/ModelsApi.md#update_model) | **PATCH** /models/{id} | Update a model
*OrganismsApi* | [**list_organisms**](docs/OrganismsApi.md#list_organisms) | **GET** /organisms | List organisms
*OrganismsApi* | [**read_organism**](docs/OrganismsApi.md#read_organism) | **GET** /organisms/{id} | Fetch an organism
*PeopleApi* | [**create_person**](docs/PeopleApi.md#create_person) | **POST** /people | Create a new person
*PeopleApi* | [**current_person**](docs/PeopleApi.md#current_person) | **GET** /people/current | Fetch the currently authenticated user
*PeopleApi* | [**delete_person**](docs/PeopleApi.md#delete_person) | **DELETE** /people/{id} | Delete a person
*PeopleApi* | [**list_people**](docs/PeopleApi.md#list_people) | **GET** /people | List people
*PeopleApi* | [**read_person**](docs/PeopleApi.md#read_person) | **GET** /people/{id} | Fetch a person
*PeopleApi* | [**update_person**](docs/PeopleApi.md#update_person) | **PATCH** /people/{id} | Update a person
*PresentationsApi* | [**create_presentation**](docs/PresentationsApi.md#create_presentation) | **POST** /presentations | Create a new presentation
*PresentationsApi* | [**delete_presentation**](docs/PresentationsApi.md#delete_presentation) | **DELETE** /presentations/{id} | Delete a presentation
*PresentationsApi* | [**list_presentations**](docs/PresentationsApi.md#list_presentations) | **GET** /presentations | List presentations
*PresentationsApi* | [**read_presentation**](docs/PresentationsApi.md#read_presentation) | **GET** /presentations/{id} | Fetch a presentation
*PresentationsApi* | [**update_presentation**](docs/PresentationsApi.md#update_presentation) | **PATCH** /presentations/{id} | Update a presentation
*ProgrammesApi* | [**create_programme**](docs/ProgrammesApi.md#create_programme) | **POST** /programmes | Create a new programme
*ProgrammesApi* | [**delete_programme**](docs/ProgrammesApi.md#delete_programme) | **DELETE** /programmes/{id} | Delete a programme
*ProgrammesApi* | [**list_programmes**](docs/ProgrammesApi.md#list_programmes) | **GET** /programmes | List programmes
*ProgrammesApi* | [**read_programme**](docs/ProgrammesApi.md#read_programme) | **GET** /programmes/{id} | Fetch a programme
*ProgrammesApi* | [**update_programme**](docs/ProgrammesApi.md#update_programme) | **PATCH** /programmes/{id} | Update a programme
*ProjectsApi* | [**create_project**](docs/ProjectsApi.md#create_project) | **POST** /projects | Create a new project
*ProjectsApi* | [**delete_project**](docs/ProjectsApi.md#delete_project) | **DELETE** /projects/{id} | Delete a project
*ProjectsApi* | [**list_projects**](docs/ProjectsApi.md#list_projects) | **GET** /projects | List projects
*ProjectsApi* | [**read_project**](docs/ProjectsApi.md#read_project) | **GET** /projects/{id} | Fetch a project
*ProjectsApi* | [**update_project**](docs/ProjectsApi.md#update_project) | **PATCH** /projects/{id} | Update a project
*PublicationsApi* | [**list_publications**](docs/PublicationsApi.md#list_publications) | **GET** /publications | List publications
*PublicationsApi* | [**read_publication**](docs/PublicationsApi.md#read_publication) | **GET** /publications/{id} | Fetch a publication
*ReadApi* | [**current_person**](docs/ReadApi.md#current_person) | **GET** /people/current | Fetch the currently authenticated user
*ReadApi* | [**read_assay**](docs/ReadApi.md#read_assay) | **GET** /assays/{id} | Fetch an assay
*ReadApi* | [**read_collection**](docs/ReadApi.md#read_collection) | **GET** /collections/{id} | Fetch a collection
*ReadApi* | [**read_collection_item**](docs/ReadApi.md#read_collection_item) | **GET** /collections/{collection_id}/items/{id} | Fetch an item from a collection
*ReadApi* | [**read_content_blob**](docs/ReadApi.md#read_content_blob) | **GET** /{asset_types}/{id}/content_blobs/{blob_id} | Fetch information on a content blob
*ReadApi* | [**read_data_file**](docs/ReadApi.md#read_data_file) | **GET** /data_files/{id} | Fetch a data file
*ReadApi* | [**read_document**](docs/ReadApi.md#read_document) | **GET** /documents/{id} | Fetch a document
*ReadApi* | [**read_event**](docs/ReadApi.md#read_event) | **GET** /events/{id} | Fetch an event
*ReadApi* | [**read_extended_metadata_type**](docs/ReadApi.md#read_extended_metadata_type) | **GET** /extended_metadata_types/{id} | Fetch an extended metadata type
*ReadApi* | [**read_institution**](docs/ReadApi.md#read_institution) | **GET** /institutions/{id} | Fetch an institution
*ReadApi* | [**read_investigation**](docs/ReadApi.md#read_investigation) | **GET** /investigations/{id} | Fetch an investigation
*ReadApi* | [**read_model**](docs/ReadApi.md#read_model) | **GET** /models/{id} | Fetch a model
*ReadApi* | [**read_organism**](docs/ReadApi.md#read_organism) | **GET** /organisms/{id} | Fetch an organism
*ReadApi* | [**read_person**](docs/ReadApi.md#read_person) | **GET** /people/{id} | Fetch a person
*ReadApi* | [**read_presentation**](docs/ReadApi.md#read_presentation) | **GET** /presentations/{id} | Fetch a presentation
*ReadApi* | [**read_programme**](docs/ReadApi.md#read_programme) | **GET** /programmes/{id} | Fetch a programme
*ReadApi* | [**read_project**](docs/ReadApi.md#read_project) | **GET** /projects/{id} | Fetch a project
*ReadApi* | [**read_publication**](docs/ReadApi.md#read_publication) | **GET** /publications/{id} | Fetch a publication
*ReadApi* | [**read_sample**](docs/ReadApi.md#read_sample) | **GET** /samples/{id} | Fetch a sample
*ReadApi* | [**read_sample_type**](docs/ReadApi.md#read_sample_type) | **GET** /sample_types/{id} | Fetch a sample type
*ReadApi* | [**read_sop**](docs/ReadApi.md#read_sop) | **GET** /sops/{id} | Fetch a sop
*ReadApi* | [**read_study**](docs/ReadApi.md#read_study) | **GET** /studies/{id} | Fetch a study
*ReadApi* | [**read_workflow**](docs/ReadApi.md#read_workflow) | **GET** /workflows/{id} | Fetch a workflow
*SampleAttributeTypesApi* | [**list_sample_attribute_types**](docs/SampleAttributeTypesApi.md#list_sample_attribute_types) | **GET** /sample_attribute_types | List possible sample attribute types
*SampleTypesApi* | [**create_sample_type**](docs/SampleTypesApi.md#create_sample_type) | **POST** /sample_types | Create a new sample type
*SampleTypesApi* | [**delete_sample_type**](docs/SampleTypesApi.md#delete_sample_type) | **DELETE** /sample_types/{id} | Delete a sample type
*SampleTypesApi* | [**list_sample_types**](docs/SampleTypesApi.md#list_sample_types) | **GET** /sample_types | List sample types
*SampleTypesApi* | [**read_sample_type**](docs/SampleTypesApi.md#read_sample_type) | **GET** /sample_types/{id} | Fetch a sample type
*SampleTypesApi* | [**update_sample_type**](docs/SampleTypesApi.md#update_sample_type) | **PATCH** /sample_types/{id} | Update a sample type
*SamplesApi* | [**create_sample**](docs/SamplesApi.md#create_sample) | **POST** /samples | Create a new sample
*SamplesApi* | [**delete_sample**](docs/SamplesApi.md#delete_sample) | **DELETE** /samples/{id} | Delete a sample
*SamplesApi* | [**read_sample**](docs/SamplesApi.md#read_sample) | **GET** /samples/{id} | Fetch a sample
*SamplesApi* | [**update_sample**](docs/SamplesApi.md#update_sample) | **PATCH** /samples/{id} | Update a sample
*SearchApi* | [**search**](docs/SearchApi.md#search) | **GET** /search | Search SEEK for a given query
*SopsApi* | [**create_sop**](docs/SopsApi.md#create_sop) | **POST** /sops | Create a new sop
*SopsApi* | [**delete_sop**](docs/SopsApi.md#delete_sop) | **DELETE** /sops/{id} | Delete a sop
*SopsApi* | [**list_sops**](docs/SopsApi.md#list_sops) | **GET** /sops | List sops
*SopsApi* | [**read_sop**](docs/SopsApi.md#read_sop) | **GET** /sops/{id} | Fetch a sop
*SopsApi* | [**update_sop**](docs/SopsApi.md#update_sop) | **PATCH** /sops/{id} | Update a sop
*StudiesApi* | [**create_study**](docs/StudiesApi.md#create_study) | **POST** /studies | Create a new study
*StudiesApi* | [**delete_study**](docs/StudiesApi.md#delete_study) | **DELETE** /studies/{id} | Delete a study
*StudiesApi* | [**list_studies**](docs/StudiesApi.md#list_studies) | **GET** /studies | List studies
*StudiesApi* | [**read_study**](docs/StudiesApi.md#read_study) | **GET** /studies/{id} | Fetch a study
*StudiesApi* | [**update_study**](docs/StudiesApi.md#update_study) | **PATCH** /studies/{id} | Update a study
*UpdateApi* | [**update_assay**](docs/UpdateApi.md#update_assay) | **PATCH** /assays/{id} | Update an assay
*UpdateApi* | [**update_collection**](docs/UpdateApi.md#update_collection) | **PATCH** /collections/{id} | Update a collection
*UpdateApi* | [**update_collection_item**](docs/UpdateApi.md#update_collection_item) | **PATCH** /collections/{collection_id}/items/{id} | Update an item in a collection
*UpdateApi* | [**update_data_file**](docs/UpdateApi.md#update_data_file) | **PATCH** /data_files/{id} | Update a data file
*UpdateApi* | [**update_document**](docs/UpdateApi.md#update_document) | **PATCH** /documents/{id} | Update a document
*UpdateApi* | [**update_event**](docs/UpdateApi.md#update_event) | **PATCH** /events/{id} | Update an event
*UpdateApi* | [**update_institution**](docs/UpdateApi.md#update_institution) | **PATCH** /institutions/{id} | Update an institution
*UpdateApi* | [**update_investigation**](docs/UpdateApi.md#update_investigation) | **PATCH** /investigations/{id} | Update an investigation
*UpdateApi* | [**update_model**](docs/UpdateApi.md#update_model) | **PATCH** /models/{id} | Update a model
*UpdateApi* | [**update_person**](docs/UpdateApi.md#update_person) | **PATCH** /people/{id} | Update a person
*UpdateApi* | [**update_presentation**](docs/UpdateApi.md#update_presentation) | **PATCH** /presentations/{id} | Update a presentation
*UpdateApi* | [**update_programme**](docs/UpdateApi.md#update_programme) | **PATCH** /programmes/{id} | Update a programme
*UpdateApi* | [**update_project**](docs/UpdateApi.md#update_project) | **PATCH** /projects/{id} | Update a project
*UpdateApi* | [**update_sample**](docs/UpdateApi.md#update_sample) | **PATCH** /samples/{id} | Update a sample
*UpdateApi* | [**update_sample_type**](docs/UpdateApi.md#update_sample_type) | **PATCH** /sample_types/{id} | Update a sample type
*UpdateApi* | [**update_sop**](docs/UpdateApi.md#update_sop) | **PATCH** /sops/{id} | Update a sop
*UpdateApi* | [**update_study**](docs/UpdateApi.md#update_study) | **PATCH** /studies/{id} | Update a study
*UpdateApi* | [**update_workflow**](docs/UpdateApi.md#update_workflow) | **PATCH** /workflows/{id} | Update a workflow
*UploadApi* | [**upload_asset_content**](docs/UploadApi.md#upload_asset_content) | **PUT** /{asset_types}/{id}/content_blobs/{blob_id} | Upload content to an existing content blob placeholder
*WorkflowsApi* | [**create_workflow**](docs/WorkflowsApi.md#create_workflow) | **POST** /workflows | Create a new workflow
*WorkflowsApi* | [**delete_workflow**](docs/WorkflowsApi.md#delete_workflow) | **DELETE** /workflows/{id} | Delete a workflow
*WorkflowsApi* | [**list_workflows**](docs/WorkflowsApi.md#list_workflows) | **GET** /workflows | List workflows
*WorkflowsApi* | [**read_workflow**](docs/WorkflowsApi.md#read_workflow) | **GET** /workflows/{id} | Fetch a workflow
*WorkflowsApi* | [**update_workflow**](docs/WorkflowsApi.md#update_workflow) | **PATCH** /workflows/{id} | Update a workflow


## Documentation For Models

 - [AccessTypes](docs/AccessTypes.md)
 - [AnySkeleton](docs/AnySkeleton.md)
 - [AnySkeletonAttributes](docs/AnySkeletonAttributes.md)
 - [AnyType](docs/AnyType.md)
 - [AssayAttributes](docs/AssayAttributes.md)
 - [AssayAttributesAssayClass](docs/AssayAttributesAssayClass.md)
 - [AssayAttributesAssayType](docs/AssayAttributesAssayType.md)
 - [AssayAttributesTechnologyType](docs/AssayAttributesTechnologyType.md)
 - [AssayPatch](docs/AssayPatch.md)
 - [AssayPatchData](docs/AssayPatchData.md)
 - [AssayPatchDataAttributes](docs/AssayPatchDataAttributes.md)
 - [AssayPatchDataRelationships](docs/AssayPatchDataRelationships.md)
 - [AssayPost](docs/AssayPost.md)
 - [AssayPostData](docs/AssayPostData.md)
 - [AssayPostDataAttributes](docs/AssayPostDataAttributes.md)
 - [AssayPostDataAttributesAssayClass](docs/AssayPostDataAttributesAssayClass.md)
 - [AssayPostDataAttributesAssayType](docs/AssayPostDataAttributesAssayType.md)
 - [AssayPostDataRelationships](docs/AssayPostDataRelationships.md)
 - [AssayResponse](docs/AssayResponse.md)
 - [AssayResponseData](docs/AssayResponseData.md)
 - [AssayResponseDataAttributes](docs/AssayResponseDataAttributes.md)
 - [AssayResponseDataAttributesAssayClass](docs/AssayResponseDataAttributesAssayClass.md)
 - [AssayResponseDataAttributesAssayType](docs/AssayResponseDataAttributesAssayType.md)
 - [AssayResponseDataAttributesTechnologyType](docs/AssayResponseDataAttributesTechnologyType.md)
 - [AssayResponseDataRelationships](docs/AssayResponseDataRelationships.md)
 - [AssayType](docs/AssayType.md)
 - [AssetLink](docs/AssetLink.md)
 - [AssetLinkCreate](docs/AssetLinkCreate.md)
 - [AssetLinkPatchListInner](docs/AssetLinkPatchListInner.md)
 - [AssetType](docs/AssetType.md)
 - [AssetsCreator](docs/AssetsCreator.md)
 - [BadRequestResponse](docs/BadRequestResponse.md)
 - [BaseMeta](docs/BaseMeta.md)
 - [CollectionAttributes](docs/CollectionAttributes.md)
 - [CollectionItem](docs/CollectionItem.md)
 - [CollectionItemAttributes](docs/CollectionItemAttributes.md)
 - [CollectionItemMeta](docs/CollectionItemMeta.md)
 - [CollectionItemPatch](docs/CollectionItemPatch.md)
 - [CollectionItemPatchData](docs/CollectionItemPatchData.md)
 - [CollectionItemPost](docs/CollectionItemPost.md)
 - [CollectionItemPostData](docs/CollectionItemPostData.md)
 - [CollectionItemPostDataAttributes](docs/CollectionItemPostDataAttributes.md)
 - [CollectionItemPostDataRelationships](docs/CollectionItemPostDataRelationships.md)
 - [CollectionItemRelationships](docs/CollectionItemRelationships.md)
 - [CollectionItemResponse](docs/CollectionItemResponse.md)
 - [CollectionItemType](docs/CollectionItemType.md)
 - [CollectionItemsResponse](docs/CollectionItemsResponse.md)
 - [CollectionLinks](docs/CollectionLinks.md)
 - [CollectionPatch](docs/CollectionPatch.md)
 - [CollectionPatchData](docs/CollectionPatchData.md)
 - [CollectionPatchDataAttributes](docs/CollectionPatchDataAttributes.md)
 - [CollectionPatchDataRelationships](docs/CollectionPatchDataRelationships.md)
 - [CollectionPost](docs/CollectionPost.md)
 - [CollectionPostData](docs/CollectionPostData.md)
 - [CollectionPostDataAttributes](docs/CollectionPostDataAttributes.md)
 - [CollectionPostDataRelationships](docs/CollectionPostDataRelationships.md)
 - [CollectionResponse](docs/CollectionResponse.md)
 - [CollectionResponseData](docs/CollectionResponseData.md)
 - [CollectionResponseDataRelationships](docs/CollectionResponseDataRelationships.md)
 - [CollectionType](docs/CollectionType.md)
 - [ContentBlob](docs/ContentBlob.md)
 - [ContentBlobPlaceholder](docs/ContentBlobPlaceholder.md)
 - [ContentBlobResponse](docs/ContentBlobResponse.md)
 - [ContentBlobResponseData](docs/ContentBlobResponseData.md)
 - [ContentBlobResponseDataAttributes](docs/ContentBlobResponseDataAttributes.md)
 - [ContentBlobSlot](docs/ContentBlobSlot.md)
 - [ContentBlobType](docs/ContentBlobType.md)
 - [ContributedTypeAttributes](docs/ContributedTypeAttributes.md)
 - [DataFilePatch](docs/DataFilePatch.md)
 - [DataFilePatchData](docs/DataFilePatchData.md)
 - [DataFilePatchDataAttributes](docs/DataFilePatchDataAttributes.md)
 - [DataFilePatchDataRelationships](docs/DataFilePatchDataRelationships.md)
 - [DataFilePost](docs/DataFilePost.md)
 - [DataFilePostData](docs/DataFilePostData.md)
 - [DataFilePostDataAttributes](docs/DataFilePostDataAttributes.md)
 - [DataFilePostDataRelationships](docs/DataFilePostDataRelationships.md)
 - [DataFileResponse](docs/DataFileResponse.md)
 - [DataFileResponseData](docs/DataFileResponseData.md)
 - [DataFileResponseDataAttributes](docs/DataFileResponseDataAttributes.md)
 - [DataFileResponseDataRelationships](docs/DataFileResponseDataRelationships.md)
 - [DataFileType](docs/DataFileType.md)
 - [DocumentPatch](docs/DocumentPatch.md)
 - [DocumentPatchData](docs/DocumentPatchData.md)
 - [DocumentPatchDataRelationships](docs/DocumentPatchDataRelationships.md)
 - [DocumentPost](docs/DocumentPost.md)
 - [DocumentPostData](docs/DocumentPostData.md)
 - [DocumentPostDataAttributes](docs/DocumentPostDataAttributes.md)
 - [DocumentPostDataRelationships](docs/DocumentPostDataRelationships.md)
 - [DocumentResponse](docs/DocumentResponse.md)
 - [DocumentResponseData](docs/DocumentResponseData.md)
 - [DocumentResponseDataRelationships](docs/DocumentResponseDataRelationships.md)
 - [DocumentType](docs/DocumentType.md)
 - [DownloadableLinks](docs/DownloadableLinks.md)
 - [Error](docs/Error.md)
 - [ErrorSource](docs/ErrorSource.md)
 - [EventPatch](docs/EventPatch.md)
 - [EventPatchData](docs/EventPatchData.md)
 - [EventPatchDataAttributes](docs/EventPatchDataAttributes.md)
 - [EventPatchDataRelationships](docs/EventPatchDataRelationships.md)
 - [EventPost](docs/EventPost.md)
 - [EventPostData](docs/EventPostData.md)
 - [EventPostDataAttributes](docs/EventPostDataAttributes.md)
 - [EventPostDataRelationships](docs/EventPostDataRelationships.md)
 - [EventResponse](docs/EventResponse.md)
 - [EventResponseData](docs/EventResponseData.md)
 - [EventResponseDataAttributes](docs/EventResponseDataAttributes.md)
 - [EventResponseDataRelationships](docs/EventResponseDataRelationships.md)
 - [EventType](docs/EventType.md)
 - [ExtendedMetadata](docs/ExtendedMetadata.md)
 - [ExtendedMetadataTypeExtendedMetadataAttributeResponse](docs/ExtendedMetadataTypeExtendedMetadataAttributeResponse.md)
 - [ExtendedMetadataTypeResponse](docs/ExtendedMetadataTypeResponse.md)
 - [ExtendedMetadataTypeResponseData](docs/ExtendedMetadataTypeResponseData.md)
 - [ExtendedMetadataTypeResponseDataAttributes](docs/ExtendedMetadataTypeResponseDataAttributes.md)
 - [ExtendedMetadataTypeResponseDataMeta](docs/ExtendedMetadataTypeResponseDataMeta.md)
 - [FileTemplateType](docs/FileTemplateType.md)
 - [ForbiddenResponse](docs/ForbiddenResponse.md)
 - [GitVersion](docs/GitVersion.md)
 - [HumanDiseaseType](docs/HumanDiseaseType.md)
 - [IndexLinks](docs/IndexLinks.md)
 - [IndexResponse](docs/IndexResponse.md)
 - [InstitutionPatch](docs/InstitutionPatch.md)
 - [InstitutionPatchData](docs/InstitutionPatchData.md)
 - [InstitutionPatchDataAttributes](docs/InstitutionPatchDataAttributes.md)
 - [InstitutionPost](docs/InstitutionPost.md)
 - [InstitutionPostData](docs/InstitutionPostData.md)
 - [InstitutionPostDataAttributes](docs/InstitutionPostDataAttributes.md)
 - [InstitutionResponse](docs/InstitutionResponse.md)
 - [InstitutionResponseData](docs/InstitutionResponseData.md)
 - [InstitutionResponseDataAttributes](docs/InstitutionResponseDataAttributes.md)
 - [InstitutionResponseDataRelationships](docs/InstitutionResponseDataRelationships.md)
 - [InstitutionType](docs/InstitutionType.md)
 - [InvestigationPatch](docs/InvestigationPatch.md)
 - [InvestigationPatchData](docs/InvestigationPatchData.md)
 - [InvestigationPatchDataAttributes](docs/InvestigationPatchDataAttributes.md)
 - [InvestigationPatchDataRelationships](docs/InvestigationPatchDataRelationships.md)
 - [InvestigationPost](docs/InvestigationPost.md)
 - [InvestigationPostData](docs/InvestigationPostData.md)
 - [InvestigationPostDataAttributes](docs/InvestigationPostDataAttributes.md)
 - [InvestigationPostDataRelationships](docs/InvestigationPostDataRelationships.md)
 - [InvestigationResponse](docs/InvestigationResponse.md)
 - [InvestigationResponseData](docs/InvestigationResponseData.md)
 - [InvestigationResponseDataAttributes](docs/InvestigationResponseDataAttributes.md)
 - [InvestigationResponseDataRelationships](docs/InvestigationResponseDataRelationships.md)
 - [InvestigationType](docs/InvestigationType.md)
 - [ItemReference](docs/ItemReference.md)
 - [JsonApiVersion](docs/JsonApiVersion.md)
 - [Links](docs/Links.md)
 - [Meta](docs/Meta.md)
 - [ModelAttributes](docs/ModelAttributes.md)
 - [ModelPatch](docs/ModelPatch.md)
 - [ModelPatchData](docs/ModelPatchData.md)
 - [ModelPatchDataAttributes](docs/ModelPatchDataAttributes.md)
 - [ModelPatchDataRelationships](docs/ModelPatchDataRelationships.md)
 - [ModelPost](docs/ModelPost.md)
 - [ModelPostData](docs/ModelPostData.md)
 - [ModelPostDataAttributes](docs/ModelPostDataAttributes.md)
 - [ModelPostDataRelationships](docs/ModelPostDataRelationships.md)
 - [ModelResponse](docs/ModelResponse.md)
 - [ModelResponseData](docs/ModelResponseData.md)
 - [ModelResponseDataRelationships](docs/ModelResponseDataRelationships.md)
 - [ModelType](docs/ModelType.md)
 - [MultipleReferences](docs/MultipleReferences.md)
 - [NotFoundResponse](docs/NotFoundResponse.md)
 - [NotImplementedResponse](docs/NotImplementedResponse.md)
 - [OkResponse](docs/OkResponse.md)
 - [OntologyTerm](docs/OntologyTerm.md)
 - [OrganismResponse](docs/OrganismResponse.md)
 - [OrganismResponseData](docs/OrganismResponseData.md)
 - [OrganismResponseDataAttributes](docs/OrganismResponseDataAttributes.md)
 - [OrganismResponseDataRelationships](docs/OrganismResponseDataRelationships.md)
 - [OrganismType](docs/OrganismType.md)
 - [PeopleType](docs/PeopleType.md)
 - [PermissionResource](docs/PermissionResource.md)
 - [PermissionResourceTypes](docs/PermissionResourceTypes.md)
 - [PersonPatch](docs/PersonPatch.md)
 - [PersonPatchData](docs/PersonPatchData.md)
 - [PersonPatchDataAttributes](docs/PersonPatchDataAttributes.md)
 - [PersonPost](docs/PersonPost.md)
 - [PersonPostData](docs/PersonPostData.md)
 - [PersonPostDataAttributes](docs/PersonPostDataAttributes.md)
 - [PersonResponse](docs/PersonResponse.md)
 - [PersonResponseData](docs/PersonResponseData.md)
 - [PersonResponseDataAttributes](docs/PersonResponseDataAttributes.md)
 - [PersonResponseDataRelationships](docs/PersonResponseDataRelationships.md)
 - [PlaceholderType](docs/PlaceholderType.md)
 - [Policy](docs/Policy.md)
 - [PolicyPermissionsInner](docs/PolicyPermissionsInner.md)
 - [PresentationPatch](docs/PresentationPatch.md)
 - [PresentationPatchData](docs/PresentationPatchData.md)
 - [PresentationPatchDataRelationships](docs/PresentationPatchDataRelationships.md)
 - [PresentationPost](docs/PresentationPost.md)
 - [PresentationPostData](docs/PresentationPostData.md)
 - [PresentationPostDataRelationships](docs/PresentationPostDataRelationships.md)
 - [PresentationResponse](docs/PresentationResponse.md)
 - [PresentationResponseData](docs/PresentationResponseData.md)
 - [PresentationResponseDataRelationships](docs/PresentationResponseDataRelationships.md)
 - [PresentationType](docs/PresentationType.md)
 - [ProgrammeDataType](docs/ProgrammeDataType.md)
 - [ProgrammePatch](docs/ProgrammePatch.md)
 - [ProgrammePatchData](docs/ProgrammePatchData.md)
 - [ProgrammePatchDataAttributes](docs/ProgrammePatchDataAttributes.md)
 - [ProgrammePatchDataRelationships](docs/ProgrammePatchDataRelationships.md)
 - [ProgrammePost](docs/ProgrammePost.md)
 - [ProgrammePostData](docs/ProgrammePostData.md)
 - [ProgrammePostDataAttributes](docs/ProgrammePostDataAttributes.md)
 - [ProgrammePostDataRelationships](docs/ProgrammePostDataRelationships.md)
 - [ProgrammeResponse](docs/ProgrammeResponse.md)
 - [ProgrammeResponseData](docs/ProgrammeResponseData.md)
 - [ProgrammeResponseDataRelationships](docs/ProgrammeResponseDataRelationships.md)
 - [ProgrammeType](docs/ProgrammeType.md)
 - [ProjectMembersListInner](docs/ProjectMembersListInner.md)
 - [ProjectPatch](docs/ProjectPatch.md)
 - [ProjectPatchData](docs/ProjectPatchData.md)
 - [ProjectPatchDataAttributes](docs/ProjectPatchDataAttributes.md)
 - [ProjectPost](docs/ProjectPost.md)
 - [ProjectPostData](docs/ProjectPostData.md)
 - [ProjectPostDataAttributes](docs/ProjectPostDataAttributes.md)
 - [ProjectPostDataRelationships](docs/ProjectPostDataRelationships.md)
 - [ProjectResponse](docs/ProjectResponse.md)
 - [ProjectResponseData](docs/ProjectResponseData.md)
 - [ProjectResponseDataAttributes](docs/ProjectResponseDataAttributes.md)
 - [ProjectResponseDataRelationships](docs/ProjectResponseDataRelationships.md)
 - [ProjectType](docs/ProjectType.md)
 - [PublicationResponse](docs/PublicationResponse.md)
 - [PublicationResponseData](docs/PublicationResponseData.md)
 - [PublicationResponseDataAttributes](docs/PublicationResponseDataAttributes.md)
 - [PublicationResponseDataRelationships](docs/PublicationResponseDataRelationships.md)
 - [PublicationType](docs/PublicationType.md)
 - [RemoteContentBlob](docs/RemoteContentBlob.md)
 - [SampleAttributeBaseType](docs/SampleAttributeBaseType.md)
 - [SampleAttributeType](docs/SampleAttributeType.md)
 - [SampleAttributeTypeAttributes](docs/SampleAttributeTypeAttributes.md)
 - [SampleAttributeTypeType](docs/SampleAttributeTypeType.md)
 - [SamplePatch](docs/SamplePatch.md)
 - [SamplePatchData](docs/SamplePatchData.md)
 - [SamplePatchDataAttributes](docs/SamplePatchDataAttributes.md)
 - [SamplePatchDataRelationships](docs/SamplePatchDataRelationships.md)
 - [SamplePost](docs/SamplePost.md)
 - [SamplePostData](docs/SamplePostData.md)
 - [SamplePostDataAttributes](docs/SamplePostDataAttributes.md)
 - [SamplePostDataRelationships](docs/SamplePostDataRelationships.md)
 - [SampleResponse](docs/SampleResponse.md)
 - [SampleResponseData](docs/SampleResponseData.md)
 - [SampleResponseDataAttributes](docs/SampleResponseDataAttributes.md)
 - [SampleResponseDataRelationships](docs/SampleResponseDataRelationships.md)
 - [SampleType](docs/SampleType.md)
 - [SampleTypePatch](docs/SampleTypePatch.md)
 - [SampleTypePatchData](docs/SampleTypePatchData.md)
 - [SampleTypePatchDataAttributes](docs/SampleTypePatchDataAttributes.md)
 - [SampleTypePatchDataRelationships](docs/SampleTypePatchDataRelationships.md)
 - [SampleTypePost](docs/SampleTypePost.md)
 - [SampleTypePostData](docs/SampleTypePostData.md)
 - [SampleTypePostDataAttributes](docs/SampleTypePostDataAttributes.md)
 - [SampleTypePostDataRelationships](docs/SampleTypePostDataRelationships.md)
 - [SampleTypeResponse](docs/SampleTypeResponse.md)
 - [SampleTypeResponseData](docs/SampleTypeResponseData.md)
 - [SampleTypeResponseDataAttributes](docs/SampleTypeResponseDataAttributes.md)
 - [SampleTypeResponseDataRelationships](docs/SampleTypeResponseDataRelationships.md)
 - [SampleTypeSampleAttributePatch](docs/SampleTypeSampleAttributePatch.md)
 - [SampleTypeSampleAttributePost](docs/SampleTypeSampleAttributePost.md)
 - [SampleTypeSampleAttributePostSampleAttributeType](docs/SampleTypeSampleAttributePostSampleAttributeType.md)
 - [SampleTypeSampleAttributeResponse](docs/SampleTypeSampleAttributeResponse.md)
 - [SampleTypeSampleAttributeResponseSampleAttributeType](docs/SampleTypeSampleAttributeResponseSampleAttributeType.md)
 - [SampleTypeType](docs/SampleTypeType.md)
 - [SearchResponse](docs/SearchResponse.md)
 - [SingleReference](docs/SingleReference.md)
 - [SingleReferenceWithTitle](docs/SingleReferenceWithTitle.md)
 - [SingleReferenceWithTitleMeta](docs/SingleReferenceWithTitleMeta.md)
 - [SnapshotSkeleton](docs/SnapshotSkeleton.md)
 - [SopPatch](docs/SopPatch.md)
 - [SopPatchData](docs/SopPatchData.md)
 - [SopPost](docs/SopPost.md)
 - [SopPostData](docs/SopPostData.md)
 - [SopResponse](docs/SopResponse.md)
 - [SopResponseData](docs/SopResponseData.md)
 - [SopType](docs/SopType.md)
 - [StudyPatch](docs/StudyPatch.md)
 - [StudyPatchData](docs/StudyPatchData.md)
 - [StudyPatchDataAttributes](docs/StudyPatchDataAttributes.md)
 - [StudyPatchDataRelationships](docs/StudyPatchDataRelationships.md)
 - [StudyPost](docs/StudyPost.md)
 - [StudyPostData](docs/StudyPostData.md)
 - [StudyPostDataAttributes](docs/StudyPostDataAttributes.md)
 - [StudyPostDataRelationships](docs/StudyPostDataRelationships.md)
 - [StudyResponse](docs/StudyResponse.md)
 - [StudyResponseData](docs/StudyResponseData.md)
 - [StudyResponseDataAttributes](docs/StudyResponseDataAttributes.md)
 - [StudyResponseDataRelationships](docs/StudyResponseDataRelationships.md)
 - [StudyType](docs/StudyType.md)
 - [UnprocessableEntityResponse](docs/UnprocessableEntityResponse.md)
 - [Version](docs/Version.md)
 - [VersionNumber](docs/VersionNumber.md)
 - [WorkflowInput](docs/WorkflowInput.md)
 - [WorkflowOutput](docs/WorkflowOutput.md)
 - [WorkflowPatch](docs/WorkflowPatch.md)
 - [WorkflowPatchData](docs/WorkflowPatchData.md)
 - [WorkflowPatchDataAttributes](docs/WorkflowPatchDataAttributes.md)
 - [WorkflowPatchDataRelationships](docs/WorkflowPatchDataRelationships.md)
 - [WorkflowPost](docs/WorkflowPost.md)
 - [WorkflowPostData](docs/WorkflowPostData.md)
 - [WorkflowPostDataAttributes](docs/WorkflowPostDataAttributes.md)
 - [WorkflowPostDataAttributesWorkflowClass](docs/WorkflowPostDataAttributesWorkflowClass.md)
 - [WorkflowPostDataRelationships](docs/WorkflowPostDataRelationships.md)
 - [WorkflowResponse](docs/WorkflowResponse.md)
 - [WorkflowResponseData](docs/WorkflowResponseData.md)
 - [WorkflowResponseDataAttributes](docs/WorkflowResponseDataAttributes.md)
 - [WorkflowResponseDataAttributesInternals](docs/WorkflowResponseDataAttributesInternals.md)
 - [WorkflowResponseDataAttributesVersionsInner](docs/WorkflowResponseDataAttributesVersionsInner.md)
 - [WorkflowResponseDataAttributesWorkflowClass](docs/WorkflowResponseDataAttributesWorkflowClass.md)
 - [WorkflowResponseDataLinks](docs/WorkflowResponseDataLinks.md)
 - [WorkflowResponseDataRelationships](docs/WorkflowResponseDataRelationships.md)
 - [WorkflowStep](docs/WorkflowStep.md)
 - [WorkflowType](docs/WorkflowType.md)
 - [Workflowtool](docs/Workflowtool.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization


Authentication schemes defined for the API:
<a id="OAuth2"></a>
### OAuth2

- **Type**: OAuth
- **Flow**: accessCode
- **Authorization URL**: /oauth/authorize
- **Scopes**: 
 - **read**: Read, download and list resources
 - **write**: Create, upload, update and delete resources

<a id="apiToken"></a>
### apiToken

- **Type**: API key
- **API key parameter name**: Authorization
- **Location**: HTTP header

<a id="basicAuth"></a>
### basicAuth

- **Type**: HTTP basic authentication


## Author

support@fair-dom.org


