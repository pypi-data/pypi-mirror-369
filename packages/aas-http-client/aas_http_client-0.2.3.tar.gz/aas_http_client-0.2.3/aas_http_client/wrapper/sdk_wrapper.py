"""BaSyx Server interface for REST API communication."""

import json
import logging
from pathlib import Path
from typing import Any

import basyx.aas.adapter.json

from basyx.aas.model import AssetAdministrationShell, Reference, Submodel, ModelReference
from aas_http_client.client import AasHttpClient, _create_client
logger = logging.getLogger(__name__)

class SdkWrapper():
    """Represents a wrapper for the BaSyx Python SDK to communicate with a REST API."""
    _client: AasHttpClient = None

    def post_shells(self, aas: AssetAdministrationShell) -> dict | None:
        """Post an Asset Administration Shell (AAS) to the REST API.

        :param aas: Asset Administration Shell to post
        :return: Response data as a dictionary or None if an error occurred
        """
        aas_data = _to_dict(aas)
        return self._client.post_shells(aas_data)

    def put_shells(self, identifier: str, aas: AssetAdministrationShell) -> bool:
        """Update an Asset Administration Shell (AAS) by its ID in the REST API.

        :param identifier: Identifier of the AAS to update
        :param aas: Asset Administration Shell data to update
        :return: True if the update was successful, False otherwise
        """
        aas_data = _to_dict(aas)
        return self._client.put_shells(identifier, aas_data)

    def put_shells_submodels_by_id(self, aas_id: str, submodel_id: str, submodel: Submodel) -> bool:
        """Update a submodel by its ID for a specific Asset Administration Shell (AAS).

        :param aas_id: ID of the AAS to update the submodel for
        :param submodel: Submodel data to update
        :return: True if the update was successful, False otherwise
        """
        sm_data = _to_dict(submodel)
        return self._client.put_shells_submodels_by_id(aas_id, submodel_id, sm_data)

    def get_shells(self) -> list[AssetAdministrationShell] | None:
        """Get all Asset Administration Shells (AAS) from the REST API.

        :return: AAS objects or None if an error occurred
        """
        content: dict = self._client.get_shells()
        
        if not content:
            return None

        results: list = content.get("result", [])
        if not results:
            logger.warning("No shells found on server.")
            return []

        aas_list: list[AssetAdministrationShell] = []

        for result in results:
            if not isinstance(result, dict):
                logger.error(f"Invalid shell data: {result}")
                return None

            aas = _to_object(result)

            if aas:
                aas_list.append(aas)

        return aas_list

    def get_shells_by_id(self, aas_id: str) -> AssetAdministrationShell | None:
        """Get an Asset Administration Shell (AAS) by its ID from the REST API.

        :param aas_id: ID of the AAS to retrieve
        :return: AAS object or None if an error occurred
        """
        content: dict = self._client.get_shells_by_id(aas_id)
        
        if not content:
            logger.warning(f"No shell found with ID '{aas_id}' on server.")
            return None
        
        return _to_object(content)

    def get_shells_reference_by_id(self, aas_id: str) -> Reference | None:
        #workaround because serialization not working
        aas = self.get_shells_by_id(aas_id)
        return ModelReference.from_referable(aas)
        
        # content: dict = self._client.get_shells_reference_by_id(aas_id)
        # return json.loads(content, cls=basyx.aas.adapter.json.AASFromJsonDecoder)

    def get_shells_submodels_by_id(self, aas_id: str, submodel_id: str) -> Submodel | None:
        """Get a submodel by its ID for a specific Asset Administration Shell (AAS).

        :param aas_id: ID of the AAS to retrieve the submodel from
        :param submodel_id: ID of the submodel to retrieve
        :return: Submodel object or None if an error occurred
        """
        content: dict = self._client.get_shells_submodels_by_id(aas_id, submodel_id)
        return _to_object(content)

    def delete_shells_by_id(self, aas_id: str) -> bool:
        """Get an Asset Administration Shell (AAS) by its ID from the REST API.

        :param aas_id: ID of the AAS to retrieve
        :return: True if the deletion was successful, False otherwise
        """
        return self._client.delete_shells_by_id(aas_id)

    def post_submodels(self, submodel: Submodel) -> bool:
        """Post a submodel to the REST API.

        :param submodel: submodel data as a dictionary
        :return: Response data as a dictionary or None if an error occurred
        """
        sm_data = _to_dict(submodel)
        return self._client.post_submodels(sm_data)

    def put_submodels_by_id(self, identifier: str, submodel: Submodel) -> bool:
        """Update a submodel by its ID in the REST API.

        :param identifier: Identifier of the submodel to update
        :param submodel: Submodel data to update
        :return: True if the update was successful, False otherwise
        """
        sm_data = _to_dict(submodel)
        return self._client.put_submodels_by_id(identifier, sm_data)

    def get_submodels(self) -> list[Submodel] | None:
        """Get all submodels from the REST API.

        :return: Submodel objects or None if an error occurred
        """
        content: list = self._client.get_submodels()

        if not content:
            return []

        results: list = content.get("result", [])
        if not results:
            logger.warning("No submodels found on server.")
            return []

        submodels: list[Submodel] = []

        for result in results:
            if not isinstance(result, dict):
                logger.error(f"Invalid submodel data: {result}")
                return None

            submodel = _to_object(result)

            if submodel:
                submodels.append(submodel)

        return submodels

    def get_submodels_by_id(self, submodel_id: str) -> Submodel | None:
        """Get a submodel by its ID from the REST API.

        :param submodel_id: ID of the submodel to retrieve
        :return: Submodel object or None if an error occurred
        """
        content = self._client.get_submodels_by_id(submodel_id)

        if not content:
            logger.warning(f"No submodel found with ID '{submodel_id}' on server.")
            return None
        
        return _to_object(content)

    def patch_submodel_by_id(self, submodel_id: str, submodel: Submodel):
        sm_data = _to_dict(submodel)
        return self._client.patch_submodel_by_id(submodel_id, sm_data)

    def delete_submodels_by_id(self, submodel_id: str) -> bool:
        """Delete a submodel by its ID from the REST API.

        :param submodel_id: ID of the submodel to delete
        :return: True if the deletion was successful, False otherwise
        """
        return self._client.delete_submodels_by_id(submodel_id)

def _to_object(content: dict) -> Any | None:
    try:
        dict_string = json.dumps(content)
        return json.loads(dict_string, cls=basyx.aas.adapter.json.AASFromJsonDecoder)
    except Exception as e:
        logger.error(f"Decoding error: {e}")
        logger.error(f"In JSON: {content}")
        return None
    
def _to_dict(object: Any) -> dict | None:
    try:
        data_string = json.dumps(object, cls=basyx.aas.adapter.json.AASToJsonEncoder)
        return json.loads(data_string)
    except Exception as e:
        logger.error(f"Encoding error: {e}")
        logger.error(f"In object: {object}")
        return None    

def create_wrapper_by_url(
    base_url: str,
    username: str = "",
    password: str = "",
    http_proxy: str = "",
    https_proxy: str = "",
    time_out: int = 200,
    connection_time_out: int = 60,
    ssl_verify: str = True,  # noqa: FBT002
) -> SdkWrapper | None:
    """Create a wrapper for the BaSyx Python SDK from the given parameters.

    :param base_url: base URL of the BaSyx server, e.g. "http://basyx_python_server:80/"_
    :param username: username for the BaSyx server interface client, defaults to ""_
    :param password: password for the BaSyx server interface client, defaults to ""_
    :param http_proxy: http proxy URL, defaults to ""_
    :param https_proxy: https proxy URL, defaults to ""_
    :param time_out: timeout for the API calls, defaults to 200
    :param connection_time_out: timeout for the connection to the API, defaults to 60
    :param ssl_verify: whether to verify SSL certificates, defaults to True
    :return: An instance of SdkWrapper initialized with the provided parameters.
    """
    logger.info(f"Create BaSyx Python SDK wrapper from URL '{base_url}'")
    config_dict: dict[str, str] = {}
    config_dict["base_url"] = base_url
    config_dict["username"] = username
    config_dict["http_proxy"] = http_proxy
    config_dict["https_proxy"] = https_proxy
    config_dict["time_out"] = time_out
    config_dict["connection_time_out"] = connection_time_out
    config_dict["ssl_verify"] = ssl_verify
    config_string = json.dumps(config_dict, indent=4)
    
    wrapper = SdkWrapper()
    client = _create_client(config_string, password)      
    
    if not client:
        return None
    
    wrapper._client = client          
    return wrapper
    


def create_wrapper_by_config(config_file: Path, password: str = "") -> SdkWrapper | None:
    """Create a wrapper for the BaSyx Python SDK from the given parameters.

    :param config_file: Path to the configuration file containing the BaSyx server connection settings.
    :param password: password for the BaSyx server interface client, defaults to ""_
    :return: An instance of SdkWrapper initialized with the provided parameters.
    """
    logger.info(f"Create BaSyx Python SDK wrapper from configuration file '{config_file}'")
    if not config_file.exists():
        config_string = "{}"
        logger.warning(f"Configuration file '{config_file}' not found. Using default config.")
    else:
        config_string = config_file.read_text(encoding="utf-8")
        logger.debug(f"Configuration file '{config_file}' found.")

    wrapper = SdkWrapper()
    client = _create_client(config_string, password)
    
    if not client:
        return None
    
    wrapper._client = client       
    return wrapper