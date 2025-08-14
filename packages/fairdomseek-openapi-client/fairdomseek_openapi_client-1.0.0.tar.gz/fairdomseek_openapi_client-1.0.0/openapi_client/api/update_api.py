# coding: utf-8

"""
    JSON API to FAIRDOM SEEK

    <a name=\"api\"></a>The JSON API to FAIRDOM SEEK is a [JSON API](http://jsonapi.org) specification describing how to read and write to a SEEK instance.  The API is defined in the [OpenAPI specification](https://swagger.io/specification) currently in [version 2](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md)  Example IPython notebooks showing use of the API are available on [GitHub](https://github.com/FAIRdom/api-workshop)  ## Policy <a name=\"Policy\"></a> A Policy specifies the visibility of an object to people using SEEK. A <a href=\"#projects\">**Project**</a> may specify the default policy for objects belonging to that <a href=\"#projects\">**Project**</a>  The **Policy** specifies the visibility of the object to non-registered people or <a href=\"#people\">**People**</a> not allowed special access.  The access may be one of (in order of increasing \"power\"):  * no_access * view * download * edit * manage  In addition a **Policy** may give special access to specific <a href=\"#people\">**People**</a>, People working at an <a href=\"#institutions\">**Institution**</a> or working on a <a href=\"#projects\">**Project**</a>.  ## License <a name=\"License\"></a> The license specifies the license that will apply to any <a href=\"#dataFiles\">**DataFiles**</a>, <a href=\"#models\">**Models**</a>, <a href=\"#sops\">**SOPs**</a>, <a href=\"#documents\">**Documents**</a> and <a href=\"#presentations\">**Presentations**</a> associated with a <a href=\"#projects\">**Project**</a>.  The license can currently be:  * `CC0-1.0` - [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) * `CC-BY-4.0` - [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/) * `CC-BY-SA-4.0` - [Creative Commons Attribution Share-Alike 4.0](https://creativecommons.org/licenses/by-sa/4.0/) * `ODC-BY-1.0` - [Open Data Commons Attribution License 1.0](http://www.opendefinition.org/licenses/odc-by) * `ODbL-1.0` - [Open Data Commons Open Database License 1.0](http://www.opendefinition.org/licenses/odc-odbl) * `ODC-PDDL-1.0` - [Open Data Commons Public Domain Dedication and Licence 1.0](http://www.opendefinition.org/licenses/odc-pddl) * `notspecified` - License Not Specified * `other-at` - Other (Attribution) * `other-open` - Other (Open) * `other-pd` - Other (Public Domain) * `AFL-3.0` - [Academic Free License 3.0](http://www.opensource.org/licenses/AFL-3.0) * `Against-DRM` - [Against DRM](http://www.opendefinition.org/licenses/against-drm) * `CC-BY-NC-4.0` - [Creative Commons Attribution-NonCommercial 4.0](https://creativecommons.org/licenses/by-nc/4.0/) * `DSL` - [Design Science License](http://www.opendefinition.org/licenses/dsl) * `FAL-1.3` - [Free Art License 1.3](http://www.opendefinition.org/licenses/fal) * `GFDL-1.3-no-cover-texts-no-invariant-sections` - [GNU Free Documentation License 1.3 with no cover texts and no invariant sections](http://www.opendefinition.org/licenses/gfdl) * `geogratis` - [Geogratis](http://geogratis.gc.ca/geogratis/licenceGG) * `hesa-withrights` - [Higher Education Statistics Agency Copyright with data.gov.uk rights](http://www.hesa.ac.uk/index.php?option=com_content&amp;task=view&amp;id=2619&amp;Itemid=209) * `localauth-withrights` - Local Authority Copyright with data.gov.uk rights * `MirOS` - [MirOS Licence](http://www.opensource.org/licenses/MirOS) * `NPOSL-3.0` - [Non-Profit Open Software License 3.0](http://www.opensource.org/licenses/NPOSL-3.0) * `OGL-UK-1.0` - [Open Government Licence 1.0 (United Kingdom)](http://reference.data.gov.uk/id/open-government-licence) * `OGL-UK-2.0` - [Open Government Licence 2.0 (United Kingdom)](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/) * `OGL-UK-3.0` - [Open Government Licence 3.0 (United Kingdom)](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) * `OGL-Canada-2.0` - [Open Government License 2.0 (Canada)](http://data.gc.ca/eng/open-government-licence-canada) * `OSL-3.0` - [Open Software License 3.0](http://www.opensource.org/licenses/OSL-3.0) * `dli-model-use` - [Statistics Canada: Data Liberation Initiative (DLI) - Model Data Use Licence](http://data.library.ubc.ca/datalib/geographic/DMTI/license.html) * `Talis` - [Talis Community License](http://www.opendefinition.org/licenses/tcl) * `ukclickusepsi` - UK Click Use PSI * `ukcrown-withrights` - UK Crown Copyright with data.gov.uk rights * `ukpsi` - [UK PSI Public Sector Information](http://www.opendefinition.org/licenses/ukpsi)  ## ContentBlob <a name=\"ContentBlob\"></a> <a name=\"contentBlobs\"></a> The content of a <a href=\"#dataFiles\">**DataFile**</a>, <a href=\"#documents\">**Document**</a>, <a href=\"#models\">**Model**</a>, <a href=\"#sops\">**SOP**</a> or <a href=\"#presentations\">**Presentation**</a> is specified as a set of **ContentBlobs**.  When a resource with content is created, it is possible to specify a ContentBlob either as:  * A remote ContentBlob with:   * **URI to the content's location**   * The original filename for the content   * The content type of the remote content as a [MIME media type](https://en.wikipedia.org/wiki/Media_type) * A placeholder that will be filled with uploaded content   * **The original filename for the content**   * **The content type of the content as a [MIME media type](https://en.wikipedia.org/wiki/Media_type)**  The creation of the resource will return a JSON document containing ContentBlobs corresponding to the remote ContentBlob and to the ContentBlob placeholder. The blobs contain a URI to their location.  A placeholder can then be satisfied by uploading a file to the location URI. For example by a placeholder such as   ``` \"content_blobs\": [   {     \"original_filename\": \"a_pdf_file.pdf\",     \"content_type\": \"application/pdf\",     \"link\": \"http://fairdomhub.org/data_files/57/content_blobs/313\"   } ], ```  may be satisfied by uploading a file to http://fairdomhub.org/data_files/57/content_blobs/313 using the <a href=\"#uploadAssetContent\">uploadAssetContent</a> operation  The content of a resource may be downloaded by first *reading* the resource and then *downloading* the ContentBlobs from their URI.  ## Extended Metadata  Some types support [Extended Metadata](https://docs.seek4science.org/tech/extended-metadata), which allows additional attributes to be defined according to an Extended Metadata Type.  Types currently supported are <a href=\"#investigations\">**Investigation**</a>, <a href=\"#studies\">**Study**</a>, <a href=\"#assays\">**Assay**</a>,  <a href=\"#dataFiles\">**DataFile**</a>, <a href=\"#sops\">**SOP**</a>, <a href=\"#presentations\">**Presentation**</a>, <a href=\"#documents\">**Document**</a>, <a href=\"#models\">**Model**</a>, <a href=\"#events\">**Event**</a>, <a href=\"#collections\">**Collection**</a>, <a href=\"#projects\">**Project**</a>  The responses and requests for each of these types include an additional optional attribute _extended_attributes_ which describes  * _extended_metadata_type_id_ - the id of the extended metadata type which can be used to find more details about what its attributes are. * _attribute_map_ - which is a map of key / value pairs where the key is the attribute name   For example, a Study may have extended metadata, defined by an Extended Metadata Type with id 12, that has attributes for age, name, and date_of_birth. These could be shown, within its attributes, as:  ``` \"extended_attributes\": {   \"extended_metadata_type_id\": \"12\",   \"attribute_map\": {     \"age\": 44,     \"name\": \"Fred Bloggs\",     \"date_of_birth\": \"2024-01-01\"   } } ```  If you wish to create or update a study to make use of this extended metadata, the request payload would be described the same.  Upon creation or update there would be a validation check that the attributes are valid.  The API supports listing all available Extended Metadata Types, and inspecting an individual type by its id. For more information see the [Extended Metadata Type definitions](api#tag/extendedMetadataTypes).

    The version of the OpenAPI document: 0.3
    Contact: support@fair-dom.org
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501

import warnings
from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from pydantic import Field, StrictInt
from typing import Optional
from typing_extensions import Annotated
from openapi_client.models.assay_patch import AssayPatch
from openapi_client.models.assay_response import AssayResponse
from openapi_client.models.collection_item_patch import CollectionItemPatch
from openapi_client.models.collection_item_response import CollectionItemResponse
from openapi_client.models.collection_patch import CollectionPatch
from openapi_client.models.collection_response import CollectionResponse
from openapi_client.models.data_file_patch import DataFilePatch
from openapi_client.models.data_file_response import DataFileResponse
from openapi_client.models.document_patch import DocumentPatch
from openapi_client.models.document_response import DocumentResponse
from openapi_client.models.event_patch import EventPatch
from openapi_client.models.event_response import EventResponse
from openapi_client.models.institution_patch import InstitutionPatch
from openapi_client.models.institution_response import InstitutionResponse
from openapi_client.models.investigation_patch import InvestigationPatch
from openapi_client.models.investigation_response import InvestigationResponse
from openapi_client.models.model_patch import ModelPatch
from openapi_client.models.model_response import ModelResponse
from openapi_client.models.person_patch import PersonPatch
from openapi_client.models.person_response import PersonResponse
from openapi_client.models.presentation_patch import PresentationPatch
from openapi_client.models.presentation_response import PresentationResponse
from openapi_client.models.programme_patch import ProgrammePatch
from openapi_client.models.programme_response import ProgrammeResponse
from openapi_client.models.project_patch import ProjectPatch
from openapi_client.models.project_response import ProjectResponse
from openapi_client.models.sample_patch import SamplePatch
from openapi_client.models.sample_response import SampleResponse
from openapi_client.models.sample_type_patch import SampleTypePatch
from openapi_client.models.sample_type_response import SampleTypeResponse
from openapi_client.models.sop_patch import SopPatch
from openapi_client.models.sop_response import SopResponse
from openapi_client.models.study_patch import StudyPatch
from openapi_client.models.study_response import StudyResponse
from openapi_client.models.workflow_patch import WorkflowPatch
from openapi_client.models.workflow_response import WorkflowResponse

from openapi_client.api_client import ApiClient, RequestSerialized
from openapi_client.api_response import ApiResponse
from openapi_client.rest import RESTResponseType


class UpdateApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def update_assay(
        self,
        id: Annotated[StrictInt, Field(description="The assay to be fetched, updated or deleted")],
        assay_patch: Annotated[Optional[AssayPatch], Field(description="The assay to patch")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> AssayResponse:
        """Update an assay

        <a name=\"updateAssay\"></a>An **updateAssay** operation will modify the information held about the specified <a href=\"#assays\">**Assay**</a>. This operation is only available if the authenticated user has access to the <a href=\"#assays\">**Assay**</a>.  The **updateAssay** operation returns a JSON object representing the modified <a href=\"#assays\">**Assay**</a>. 

        :param id: The assay to be fetched, updated or deleted (required)
        :type id: int
        :param assay_patch: The assay to patch
        :type assay_patch: AssayPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_assay_serialize(
            id=id,
            assay_patch=assay_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "AssayResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_assay_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The assay to be fetched, updated or deleted")],
        assay_patch: Annotated[Optional[AssayPatch], Field(description="The assay to patch")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[AssayResponse]:
        """Update an assay

        <a name=\"updateAssay\"></a>An **updateAssay** operation will modify the information held about the specified <a href=\"#assays\">**Assay**</a>. This operation is only available if the authenticated user has access to the <a href=\"#assays\">**Assay**</a>.  The **updateAssay** operation returns a JSON object representing the modified <a href=\"#assays\">**Assay**</a>. 

        :param id: The assay to be fetched, updated or deleted (required)
        :type id: int
        :param assay_patch: The assay to patch
        :type assay_patch: AssayPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_assay_serialize(
            id=id,
            assay_patch=assay_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "AssayResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_assay_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The assay to be fetched, updated or deleted")],
        assay_patch: Annotated[Optional[AssayPatch], Field(description="The assay to patch")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update an assay

        <a name=\"updateAssay\"></a>An **updateAssay** operation will modify the information held about the specified <a href=\"#assays\">**Assay**</a>. This operation is only available if the authenticated user has access to the <a href=\"#assays\">**Assay**</a>.  The **updateAssay** operation returns a JSON object representing the modified <a href=\"#assays\">**Assay**</a>. 

        :param id: The assay to be fetched, updated or deleted (required)
        :type id: int
        :param assay_patch: The assay to patch
        :type assay_patch: AssayPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_assay_serialize(
            id=id,
            assay_patch=assay_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "AssayResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_assay_serialize(
        self,
        id,
        assay_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if assay_patch is not None:
            _body_params = assay_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/assays/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_collection(
        self,
        id: Annotated[StrictInt, Field(description="The collection to fetch")],
        collection_patch: Annotated[Optional[CollectionPatch], Field(description="The collection to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CollectionResponse:
        """Update a collection

        <a name=\"updateCollection\"></a>An **updateCollection** operation will modify the information held about the specified <a href=\"#collections\">**Collection**</a>. This operation is only available if the authenticated user has access to the <a href=\"#collections\">**Collection**</a>.  To add and remove things from the collection, see the <a href=\"#collection_items\">**Collection Item**</a> API.  The **updateCollection** operation returns a JSON object representing the modified <a href=\"#collections\">**Collection**</a>. 

        :param id: The collection to fetch (required)
        :type id: int
        :param collection_patch: The collection to patch.
        :type collection_patch: CollectionPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_collection_serialize(
            id=id,
            collection_patch=collection_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CollectionResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_collection_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The collection to fetch")],
        collection_patch: Annotated[Optional[CollectionPatch], Field(description="The collection to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CollectionResponse]:
        """Update a collection

        <a name=\"updateCollection\"></a>An **updateCollection** operation will modify the information held about the specified <a href=\"#collections\">**Collection**</a>. This operation is only available if the authenticated user has access to the <a href=\"#collections\">**Collection**</a>.  To add and remove things from the collection, see the <a href=\"#collection_items\">**Collection Item**</a> API.  The **updateCollection** operation returns a JSON object representing the modified <a href=\"#collections\">**Collection**</a>. 

        :param id: The collection to fetch (required)
        :type id: int
        :param collection_patch: The collection to patch.
        :type collection_patch: CollectionPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_collection_serialize(
            id=id,
            collection_patch=collection_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CollectionResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_collection_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The collection to fetch")],
        collection_patch: Annotated[Optional[CollectionPatch], Field(description="The collection to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a collection

        <a name=\"updateCollection\"></a>An **updateCollection** operation will modify the information held about the specified <a href=\"#collections\">**Collection**</a>. This operation is only available if the authenticated user has access to the <a href=\"#collections\">**Collection**</a>.  To add and remove things from the collection, see the <a href=\"#collection_items\">**Collection Item**</a> API.  The **updateCollection** operation returns a JSON object representing the modified <a href=\"#collections\">**Collection**</a>. 

        :param id: The collection to fetch (required)
        :type id: int
        :param collection_patch: The collection to patch.
        :type collection_patch: CollectionPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_collection_serialize(
            id=id,
            collection_patch=collection_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CollectionResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_collection_serialize(
        self,
        id,
        collection_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if collection_patch is not None:
            _body_params = collection_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/collections/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_collection_item(
        self,
        collection_id: Annotated[StrictInt, Field(description="The ID of the collection")],
        id: Annotated[StrictInt, Field(description="The ID of the item in the collection")],
        collection_item_patch: Annotated[Optional[CollectionItemPatch], Field(description="The collection item to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> CollectionItemResponse:
        """Update an item in a collection

        <a name=\"updateCollectionItem\"></a>An **updateCollectionItem** operation will modify the information held about the specified <a href=\"#collection_items\">**CollectionItem**</a>. This operation is only available if the authenticated user has access to the <a href=\"#collections\">**Collection**</a>.  The **updateCollectionItem** operation returns a JSON object representing the modified <a href=\"#collection_items\">**Collection Item**</a>. 

        :param collection_id: The ID of the collection (required)
        :type collection_id: int
        :param id: The ID of the item in the collection (required)
        :type id: int
        :param collection_item_patch: The collection item to patch.
        :type collection_item_patch: CollectionItemPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_collection_item_serialize(
            collection_id=collection_id,
            id=id,
            collection_item_patch=collection_item_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CollectionItemResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_collection_item_with_http_info(
        self,
        collection_id: Annotated[StrictInt, Field(description="The ID of the collection")],
        id: Annotated[StrictInt, Field(description="The ID of the item in the collection")],
        collection_item_patch: Annotated[Optional[CollectionItemPatch], Field(description="The collection item to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[CollectionItemResponse]:
        """Update an item in a collection

        <a name=\"updateCollectionItem\"></a>An **updateCollectionItem** operation will modify the information held about the specified <a href=\"#collection_items\">**CollectionItem**</a>. This operation is only available if the authenticated user has access to the <a href=\"#collections\">**Collection**</a>.  The **updateCollectionItem** operation returns a JSON object representing the modified <a href=\"#collection_items\">**Collection Item**</a>. 

        :param collection_id: The ID of the collection (required)
        :type collection_id: int
        :param id: The ID of the item in the collection (required)
        :type id: int
        :param collection_item_patch: The collection item to patch.
        :type collection_item_patch: CollectionItemPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_collection_item_serialize(
            collection_id=collection_id,
            id=id,
            collection_item_patch=collection_item_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CollectionItemResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_collection_item_without_preload_content(
        self,
        collection_id: Annotated[StrictInt, Field(description="The ID of the collection")],
        id: Annotated[StrictInt, Field(description="The ID of the item in the collection")],
        collection_item_patch: Annotated[Optional[CollectionItemPatch], Field(description="The collection item to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update an item in a collection

        <a name=\"updateCollectionItem\"></a>An **updateCollectionItem** operation will modify the information held about the specified <a href=\"#collection_items\">**CollectionItem**</a>. This operation is only available if the authenticated user has access to the <a href=\"#collections\">**Collection**</a>.  The **updateCollectionItem** operation returns a JSON object representing the modified <a href=\"#collection_items\">**Collection Item**</a>. 

        :param collection_id: The ID of the collection (required)
        :type collection_id: int
        :param id: The ID of the item in the collection (required)
        :type id: int
        :param collection_item_patch: The collection item to patch.
        :type collection_item_patch: CollectionItemPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_collection_item_serialize(
            collection_id=collection_id,
            id=id,
            collection_item_patch=collection_item_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "CollectionItemResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_collection_item_serialize(
        self,
        collection_id,
        id,
        collection_item_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if collection_id is not None:
            _path_params['collection_id'] = collection_id
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if collection_item_patch is not None:
            _body_params = collection_item_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/collections/{collection_id}/items/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_data_file(
        self,
        id: Annotated[StrictInt, Field(description="The data file to fetch")],
        data_file_patch: Annotated[Optional[DataFilePatch], Field(description="The data file to patch")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> DataFileResponse:
        """Update a data file

        <a name=\"updateDataFile\"></a>An **updateDataFile** operation will modify the information held about the specified <a href=\"#dataFiles\">**DataFile**</a>. This operation is only available if the authenticated user has access to the <a href=\"#dataFiles\">**DataFile**</a>.  Please note that when linking a data file to a workflow it currently isn't possible to define the relationship type (e.g test data, example data) through the api.  The **updateDataFile** operation returns a JSON object representing the modified <a href=\"#dataFiles\">**DataFile**</a>. 

        :param id: The data file to fetch (required)
        :type id: int
        :param data_file_patch: The data file to patch
        :type data_file_patch: DataFilePatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_data_file_serialize(
            id=id,
            data_file_patch=data_file_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DataFileResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_data_file_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The data file to fetch")],
        data_file_patch: Annotated[Optional[DataFilePatch], Field(description="The data file to patch")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[DataFileResponse]:
        """Update a data file

        <a name=\"updateDataFile\"></a>An **updateDataFile** operation will modify the information held about the specified <a href=\"#dataFiles\">**DataFile**</a>. This operation is only available if the authenticated user has access to the <a href=\"#dataFiles\">**DataFile**</a>.  Please note that when linking a data file to a workflow it currently isn't possible to define the relationship type (e.g test data, example data) through the api.  The **updateDataFile** operation returns a JSON object representing the modified <a href=\"#dataFiles\">**DataFile**</a>. 

        :param id: The data file to fetch (required)
        :type id: int
        :param data_file_patch: The data file to patch
        :type data_file_patch: DataFilePatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_data_file_serialize(
            id=id,
            data_file_patch=data_file_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DataFileResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_data_file_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The data file to fetch")],
        data_file_patch: Annotated[Optional[DataFilePatch], Field(description="The data file to patch")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a data file

        <a name=\"updateDataFile\"></a>An **updateDataFile** operation will modify the information held about the specified <a href=\"#dataFiles\">**DataFile**</a>. This operation is only available if the authenticated user has access to the <a href=\"#dataFiles\">**DataFile**</a>.  Please note that when linking a data file to a workflow it currently isn't possible to define the relationship type (e.g test data, example data) through the api.  The **updateDataFile** operation returns a JSON object representing the modified <a href=\"#dataFiles\">**DataFile**</a>. 

        :param id: The data file to fetch (required)
        :type id: int
        :param data_file_patch: The data file to patch
        :type data_file_patch: DataFilePatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_data_file_serialize(
            id=id,
            data_file_patch=data_file_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DataFileResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_data_file_serialize(
        self,
        id,
        data_file_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if data_file_patch is not None:
            _body_params = data_file_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/data_files/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_document(
        self,
        id: Annotated[StrictInt, Field(description="The document to fetch")],
        document_patch: Annotated[Optional[DocumentPatch], Field(description="The document to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> DocumentResponse:
        """Update a document

        <a name=\"updateDocument\"></a>An **updateDocument** operation will modify the information held about the specified <a href=\"#documents\">**Document**</a>. This operation is only available if the authenticated user has access to the <a href=\"#documents\">**Document**</a>.  The **updateDocument** operation returns a JSON object representing the modified <a href=\"#documents\">**Document**</a>. 

        :param id: The document to fetch (required)
        :type id: int
        :param document_patch: The document to patch.
        :type document_patch: DocumentPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_document_serialize(
            id=id,
            document_patch=document_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DocumentResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_document_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The document to fetch")],
        document_patch: Annotated[Optional[DocumentPatch], Field(description="The document to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[DocumentResponse]:
        """Update a document

        <a name=\"updateDocument\"></a>An **updateDocument** operation will modify the information held about the specified <a href=\"#documents\">**Document**</a>. This operation is only available if the authenticated user has access to the <a href=\"#documents\">**Document**</a>.  The **updateDocument** operation returns a JSON object representing the modified <a href=\"#documents\">**Document**</a>. 

        :param id: The document to fetch (required)
        :type id: int
        :param document_patch: The document to patch.
        :type document_patch: DocumentPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_document_serialize(
            id=id,
            document_patch=document_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DocumentResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_document_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The document to fetch")],
        document_patch: Annotated[Optional[DocumentPatch], Field(description="The document to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a document

        <a name=\"updateDocument\"></a>An **updateDocument** operation will modify the information held about the specified <a href=\"#documents\">**Document**</a>. This operation is only available if the authenticated user has access to the <a href=\"#documents\">**Document**</a>.  The **updateDocument** operation returns a JSON object representing the modified <a href=\"#documents\">**Document**</a>. 

        :param id: The document to fetch (required)
        :type id: int
        :param document_patch: The document to patch.
        :type document_patch: DocumentPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_document_serialize(
            id=id,
            document_patch=document_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "DocumentResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_document_serialize(
        self,
        id,
        document_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if document_patch is not None:
            _body_params = document_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/documents/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_event(
        self,
        id: Annotated[StrictInt, Field(description="The event to fetch")],
        event_patch: Annotated[Optional[EventPatch], Field(description="The event to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> EventResponse:
        """Update an event

        <a name=\"updateEvent\"></a>An **updateEvent** operation will modify the information held about the specified <a href=\"#events\">**Event**</a>. This operation is only available if the authenticated user has access to the <a href=\"#events\">**Event**</a>.  The **updateEvent** operation returns a JSON object representing the modified <a href=\"#events\">**Event**</a>. 

        :param id: The event to fetch (required)
        :type id: int
        :param event_patch: The event to update.
        :type event_patch: EventPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_event_serialize(
            id=id,
            event_patch=event_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "EventResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_event_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The event to fetch")],
        event_patch: Annotated[Optional[EventPatch], Field(description="The event to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[EventResponse]:
        """Update an event

        <a name=\"updateEvent\"></a>An **updateEvent** operation will modify the information held about the specified <a href=\"#events\">**Event**</a>. This operation is only available if the authenticated user has access to the <a href=\"#events\">**Event**</a>.  The **updateEvent** operation returns a JSON object representing the modified <a href=\"#events\">**Event**</a>. 

        :param id: The event to fetch (required)
        :type id: int
        :param event_patch: The event to update.
        :type event_patch: EventPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_event_serialize(
            id=id,
            event_patch=event_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "EventResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_event_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The event to fetch")],
        event_patch: Annotated[Optional[EventPatch], Field(description="The event to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update an event

        <a name=\"updateEvent\"></a>An **updateEvent** operation will modify the information held about the specified <a href=\"#events\">**Event**</a>. This operation is only available if the authenticated user has access to the <a href=\"#events\">**Event**</a>.  The **updateEvent** operation returns a JSON object representing the modified <a href=\"#events\">**Event**</a>. 

        :param id: The event to fetch (required)
        :type id: int
        :param event_patch: The event to update.
        :type event_patch: EventPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_event_serialize(
            id=id,
            event_patch=event_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "EventResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_event_serialize(
        self,
        id,
        event_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if event_patch is not None:
            _body_params = event_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/events/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_institution(
        self,
        id: Annotated[StrictInt, Field(description="The institution to fetch, patch or delete")],
        institution_patch: Annotated[Optional[InstitutionPatch], Field(description="The data with which to update the institution.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> InstitutionResponse:
        """Update an institution

        <a name=\"updateInstitution\"></a>An **updateInstitution** operation will modify the information held about the specified <a href=\"#institutions\">**Institution**</a>. This operation is only available if the authenticated user has access to the <a href=\"#institutions\">**Institution**</a>.  The **updateInstitution** operation returns a JSON object representing the modified <a href=\"#institutions\">**Institution**</a>. 

        :param id: The institution to fetch, patch or delete (required)
        :type id: int
        :param institution_patch: The data with which to update the institution.
        :type institution_patch: InstitutionPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_institution_serialize(
            id=id,
            institution_patch=institution_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "InstitutionResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_institution_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The institution to fetch, patch or delete")],
        institution_patch: Annotated[Optional[InstitutionPatch], Field(description="The data with which to update the institution.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[InstitutionResponse]:
        """Update an institution

        <a name=\"updateInstitution\"></a>An **updateInstitution** operation will modify the information held about the specified <a href=\"#institutions\">**Institution**</a>. This operation is only available if the authenticated user has access to the <a href=\"#institutions\">**Institution**</a>.  The **updateInstitution** operation returns a JSON object representing the modified <a href=\"#institutions\">**Institution**</a>. 

        :param id: The institution to fetch, patch or delete (required)
        :type id: int
        :param institution_patch: The data with which to update the institution.
        :type institution_patch: InstitutionPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_institution_serialize(
            id=id,
            institution_patch=institution_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "InstitutionResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_institution_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The institution to fetch, patch or delete")],
        institution_patch: Annotated[Optional[InstitutionPatch], Field(description="The data with which to update the institution.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update an institution

        <a name=\"updateInstitution\"></a>An **updateInstitution** operation will modify the information held about the specified <a href=\"#institutions\">**Institution**</a>. This operation is only available if the authenticated user has access to the <a href=\"#institutions\">**Institution**</a>.  The **updateInstitution** operation returns a JSON object representing the modified <a href=\"#institutions\">**Institution**</a>. 

        :param id: The institution to fetch, patch or delete (required)
        :type id: int
        :param institution_patch: The data with which to update the institution.
        :type institution_patch: InstitutionPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_institution_serialize(
            id=id,
            institution_patch=institution_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "InstitutionResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_institution_serialize(
        self,
        id,
        institution_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if institution_patch is not None:
            _body_params = institution_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/institutions/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_investigation(
        self,
        id: Annotated[StrictInt, Field(description="The investigation to fetch, patch or delete")],
        investigation_patch: Annotated[Optional[InvestigationPatch], Field(description="The investigation to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> InvestigationResponse:
        """Update an investigation

        <a name=\"updateInvestigation\"></a>An **updateInvestigation** operation will modify the information held about the specified <a href=\"#investigations\">**Investigation**</a>. This operation is only available if the authenticated user has access to the <a href=\"#investigations\">**Investigation**</a>.  The **updateInvestigation** operation returns a JSON object representing the modified <a href=\"#investigations\">**Investigation**</a>. 

        :param id: The investigation to fetch, patch or delete (required)
        :type id: int
        :param investigation_patch: The investigation to patch.
        :type investigation_patch: InvestigationPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_investigation_serialize(
            id=id,
            investigation_patch=investigation_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "InvestigationResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_investigation_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The investigation to fetch, patch or delete")],
        investigation_patch: Annotated[Optional[InvestigationPatch], Field(description="The investigation to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[InvestigationResponse]:
        """Update an investigation

        <a name=\"updateInvestigation\"></a>An **updateInvestigation** operation will modify the information held about the specified <a href=\"#investigations\">**Investigation**</a>. This operation is only available if the authenticated user has access to the <a href=\"#investigations\">**Investigation**</a>.  The **updateInvestigation** operation returns a JSON object representing the modified <a href=\"#investigations\">**Investigation**</a>. 

        :param id: The investigation to fetch, patch or delete (required)
        :type id: int
        :param investigation_patch: The investigation to patch.
        :type investigation_patch: InvestigationPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_investigation_serialize(
            id=id,
            investigation_patch=investigation_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "InvestigationResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_investigation_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The investigation to fetch, patch or delete")],
        investigation_patch: Annotated[Optional[InvestigationPatch], Field(description="The investigation to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update an investigation

        <a name=\"updateInvestigation\"></a>An **updateInvestigation** operation will modify the information held about the specified <a href=\"#investigations\">**Investigation**</a>. This operation is only available if the authenticated user has access to the <a href=\"#investigations\">**Investigation**</a>.  The **updateInvestigation** operation returns a JSON object representing the modified <a href=\"#investigations\">**Investigation**</a>. 

        :param id: The investigation to fetch, patch or delete (required)
        :type id: int
        :param investigation_patch: The investigation to patch.
        :type investigation_patch: InvestigationPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_investigation_serialize(
            id=id,
            investigation_patch=investigation_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "InvestigationResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_investigation_serialize(
        self,
        id,
        investigation_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if investigation_patch is not None:
            _body_params = investigation_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/investigations/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_model(
        self,
        id: Annotated[StrictInt, Field(description="The model to fetch, patch or delete")],
        model_patch: Annotated[Optional[ModelPatch], Field(description="The model to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ModelResponse:
        """Update a model

        <a name=\"updateModel\"></a>An **updateModel** operation will modify the information held about the specified <a href=\"#models\">**Model**</a>. This operation is only available if the authenticated user has access to the <a href=\"#models\">**Model**</a>.  The **updateModel** operation returns a JSON object representing the modified <a href=\"#models\">**Model**</a>. 

        :param id: The model to fetch, patch or delete (required)
        :type id: int
        :param model_patch: The model to patch.
        :type model_patch: ModelPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_model_serialize(
            id=id,
            model_patch=model_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ModelResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_model_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The model to fetch, patch or delete")],
        model_patch: Annotated[Optional[ModelPatch], Field(description="The model to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[ModelResponse]:
        """Update a model

        <a name=\"updateModel\"></a>An **updateModel** operation will modify the information held about the specified <a href=\"#models\">**Model**</a>. This operation is only available if the authenticated user has access to the <a href=\"#models\">**Model**</a>.  The **updateModel** operation returns a JSON object representing the modified <a href=\"#models\">**Model**</a>. 

        :param id: The model to fetch, patch or delete (required)
        :type id: int
        :param model_patch: The model to patch.
        :type model_patch: ModelPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_model_serialize(
            id=id,
            model_patch=model_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ModelResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_model_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The model to fetch, patch or delete")],
        model_patch: Annotated[Optional[ModelPatch], Field(description="The model to patch.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a model

        <a name=\"updateModel\"></a>An **updateModel** operation will modify the information held about the specified <a href=\"#models\">**Model**</a>. This operation is only available if the authenticated user has access to the <a href=\"#models\">**Model**</a>.  The **updateModel** operation returns a JSON object representing the modified <a href=\"#models\">**Model**</a>. 

        :param id: The model to fetch, patch or delete (required)
        :type id: int
        :param model_patch: The model to patch.
        :type model_patch: ModelPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_model_serialize(
            id=id,
            model_patch=model_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ModelResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_model_serialize(
        self,
        id,
        model_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if model_patch is not None:
            _body_params = model_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/models/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_person(
        self,
        id: Annotated[StrictInt, Field(description="The person to fetch, patch or delete")],
        person_patch: Annotated[Optional[PersonPatch], Field(description="The data with which to update the person.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PersonResponse:
        """Update a person

        <a name=\"updatePerson\"></a>An **updatePerson** operation will modify the information held about the specified <a href=\"#people\">**Person**</a>. This operation is only available if the authenticated user has access to the <a href=\"#people\">**Person**</a>.  The **updatePerson** operation returns a JSON object representing the modified <a href=\"#people\">**Person**</a>. 

        :param id: The person to fetch, patch or delete (required)
        :type id: int
        :param person_patch: The data with which to update the person.
        :type person_patch: PersonPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_person_serialize(
            id=id,
            person_patch=person_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PersonResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_person_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The person to fetch, patch or delete")],
        person_patch: Annotated[Optional[PersonPatch], Field(description="The data with which to update the person.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PersonResponse]:
        """Update a person

        <a name=\"updatePerson\"></a>An **updatePerson** operation will modify the information held about the specified <a href=\"#people\">**Person**</a>. This operation is only available if the authenticated user has access to the <a href=\"#people\">**Person**</a>.  The **updatePerson** operation returns a JSON object representing the modified <a href=\"#people\">**Person**</a>. 

        :param id: The person to fetch, patch or delete (required)
        :type id: int
        :param person_patch: The data with which to update the person.
        :type person_patch: PersonPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_person_serialize(
            id=id,
            person_patch=person_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PersonResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_person_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The person to fetch, patch or delete")],
        person_patch: Annotated[Optional[PersonPatch], Field(description="The data with which to update the person.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a person

        <a name=\"updatePerson\"></a>An **updatePerson** operation will modify the information held about the specified <a href=\"#people\">**Person**</a>. This operation is only available if the authenticated user has access to the <a href=\"#people\">**Person**</a>.  The **updatePerson** operation returns a JSON object representing the modified <a href=\"#people\">**Person**</a>. 

        :param id: The person to fetch, patch or delete (required)
        :type id: int
        :param person_patch: The data with which to update the person.
        :type person_patch: PersonPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_person_serialize(
            id=id,
            person_patch=person_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PersonResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_person_serialize(
        self,
        id,
        person_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if person_patch is not None:
            _body_params = person_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/people/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_presentation(
        self,
        id: Annotated[StrictInt, Field(description="The presentation to fetch, patch or delete")],
        presentation_patch: Annotated[Optional[PresentationPatch], Field(description="The presentation to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> PresentationResponse:
        """Update a presentation

        <a name=\"updatePresentation\"></a>An **updatePresentation** operation will modify the information held about the specified <a href=\"#presentations\">**Presentation**</a>. This operation is only available if the authenticated user has access to the <a href=\"#presentations\">**Presentation**</a>.  The **updatePresentation** operation returns a JSON object representing the modified <a href=\"#presentations\">**Presentation**</a>. 

        :param id: The presentation to fetch, patch or delete (required)
        :type id: int
        :param presentation_patch: The presentation to update.
        :type presentation_patch: PresentationPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_presentation_serialize(
            id=id,
            presentation_patch=presentation_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PresentationResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_presentation_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The presentation to fetch, patch or delete")],
        presentation_patch: Annotated[Optional[PresentationPatch], Field(description="The presentation to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[PresentationResponse]:
        """Update a presentation

        <a name=\"updatePresentation\"></a>An **updatePresentation** operation will modify the information held about the specified <a href=\"#presentations\">**Presentation**</a>. This operation is only available if the authenticated user has access to the <a href=\"#presentations\">**Presentation**</a>.  The **updatePresentation** operation returns a JSON object representing the modified <a href=\"#presentations\">**Presentation**</a>. 

        :param id: The presentation to fetch, patch or delete (required)
        :type id: int
        :param presentation_patch: The presentation to update.
        :type presentation_patch: PresentationPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_presentation_serialize(
            id=id,
            presentation_patch=presentation_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PresentationResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_presentation_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The presentation to fetch, patch or delete")],
        presentation_patch: Annotated[Optional[PresentationPatch], Field(description="The presentation to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a presentation

        <a name=\"updatePresentation\"></a>An **updatePresentation** operation will modify the information held about the specified <a href=\"#presentations\">**Presentation**</a>. This operation is only available if the authenticated user has access to the <a href=\"#presentations\">**Presentation**</a>.  The **updatePresentation** operation returns a JSON object representing the modified <a href=\"#presentations\">**Presentation**</a>. 

        :param id: The presentation to fetch, patch or delete (required)
        :type id: int
        :param presentation_patch: The presentation to update.
        :type presentation_patch: PresentationPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_presentation_serialize(
            id=id,
            presentation_patch=presentation_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "PresentationResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_presentation_serialize(
        self,
        id,
        presentation_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if presentation_patch is not None:
            _body_params = presentation_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/presentations/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_programme(
        self,
        id: Annotated[StrictInt, Field(description="The programme to fetch, patch or delete")],
        programme_patch: Annotated[Optional[ProgrammePatch], Field(description="The data with which to update the programme.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ProgrammeResponse:
        """Update a programme

        <a name=\"updateProgramme\"></a>An **updateProgramme** operation will modify the information held about the specified <a href=\"#programmes\">**Programme**</a>. This operation is only available if the authenticated user has access to the <a href=\"#programmes\">**Programme**</a>.  The **updateProgramme** operation returns a JSON object representing the modified <a href=\"#programmes\">**Programme**</a>. 

        :param id: The programme to fetch, patch or delete (required)
        :type id: int
        :param programme_patch: The data with which to update the programme.
        :type programme_patch: ProgrammePatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_programme_serialize(
            id=id,
            programme_patch=programme_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ProgrammeResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_programme_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The programme to fetch, patch or delete")],
        programme_patch: Annotated[Optional[ProgrammePatch], Field(description="The data with which to update the programme.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[ProgrammeResponse]:
        """Update a programme

        <a name=\"updateProgramme\"></a>An **updateProgramme** operation will modify the information held about the specified <a href=\"#programmes\">**Programme**</a>. This operation is only available if the authenticated user has access to the <a href=\"#programmes\">**Programme**</a>.  The **updateProgramme** operation returns a JSON object representing the modified <a href=\"#programmes\">**Programme**</a>. 

        :param id: The programme to fetch, patch or delete (required)
        :type id: int
        :param programme_patch: The data with which to update the programme.
        :type programme_patch: ProgrammePatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_programme_serialize(
            id=id,
            programme_patch=programme_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ProgrammeResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_programme_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The programme to fetch, patch or delete")],
        programme_patch: Annotated[Optional[ProgrammePatch], Field(description="The data with which to update the programme.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a programme

        <a name=\"updateProgramme\"></a>An **updateProgramme** operation will modify the information held about the specified <a href=\"#programmes\">**Programme**</a>. This operation is only available if the authenticated user has access to the <a href=\"#programmes\">**Programme**</a>.  The **updateProgramme** operation returns a JSON object representing the modified <a href=\"#programmes\">**Programme**</a>. 

        :param id: The programme to fetch, patch or delete (required)
        :type id: int
        :param programme_patch: The data with which to update the programme.
        :type programme_patch: ProgrammePatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_programme_serialize(
            id=id,
            programme_patch=programme_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ProgrammeResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_programme_serialize(
        self,
        id,
        programme_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if programme_patch is not None:
            _body_params = programme_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/programmes/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_project(
        self,
        id: Annotated[StrictInt, Field(description="The project to fetch, patch or delete")],
        project_patch: Annotated[Optional[ProjectPatch], Field(description="The data with which to update the project.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ProjectResponse:
        """Update a project

        <a name=\"updateProject\"></a>An **updateProject** operation will modify the information held about the specified <a href=\"#projects\">**Project**</a>. This operation is only available if the authenticated user has access to the <a href=\"#projects\">**Project**</a>.  The **updateProject** operation returns a JSON object representing the modified <a href=\"#projects\">**Project**</a>. 

        :param id: The project to fetch, patch or delete (required)
        :type id: int
        :param project_patch: The data with which to update the project.
        :type project_patch: ProjectPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_project_serialize(
            id=id,
            project_patch=project_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ProjectResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_project_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The project to fetch, patch or delete")],
        project_patch: Annotated[Optional[ProjectPatch], Field(description="The data with which to update the project.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[ProjectResponse]:
        """Update a project

        <a name=\"updateProject\"></a>An **updateProject** operation will modify the information held about the specified <a href=\"#projects\">**Project**</a>. This operation is only available if the authenticated user has access to the <a href=\"#projects\">**Project**</a>.  The **updateProject** operation returns a JSON object representing the modified <a href=\"#projects\">**Project**</a>. 

        :param id: The project to fetch, patch or delete (required)
        :type id: int
        :param project_patch: The data with which to update the project.
        :type project_patch: ProjectPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_project_serialize(
            id=id,
            project_patch=project_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ProjectResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_project_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The project to fetch, patch or delete")],
        project_patch: Annotated[Optional[ProjectPatch], Field(description="The data with which to update the project.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a project

        <a name=\"updateProject\"></a>An **updateProject** operation will modify the information held about the specified <a href=\"#projects\">**Project**</a>. This operation is only available if the authenticated user has access to the <a href=\"#projects\">**Project**</a>.  The **updateProject** operation returns a JSON object representing the modified <a href=\"#projects\">**Project**</a>. 

        :param id: The project to fetch, patch or delete (required)
        :type id: int
        :param project_patch: The data with which to update the project.
        :type project_patch: ProjectPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_project_serialize(
            id=id,
            project_patch=project_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ProjectResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_project_serialize(
        self,
        id,
        project_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if project_patch is not None:
            _body_params = project_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/projects/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_sample(
        self,
        id: Annotated[StrictInt, Field(description="The sample to fetch, patch or delete")],
        sample_patch: Annotated[Optional[SamplePatch], Field(description="The sample to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> SampleResponse:
        """Update a sample

        <a name=\"updateSample\"></a>An **updateSample** operation will modify the information held about the specified <a href=\"#samples\">**Sample**</a>. This operation is only available if the authenticated user has access to the <a href=\"#samples\">**Sample**</a>.  The **updateSample** operation returns a JSON object representing the modified <a href=\"#samples\">**Sample**</a>. 

        :param id: The sample to fetch, patch or delete (required)
        :type id: int
        :param sample_patch: The sample to update.
        :type sample_patch: SamplePatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_sample_serialize(
            id=id,
            sample_patch=sample_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SampleResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_sample_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The sample to fetch, patch or delete")],
        sample_patch: Annotated[Optional[SamplePatch], Field(description="The sample to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[SampleResponse]:
        """Update a sample

        <a name=\"updateSample\"></a>An **updateSample** operation will modify the information held about the specified <a href=\"#samples\">**Sample**</a>. This operation is only available if the authenticated user has access to the <a href=\"#samples\">**Sample**</a>.  The **updateSample** operation returns a JSON object representing the modified <a href=\"#samples\">**Sample**</a>. 

        :param id: The sample to fetch, patch or delete (required)
        :type id: int
        :param sample_patch: The sample to update.
        :type sample_patch: SamplePatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_sample_serialize(
            id=id,
            sample_patch=sample_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SampleResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_sample_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The sample to fetch, patch or delete")],
        sample_patch: Annotated[Optional[SamplePatch], Field(description="The sample to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a sample

        <a name=\"updateSample\"></a>An **updateSample** operation will modify the information held about the specified <a href=\"#samples\">**Sample**</a>. This operation is only available if the authenticated user has access to the <a href=\"#samples\">**Sample**</a>.  The **updateSample** operation returns a JSON object representing the modified <a href=\"#samples\">**Sample**</a>. 

        :param id: The sample to fetch, patch or delete (required)
        :type id: int
        :param sample_patch: The sample to update.
        :type sample_patch: SamplePatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_sample_serialize(
            id=id,
            sample_patch=sample_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SampleResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_sample_serialize(
        self,
        id,
        sample_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if sample_patch is not None:
            _body_params = sample_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/samples/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_sample_type(
        self,
        id: Annotated[StrictInt, Field(description="The sample type to be fetched, updated or deleted")],
        sample_type_patch: Annotated[Optional[SampleTypePatch], Field(description="The sample type to patch")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> SampleTypeResponse:
        """Update a sample type

        <a name=\"updateSampleType\"></a>An **updateSampleType** operation will modify the information held about the specified <a href=\"#sampleTypes\">**SampleType**</a>. This operation is only available if the authenticated user has access to the <a href=\"#sampleTypes\">**SampleType**</a>.  The **updateSampleType** operation returns a JSON object representing the modified <a href=\"#sampleTypes\">**SampleType**</a>. 

        :param id: The sample type to be fetched, updated or deleted (required)
        :type id: int
        :param sample_type_patch: The sample type to patch
        :type sample_type_patch: SampleTypePatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_sample_type_serialize(
            id=id,
            sample_type_patch=sample_type_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SampleTypeResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_sample_type_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The sample type to be fetched, updated or deleted")],
        sample_type_patch: Annotated[Optional[SampleTypePatch], Field(description="The sample type to patch")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[SampleTypeResponse]:
        """Update a sample type

        <a name=\"updateSampleType\"></a>An **updateSampleType** operation will modify the information held about the specified <a href=\"#sampleTypes\">**SampleType**</a>. This operation is only available if the authenticated user has access to the <a href=\"#sampleTypes\">**SampleType**</a>.  The **updateSampleType** operation returns a JSON object representing the modified <a href=\"#sampleTypes\">**SampleType**</a>. 

        :param id: The sample type to be fetched, updated or deleted (required)
        :type id: int
        :param sample_type_patch: The sample type to patch
        :type sample_type_patch: SampleTypePatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_sample_type_serialize(
            id=id,
            sample_type_patch=sample_type_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SampleTypeResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_sample_type_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The sample type to be fetched, updated or deleted")],
        sample_type_patch: Annotated[Optional[SampleTypePatch], Field(description="The sample type to patch")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a sample type

        <a name=\"updateSampleType\"></a>An **updateSampleType** operation will modify the information held about the specified <a href=\"#sampleTypes\">**SampleType**</a>. This operation is only available if the authenticated user has access to the <a href=\"#sampleTypes\">**SampleType**</a>.  The **updateSampleType** operation returns a JSON object representing the modified <a href=\"#sampleTypes\">**SampleType**</a>. 

        :param id: The sample type to be fetched, updated or deleted (required)
        :type id: int
        :param sample_type_patch: The sample type to patch
        :type sample_type_patch: SampleTypePatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_sample_type_serialize(
            id=id,
            sample_type_patch=sample_type_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SampleTypeResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_sample_type_serialize(
        self,
        id,
        sample_type_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if sample_type_patch is not None:
            _body_params = sample_type_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/sample_types/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_sop(
        self,
        id: Annotated[StrictInt, Field(description="The SOP to fetch, patch or delete")],
        sop_patch: Annotated[Optional[SopPatch], Field(description="The sop to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> SopResponse:
        """Update a sop

        <a name=\"updateSop\"></a>An **updateSop** operation will modify the information held about the specified <a href=\"#sops\">**Sop**</a>. This operation is only available if the authenticated user has access to the <a href=\"#sops\">**Sop**</a>.  The **updateSop** operation returns a JSON object representing the modified <a href=\"#sops\">**Sop**</a>. 

        :param id: The SOP to fetch, patch or delete (required)
        :type id: int
        :param sop_patch: The sop to update.
        :type sop_patch: SopPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_sop_serialize(
            id=id,
            sop_patch=sop_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SopResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_sop_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The SOP to fetch, patch or delete")],
        sop_patch: Annotated[Optional[SopPatch], Field(description="The sop to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[SopResponse]:
        """Update a sop

        <a name=\"updateSop\"></a>An **updateSop** operation will modify the information held about the specified <a href=\"#sops\">**Sop**</a>. This operation is only available if the authenticated user has access to the <a href=\"#sops\">**Sop**</a>.  The **updateSop** operation returns a JSON object representing the modified <a href=\"#sops\">**Sop**</a>. 

        :param id: The SOP to fetch, patch or delete (required)
        :type id: int
        :param sop_patch: The sop to update.
        :type sop_patch: SopPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_sop_serialize(
            id=id,
            sop_patch=sop_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SopResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_sop_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The SOP to fetch, patch or delete")],
        sop_patch: Annotated[Optional[SopPatch], Field(description="The sop to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a sop

        <a name=\"updateSop\"></a>An **updateSop** operation will modify the information held about the specified <a href=\"#sops\">**Sop**</a>. This operation is only available if the authenticated user has access to the <a href=\"#sops\">**Sop**</a>.  The **updateSop** operation returns a JSON object representing the modified <a href=\"#sops\">**Sop**</a>. 

        :param id: The SOP to fetch, patch or delete (required)
        :type id: int
        :param sop_patch: The sop to update.
        :type sop_patch: SopPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_sop_serialize(
            id=id,
            sop_patch=sop_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SopResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_sop_serialize(
        self,
        id,
        sop_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if sop_patch is not None:
            _body_params = sop_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/sops/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_study(
        self,
        id: Annotated[StrictInt, Field(description="The study to fetch, patch or delete")],
        study_patch: Annotated[Optional[StudyPatch], Field(description="The study to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> StudyResponse:
        """Update a study

        <a name=\"updateStudy\"></a>An **updateStudy** operation will modify the information held about the specified <a href=\"#studies\">**Study**</a>. This operation is only available if the authenticated user has access to the <a href=\"#studies\">**Study**</a>.  The **updateStudy** operation returns a JSON object representing the modified <a href=\"#studies\">**Study**</a>. 

        :param id: The study to fetch, patch or delete (required)
        :type id: int
        :param study_patch: The study to update.
        :type study_patch: StudyPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_study_serialize(
            id=id,
            study_patch=study_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "StudyResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_study_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The study to fetch, patch or delete")],
        study_patch: Annotated[Optional[StudyPatch], Field(description="The study to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[StudyResponse]:
        """Update a study

        <a name=\"updateStudy\"></a>An **updateStudy** operation will modify the information held about the specified <a href=\"#studies\">**Study**</a>. This operation is only available if the authenticated user has access to the <a href=\"#studies\">**Study**</a>.  The **updateStudy** operation returns a JSON object representing the modified <a href=\"#studies\">**Study**</a>. 

        :param id: The study to fetch, patch or delete (required)
        :type id: int
        :param study_patch: The study to update.
        :type study_patch: StudyPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_study_serialize(
            id=id,
            study_patch=study_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "StudyResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_study_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The study to fetch, patch or delete")],
        study_patch: Annotated[Optional[StudyPatch], Field(description="The study to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a study

        <a name=\"updateStudy\"></a>An **updateStudy** operation will modify the information held about the specified <a href=\"#studies\">**Study**</a>. This operation is only available if the authenticated user has access to the <a href=\"#studies\">**Study**</a>.  The **updateStudy** operation returns a JSON object representing the modified <a href=\"#studies\">**Study**</a>. 

        :param id: The study to fetch, patch or delete (required)
        :type id: int
        :param study_patch: The study to update.
        :type study_patch: StudyPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_study_serialize(
            id=id,
            study_patch=study_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "StudyResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_study_serialize(
        self,
        id,
        study_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if study_patch is not None:
            _body_params = study_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/studies/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def update_workflow(
        self,
        id: Annotated[StrictInt, Field(description="The workflow to fetch, patch or delete")],
        workflow_patch: Annotated[Optional[WorkflowPatch], Field(description="The workflow to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> WorkflowResponse:
        """Update a workflow

        <a name=\"updateWorkflow\"></a>An **updateWorkflow** operation will modify the information held about the specified <a href=\"#workflows\">**Workflow**</a>. This operation is only available if the authenticated user has access to the <a href=\"#workflows\">**Workflow**</a>.  Please note that when linking a workflow to a data file it currently isn't possible to define the relationship type (e.g test data, example data) through the api.  The **updateWorkflow** operation returns a JSON object representing the modified <a href=\"#workflows\">**Workflow**</a>. 

        :param id: The workflow to fetch, patch or delete (required)
        :type id: int
        :param workflow_patch: The workflow to update.
        :type workflow_patch: WorkflowPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_workflow_serialize(
            id=id,
            workflow_patch=workflow_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "WorkflowResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def update_workflow_with_http_info(
        self,
        id: Annotated[StrictInt, Field(description="The workflow to fetch, patch or delete")],
        workflow_patch: Annotated[Optional[WorkflowPatch], Field(description="The workflow to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[WorkflowResponse]:
        """Update a workflow

        <a name=\"updateWorkflow\"></a>An **updateWorkflow** operation will modify the information held about the specified <a href=\"#workflows\">**Workflow**</a>. This operation is only available if the authenticated user has access to the <a href=\"#workflows\">**Workflow**</a>.  Please note that when linking a workflow to a data file it currently isn't possible to define the relationship type (e.g test data, example data) through the api.  The **updateWorkflow** operation returns a JSON object representing the modified <a href=\"#workflows\">**Workflow**</a>. 

        :param id: The workflow to fetch, patch or delete (required)
        :type id: int
        :param workflow_patch: The workflow to update.
        :type workflow_patch: WorkflowPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_workflow_serialize(
            id=id,
            workflow_patch=workflow_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "WorkflowResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def update_workflow_without_preload_content(
        self,
        id: Annotated[StrictInt, Field(description="The workflow to fetch, patch or delete")],
        workflow_patch: Annotated[Optional[WorkflowPatch], Field(description="The workflow to update.")] = None,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Update a workflow

        <a name=\"updateWorkflow\"></a>An **updateWorkflow** operation will modify the information held about the specified <a href=\"#workflows\">**Workflow**</a>. This operation is only available if the authenticated user has access to the <a href=\"#workflows\">**Workflow**</a>.  Please note that when linking a workflow to a data file it currently isn't possible to define the relationship type (e.g test data, example data) through the api.  The **updateWorkflow** operation returns a JSON object representing the modified <a href=\"#workflows\">**Workflow**</a>. 

        :param id: The workflow to fetch, patch or delete (required)
        :type id: int
        :param workflow_patch: The workflow to update.
        :type workflow_patch: WorkflowPatch
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._update_workflow_serialize(
            id=id,
            workflow_patch=workflow_patch,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "WorkflowResponse",
            '403': "ForbiddenResponse",
            '404': "NotFoundResponse",
            '422': "UnprocessableEntityResponse",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _update_workflow_serialize(
        self,
        id,
        workflow_patch,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id is not None:
            _path_params['id'] = id
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if workflow_patch is not None:
            _body_params = workflow_patch


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'OAuth2', 
            'apiToken', 
            'basicAuth'
        ]

        return self.api_client.param_serialize(
            method='PATCH',
            resource_path='/workflows/{id}',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


