# coding: utf-8

"""
    JSON API to FAIRDOM SEEK

    <a name=\"api\"></a>The JSON API to FAIRDOM SEEK is a [JSON API](http://jsonapi.org) specification describing how to read and write to a SEEK instance.  The API is defined in the [OpenAPI specification](https://swagger.io/specification) currently in [version 2](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md)  Example IPython notebooks showing use of the API are available on [GitHub](https://github.com/FAIRdom/api-workshop)  ## Policy <a name=\"Policy\"></a> A Policy specifies the visibility of an object to people using SEEK. A <a href=\"#projects\">**Project**</a> may specify the default policy for objects belonging to that <a href=\"#projects\">**Project**</a>  The **Policy** specifies the visibility of the object to non-registered people or <a href=\"#people\">**People**</a> not allowed special access.  The access may be one of (in order of increasing \"power\"):  * no_access * view * download * edit * manage  In addition a **Policy** may give special access to specific <a href=\"#people\">**People**</a>, People working at an <a href=\"#institutions\">**Institution**</a> or working on a <a href=\"#projects\">**Project**</a>.  ## License <a name=\"License\"></a> The license specifies the license that will apply to any <a href=\"#dataFiles\">**DataFiles**</a>, <a href=\"#models\">**Models**</a>, <a href=\"#sops\">**SOPs**</a>, <a href=\"#documents\">**Documents**</a> and <a href=\"#presentations\">**Presentations**</a> associated with a <a href=\"#projects\">**Project**</a>.  The license can currently be:  * `CC0-1.0` - [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) * `CC-BY-4.0` - [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/) * `CC-BY-SA-4.0` - [Creative Commons Attribution Share-Alike 4.0](https://creativecommons.org/licenses/by-sa/4.0/) * `ODC-BY-1.0` - [Open Data Commons Attribution License 1.0](http://www.opendefinition.org/licenses/odc-by) * `ODbL-1.0` - [Open Data Commons Open Database License 1.0](http://www.opendefinition.org/licenses/odc-odbl) * `ODC-PDDL-1.0` - [Open Data Commons Public Domain Dedication and Licence 1.0](http://www.opendefinition.org/licenses/odc-pddl) * `notspecified` - License Not Specified * `other-at` - Other (Attribution) * `other-open` - Other (Open) * `other-pd` - Other (Public Domain) * `AFL-3.0` - [Academic Free License 3.0](http://www.opensource.org/licenses/AFL-3.0) * `Against-DRM` - [Against DRM](http://www.opendefinition.org/licenses/against-drm) * `CC-BY-NC-4.0` - [Creative Commons Attribution-NonCommercial 4.0](https://creativecommons.org/licenses/by-nc/4.0/) * `DSL` - [Design Science License](http://www.opendefinition.org/licenses/dsl) * `FAL-1.3` - [Free Art License 1.3](http://www.opendefinition.org/licenses/fal) * `GFDL-1.3-no-cover-texts-no-invariant-sections` - [GNU Free Documentation License 1.3 with no cover texts and no invariant sections](http://www.opendefinition.org/licenses/gfdl) * `geogratis` - [Geogratis](http://geogratis.gc.ca/geogratis/licenceGG) * `hesa-withrights` - [Higher Education Statistics Agency Copyright with data.gov.uk rights](http://www.hesa.ac.uk/index.php?option=com_content&amp;task=view&amp;id=2619&amp;Itemid=209) * `localauth-withrights` - Local Authority Copyright with data.gov.uk rights * `MirOS` - [MirOS Licence](http://www.opensource.org/licenses/MirOS) * `NPOSL-3.0` - [Non-Profit Open Software License 3.0](http://www.opensource.org/licenses/NPOSL-3.0) * `OGL-UK-1.0` - [Open Government Licence 1.0 (United Kingdom)](http://reference.data.gov.uk/id/open-government-licence) * `OGL-UK-2.0` - [Open Government Licence 2.0 (United Kingdom)](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/) * `OGL-UK-3.0` - [Open Government Licence 3.0 (United Kingdom)](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) * `OGL-Canada-2.0` - [Open Government License 2.0 (Canada)](http://data.gc.ca/eng/open-government-licence-canada) * `OSL-3.0` - [Open Software License 3.0](http://www.opensource.org/licenses/OSL-3.0) * `dli-model-use` - [Statistics Canada: Data Liberation Initiative (DLI) - Model Data Use Licence](http://data.library.ubc.ca/datalib/geographic/DMTI/license.html) * `Talis` - [Talis Community License](http://www.opendefinition.org/licenses/tcl) * `ukclickusepsi` - UK Click Use PSI * `ukcrown-withrights` - UK Crown Copyright with data.gov.uk rights * `ukpsi` - [UK PSI Public Sector Information](http://www.opendefinition.org/licenses/ukpsi)  ## ContentBlob <a name=\"ContentBlob\"></a> <a name=\"contentBlobs\"></a> The content of a <a href=\"#dataFiles\">**DataFile**</a>, <a href=\"#documents\">**Document**</a>, <a href=\"#models\">**Model**</a>, <a href=\"#sops\">**SOP**</a> or <a href=\"#presentations\">**Presentation**</a> is specified as a set of **ContentBlobs**.  When a resource with content is created, it is possible to specify a ContentBlob either as:  * A remote ContentBlob with:   * **URI to the content's location**   * The original filename for the content   * The content type of the remote content as a [MIME media type](https://en.wikipedia.org/wiki/Media_type) * A placeholder that will be filled with uploaded content   * **The original filename for the content**   * **The content type of the content as a [MIME media type](https://en.wikipedia.org/wiki/Media_type)**  The creation of the resource will return a JSON document containing ContentBlobs corresponding to the remote ContentBlob and to the ContentBlob placeholder. The blobs contain a URI to their location.  A placeholder can then be satisfied by uploading a file to the location URI. For example by a placeholder such as   ``` \"content_blobs\": [   {     \"original_filename\": \"a_pdf_file.pdf\",     \"content_type\": \"application/pdf\",     \"link\": \"http://fairdomhub.org/data_files/57/content_blobs/313\"   } ], ```  may be satisfied by uploading a file to http://fairdomhub.org/data_files/57/content_blobs/313 using the <a href=\"#uploadAssetContent\">uploadAssetContent</a> operation  The content of a resource may be downloaded by first *reading* the resource and then *downloading* the ContentBlobs from their URI.  ## Extended Metadata  Some types support [Extended Metadata](https://docs.seek4science.org/tech/extended-metadata), which allows additional attributes to be defined according to an Extended Metadata Type.  Types currently supported are <a href=\"#investigations\">**Investigation**</a>, <a href=\"#studies\">**Study**</a>, <a href=\"#assays\">**Assay**</a>,  <a href=\"#dataFiles\">**DataFile**</a>, <a href=\"#sops\">**SOP**</a>, <a href=\"#presentations\">**Presentation**</a>, <a href=\"#documents\">**Document**</a>, <a href=\"#models\">**Model**</a>, <a href=\"#events\">**Event**</a>, <a href=\"#collections\">**Collection**</a>, <a href=\"#projects\">**Project**</a>  The responses and requests for each of these types include an additional optional attribute _extended_attributes_ which describes  * _extended_metadata_type_id_ - the id of the extended metadata type which can be used to find more details about what its attributes are. * _attribute_map_ - which is a map of key / value pairs where the key is the attribute name   For example, a Study may have extended metadata, defined by an Extended Metadata Type with id 12, that has attributes for age, name, and date_of_birth. These could be shown, within its attributes, as:  ``` \"extended_attributes\": {   \"extended_metadata_type_id\": \"12\",   \"attribute_map\": {     \"age\": 44,     \"name\": \"Fred Bloggs\",     \"date_of_birth\": \"2024-01-01\"   } } ```  If you wish to create or update a study to make use of this extended metadata, the request payload would be described the same.  Upon creation or update there would be a validation check that the attributes are valid.  The API supports listing all available Extended Metadata Types, and inspecting an individual type by its id. For more information see the [Extended Metadata Type definitions](api#tag/extendedMetadataTypes).

    The version of the OpenAPI document: 0.3
    Contact: support@fair-dom.org
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import json
import pprint
from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError, field_validator
from typing import Any, List, Optional
from openapi_client.models.git_version import GitVersion
from openapi_client.models.version import Version
from pydantic import StrictStr, Field
from typing import Union, List, Set, Optional, Dict
from typing_extensions import Literal, Self

WORKFLOWRESPONSEDATAATTRIBUTESVERSIONSINNER_ONE_OF_SCHEMAS = ["GitVersion", "Version"]

class WorkflowResponseDataAttributesVersionsInner(BaseModel):
    """
    WorkflowResponseDataAttributesVersionsInner
    """
    # data type: Version
    oneof_schema_1_validator: Optional[Version] = None
    # data type: GitVersion
    oneof_schema_2_validator: Optional[GitVersion] = None
    actual_instance: Optional[Union[GitVersion, Version]] = None
    one_of_schemas: Set[str] = { "GitVersion", "Version" }

    model_config = ConfigDict(
        validate_assignment=True,
        protected_namespaces=(),
    )


    def __init__(self, *args, **kwargs) -> None:
        if args:
            if len(args) > 1:
                raise ValueError("If a position argument is used, only 1 is allowed to set `actual_instance`")
            if kwargs:
                raise ValueError("If a position argument is used, keyword arguments cannot be used.")
            super().__init__(actual_instance=args[0])
        else:
            super().__init__(**kwargs)

    @field_validator('actual_instance')
    def actual_instance_must_validate_oneof(cls, v):
        instance = WorkflowResponseDataAttributesVersionsInner.model_construct()
        error_messages = []
        match = 0
        # validate data type: Version
        if not isinstance(v, Version):
            error_messages.append(f"Error! Input type `{type(v)}` is not `Version`")
        else:
            match += 1
        # validate data type: GitVersion
        if not isinstance(v, GitVersion):
            error_messages.append(f"Error! Input type `{type(v)}` is not `GitVersion`")
        else:
            match += 1
        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when setting `actual_instance` in WorkflowResponseDataAttributesVersionsInner with oneOf schemas: GitVersion, Version. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when setting `actual_instance` in WorkflowResponseDataAttributesVersionsInner with oneOf schemas: GitVersion, Version. Details: " + ", ".join(error_messages))
        else:
            return v

    @classmethod
    def from_dict(cls, obj: Union[str, Dict[str, Any]]) -> Self:
        return cls.from_json(json.dumps(obj))

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Returns the object represented by the json string"""
        instance = cls.model_construct()
        error_messages = []
        match = 0

        # deserialize data into Version
        try:
            instance.actual_instance = Version.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into GitVersion
        try:
            instance.actual_instance = GitVersion.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))

        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when deserializing the JSON string into WorkflowResponseDataAttributesVersionsInner with oneOf schemas: GitVersion, Version. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when deserializing the JSON string into WorkflowResponseDataAttributesVersionsInner with oneOf schemas: GitVersion, Version. Details: " + ", ".join(error_messages))
        else:
            return instance

    def to_json(self) -> str:
        """Returns the JSON representation of the actual instance"""
        if self.actual_instance is None:
            return "null"

        if hasattr(self.actual_instance, "to_json") and callable(self.actual_instance.to_json):
            return self.actual_instance.to_json()
        else:
            return json.dumps(self.actual_instance)

    def to_dict(self) -> Optional[Union[Dict[str, Any], GitVersion, Version]]:
        """Returns the dict representation of the actual instance"""
        if self.actual_instance is None:
            return None

        if hasattr(self.actual_instance, "to_dict") and callable(self.actual_instance.to_dict):
            return self.actual_instance.to_dict()
        else:
            # primitive type
            return self.actual_instance

    def to_str(self) -> str:
        """Returns the string representation of the actual instance"""
        return pprint.pformat(self.model_dump())


