# coding: utf-8

"""
    JSON API to FAIRDOM SEEK

    <a name=\"api\"></a>The JSON API to FAIRDOM SEEK is a [JSON API](http://jsonapi.org) specification describing how to read and write to a SEEK instance.  The API is defined in the [OpenAPI specification](https://swagger.io/specification) currently in [version 2](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md)  Example IPython notebooks showing use of the API are available on [GitHub](https://github.com/FAIRdom/api-workshop)  ## Policy <a name=\"Policy\"></a> A Policy specifies the visibility of an object to people using SEEK. A <a href=\"#projects\">**Project**</a> may specify the default policy for objects belonging to that <a href=\"#projects\">**Project**</a>  The **Policy** specifies the visibility of the object to non-registered people or <a href=\"#people\">**People**</a> not allowed special access.  The access may be one of (in order of increasing \"power\"):  * no_access * view * download * edit * manage  In addition a **Policy** may give special access to specific <a href=\"#people\">**People**</a>, People working at an <a href=\"#institutions\">**Institution**</a> or working on a <a href=\"#projects\">**Project**</a>.  ## License <a name=\"License\"></a> The license specifies the license that will apply to any <a href=\"#dataFiles\">**DataFiles**</a>, <a href=\"#models\">**Models**</a>, <a href=\"#sops\">**SOPs**</a>, <a href=\"#documents\">**Documents**</a> and <a href=\"#presentations\">**Presentations**</a> associated with a <a href=\"#projects\">**Project**</a>.  The license can currently be:  * `CC0-1.0` - [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) * `CC-BY-4.0` - [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/) * `CC-BY-SA-4.0` - [Creative Commons Attribution Share-Alike 4.0](https://creativecommons.org/licenses/by-sa/4.0/) * `ODC-BY-1.0` - [Open Data Commons Attribution License 1.0](http://www.opendefinition.org/licenses/odc-by) * `ODbL-1.0` - [Open Data Commons Open Database License 1.0](http://www.opendefinition.org/licenses/odc-odbl) * `ODC-PDDL-1.0` - [Open Data Commons Public Domain Dedication and Licence 1.0](http://www.opendefinition.org/licenses/odc-pddl) * `notspecified` - License Not Specified * `other-at` - Other (Attribution) * `other-open` - Other (Open) * `other-pd` - Other (Public Domain) * `AFL-3.0` - [Academic Free License 3.0](http://www.opensource.org/licenses/AFL-3.0) * `Against-DRM` - [Against DRM](http://www.opendefinition.org/licenses/against-drm) * `CC-BY-NC-4.0` - [Creative Commons Attribution-NonCommercial 4.0](https://creativecommons.org/licenses/by-nc/4.0/) * `DSL` - [Design Science License](http://www.opendefinition.org/licenses/dsl) * `FAL-1.3` - [Free Art License 1.3](http://www.opendefinition.org/licenses/fal) * `GFDL-1.3-no-cover-texts-no-invariant-sections` - [GNU Free Documentation License 1.3 with no cover texts and no invariant sections](http://www.opendefinition.org/licenses/gfdl) * `geogratis` - [Geogratis](http://geogratis.gc.ca/geogratis/licenceGG) * `hesa-withrights` - [Higher Education Statistics Agency Copyright with data.gov.uk rights](http://www.hesa.ac.uk/index.php?option=com_content&amp;task=view&amp;id=2619&amp;Itemid=209) * `localauth-withrights` - Local Authority Copyright with data.gov.uk rights * `MirOS` - [MirOS Licence](http://www.opensource.org/licenses/MirOS) * `NPOSL-3.0` - [Non-Profit Open Software License 3.0](http://www.opensource.org/licenses/NPOSL-3.0) * `OGL-UK-1.0` - [Open Government Licence 1.0 (United Kingdom)](http://reference.data.gov.uk/id/open-government-licence) * `OGL-UK-2.0` - [Open Government Licence 2.0 (United Kingdom)](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/) * `OGL-UK-3.0` - [Open Government Licence 3.0 (United Kingdom)](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) * `OGL-Canada-2.0` - [Open Government License 2.0 (Canada)](http://data.gc.ca/eng/open-government-licence-canada) * `OSL-3.0` - [Open Software License 3.0](http://www.opensource.org/licenses/OSL-3.0) * `dli-model-use` - [Statistics Canada: Data Liberation Initiative (DLI) - Model Data Use Licence](http://data.library.ubc.ca/datalib/geographic/DMTI/license.html) * `Talis` - [Talis Community License](http://www.opendefinition.org/licenses/tcl) * `ukclickusepsi` - UK Click Use PSI * `ukcrown-withrights` - UK Crown Copyright with data.gov.uk rights * `ukpsi` - [UK PSI Public Sector Information](http://www.opendefinition.org/licenses/ukpsi)  ## ContentBlob <a name=\"ContentBlob\"></a> <a name=\"contentBlobs\"></a> The content of a <a href=\"#dataFiles\">**DataFile**</a>, <a href=\"#documents\">**Document**</a>, <a href=\"#models\">**Model**</a>, <a href=\"#sops\">**SOP**</a> or <a href=\"#presentations\">**Presentation**</a> is specified as a set of **ContentBlobs**.  When a resource with content is created, it is possible to specify a ContentBlob either as:  * A remote ContentBlob with:   * **URI to the content's location**   * The original filename for the content   * The content type of the remote content as a [MIME media type](https://en.wikipedia.org/wiki/Media_type) * A placeholder that will be filled with uploaded content   * **The original filename for the content**   * **The content type of the content as a [MIME media type](https://en.wikipedia.org/wiki/Media_type)**  The creation of the resource will return a JSON document containing ContentBlobs corresponding to the remote ContentBlob and to the ContentBlob placeholder. The blobs contain a URI to their location.  A placeholder can then be satisfied by uploading a file to the location URI. For example by a placeholder such as   ``` \"content_blobs\": [   {     \"original_filename\": \"a_pdf_file.pdf\",     \"content_type\": \"application/pdf\",     \"link\": \"http://fairdomhub.org/data_files/57/content_blobs/313\"   } ], ```  may be satisfied by uploading a file to http://fairdomhub.org/data_files/57/content_blobs/313 using the <a href=\"#uploadAssetContent\">uploadAssetContent</a> operation  The content of a resource may be downloaded by first *reading* the resource and then *downloading* the ContentBlobs from their URI.  ## Extended Metadata  Some types support [Extended Metadata](https://docs.seek4science.org/tech/extended-metadata), which allows additional attributes to be defined according to an Extended Metadata Type.  Types currently supported are <a href=\"#investigations\">**Investigation**</a>, <a href=\"#studies\">**Study**</a>, <a href=\"#assays\">**Assay**</a>,  <a href=\"#dataFiles\">**DataFile**</a>, <a href=\"#sops\">**SOP**</a>, <a href=\"#presentations\">**Presentation**</a>, <a href=\"#documents\">**Document**</a>, <a href=\"#models\">**Model**</a>, <a href=\"#events\">**Event**</a>, <a href=\"#collections\">**Collection**</a>, <a href=\"#projects\">**Project**</a>  The responses and requests for each of these types include an additional optional attribute _extended_attributes_ which describes  * _extended_metadata_type_id_ - the id of the extended metadata type which can be used to find more details about what its attributes are. * _attribute_map_ - which is a map of key / value pairs where the key is the attribute name   For example, a Study may have extended metadata, defined by an Extended Metadata Type with id 12, that has attributes for age, name, and date_of_birth. These could be shown, within its attributes, as:  ``` \"extended_attributes\": {   \"extended_metadata_type_id\": \"12\",   \"attribute_map\": {     \"age\": 44,     \"name\": \"Fred Bloggs\",     \"date_of_birth\": \"2024-01-01\"   } } ```  If you wish to create or update a study to make use of this extended metadata, the request payload would be described the same.  Upon creation or update there would be a validation check that the attributes are valid.  The API supports listing all available Extended Metadata Types, and inspecting an individual type by its id. For more information see the [Extended Metadata Type definitions](api#tag/extendedMetadataTypes).

    The version of the OpenAPI document: 0.3
    Contact: support@fair-dom.org
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import io
import json
import re
import ssl

import urllib3

from openapi_client.exceptions import ApiException, ApiValueError

SUPPORTED_SOCKS_PROXIES = {"socks5", "socks5h", "socks4", "socks4a"}
RESTResponseType = urllib3.HTTPResponse


def is_socks_proxy_url(url):
    if url is None:
        return False
    split_section = url.split("://")
    if len(split_section) < 2:
        return False
    else:
        return split_section[0].lower() in SUPPORTED_SOCKS_PROXIES


class RESTResponse(io.IOBase):

    def __init__(self, resp) -> None:
        self.response = resp
        self.status = resp.status
        self.reason = resp.reason
        self.data = None

    def read(self):
        if self.data is None:
            self.data = self.response.data
        return self.data

    def getheaders(self):
        """Returns a dictionary of the response headers."""
        return self.response.headers

    def getheader(self, name, default=None):
        """Returns a given response header."""
        return self.response.headers.get(name, default)


class RESTClientObject:

    def __init__(self, configuration) -> None:
        # urllib3.PoolManager will pass all kw parameters to connectionpool
        # https://github.com/shazow/urllib3/blob/f9409436f83aeb79fbaf090181cd81b784f1b8ce/urllib3/poolmanager.py#L75  # noqa: E501
        # https://github.com/shazow/urllib3/blob/f9409436f83aeb79fbaf090181cd81b784f1b8ce/urllib3/connectionpool.py#L680  # noqa: E501
        # Custom SSL certificates and client certificates: http://urllib3.readthedocs.io/en/latest/advanced-usage.html  # noqa: E501

        # cert_reqs
        if configuration.verify_ssl:
            cert_reqs = ssl.CERT_REQUIRED
        else:
            cert_reqs = ssl.CERT_NONE

        pool_args = {
            "cert_reqs": cert_reqs,
            "ca_certs": configuration.ssl_ca_cert,
            "cert_file": configuration.cert_file,
            "key_file": configuration.key_file,
            "ca_cert_data": configuration.ca_cert_data,
        }
        if configuration.assert_hostname is not None:
            pool_args['assert_hostname'] = (
                configuration.assert_hostname
            )

        if configuration.retries is not None:
            pool_args['retries'] = configuration.retries

        if configuration.tls_server_name:
            pool_args['server_hostname'] = configuration.tls_server_name


        if configuration.socket_options is not None:
            pool_args['socket_options'] = configuration.socket_options

        if configuration.connection_pool_maxsize is not None:
            pool_args['maxsize'] = configuration.connection_pool_maxsize

        # https pool manager
        self.pool_manager: urllib3.PoolManager

        if configuration.proxy:
            if is_socks_proxy_url(configuration.proxy):
                from urllib3.contrib.socks import SOCKSProxyManager
                pool_args["proxy_url"] = configuration.proxy
                pool_args["headers"] = configuration.proxy_headers
                self.pool_manager = SOCKSProxyManager(**pool_args)
            else:
                pool_args["proxy_url"] = configuration.proxy
                pool_args["proxy_headers"] = configuration.proxy_headers
                self.pool_manager = urllib3.ProxyManager(**pool_args)
        else:
            self.pool_manager = urllib3.PoolManager(**pool_args)

    def request(
        self,
        method,
        url,
        headers=None,
        body=None,
        post_params=None,
        _request_timeout=None
    ):
        """Perform requests.

        :param method: http request method
        :param url: http request url
        :param headers: http request headers
        :param body: request json body, for `application/json`
        :param post_params: request post parameters,
                            `application/x-www-form-urlencoded`
                            and `multipart/form-data`
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        """
        method = method.upper()
        assert method in [
            'GET',
            'HEAD',
            'DELETE',
            'POST',
            'PUT',
            'PATCH',
            'OPTIONS'
        ]

        if post_params and body:
            raise ApiValueError(
                "body parameter cannot be used with post_params parameter."
            )

        post_params = post_params or {}
        headers = headers or {}

        timeout = None
        if _request_timeout:
            if isinstance(_request_timeout, (int, float)):
                timeout = urllib3.Timeout(total=_request_timeout)
            elif (
                    isinstance(_request_timeout, tuple)
                    and len(_request_timeout) == 2
                ):
                timeout = urllib3.Timeout(
                    connect=_request_timeout[0],
                    read=_request_timeout[1]
                )

        try:
            # For `POST`, `PUT`, `PATCH`, `OPTIONS`, `DELETE`
            if method in ['POST', 'PUT', 'PATCH', 'OPTIONS', 'DELETE']:

                # no content type provided or payload is json
                content_type = headers.get('Content-Type')
                if (
                    not content_type
                    or re.search('json', content_type, re.IGNORECASE)
                ):
                    request_body = None
                    if body is not None:
                        request_body = json.dumps(body)
                    r = self.pool_manager.request(
                        method,
                        url,
                        body=request_body,
                        timeout=timeout,
                        headers=headers,
                        preload_content=False
                    )
                elif content_type == 'application/x-www-form-urlencoded':
                    r = self.pool_manager.request(
                        method,
                        url,
                        fields=post_params,
                        encode_multipart=False,
                        timeout=timeout,
                        headers=headers,
                        preload_content=False
                    )
                elif content_type == 'multipart/form-data':
                    # must del headers['Content-Type'], or the correct
                    # Content-Type which generated by urllib3 will be
                    # overwritten.
                    del headers['Content-Type']
                    # Ensures that dict objects are serialized
                    post_params = [(a, json.dumps(b)) if isinstance(b, dict) else (a,b) for a, b in post_params]
                    r = self.pool_manager.request(
                        method,
                        url,
                        fields=post_params,
                        encode_multipart=True,
                        timeout=timeout,
                        headers=headers,
                        preload_content=False
                    )
                # Pass a `string` parameter directly in the body to support
                # other content types than JSON when `body` argument is
                # provided in serialized form.
                elif isinstance(body, str) or isinstance(body, bytes):
                    r = self.pool_manager.request(
                        method,
                        url,
                        body=body,
                        timeout=timeout,
                        headers=headers,
                        preload_content=False
                    )
                elif headers['Content-Type'].startswith('text/') and isinstance(body, bool):
                    request_body = "true" if body else "false"
                    r = self.pool_manager.request(
                        method,
                        url,
                        body=request_body,
                        preload_content=False,
                        timeout=timeout,
                        headers=headers)
                else:
                    # Cannot generate the request from given parameters
                    msg = """Cannot prepare a request message for provided
                             arguments. Please check that your arguments match
                             declared content type."""
                    raise ApiException(status=0, reason=msg)
            # For `GET`, `HEAD`
            else:
                r = self.pool_manager.request(
                    method,
                    url,
                    fields={},
                    timeout=timeout,
                    headers=headers,
                    preload_content=False
                )
        except urllib3.exceptions.SSLError as e:
            msg = "\n".join([type(e).__name__, str(e)])
            raise ApiException(status=0, reason=msg)

        return RESTResponse(r)
