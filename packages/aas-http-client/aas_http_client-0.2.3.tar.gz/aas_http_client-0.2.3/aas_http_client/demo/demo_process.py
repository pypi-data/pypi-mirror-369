import logging
import aas_http_client.utilities.model_builder as model_builder
from aas_http_client.client import create_client_by_config, AasHttpClient
from aas_http_client.wrapper.sdk_wrapper import SdkWrapper, create_wrapper_by_config
from pathlib import Path
import json
import basyx.aas.adapter.json
import basyx.aas.model

logger = logging.getLogger(__name__)

def start():
    """Start the demo process."""

    aas_1 = _create_shell()
    aas_2 = _create_shell()
    
    client = _create_client()
    java_sdk_wrapper = _create_sdk_wrapper(Path("./aas_http_client/demo/java_server_config.json"))
    dotnet_sdk_wrapper = _create_sdk_wrapper(Path("./aas_http_client/demo/dotnet_server_config.json"))

    java_sdk_wrapper.get_shells_by_id(aas_1.id)
    dotnet_sdk_wrapper.get_shells_by_id(aas_1.id)
    
    java_sdk_wrapper.get_submodels_by_id(aas_1.id)
    dotnet_sdk_wrapper.get_submodels_by_id(aas_1.id)
    
    exist_shells = java_sdk_wrapper.get_shells()
    exist_shells = dotnet_sdk_wrapper.get_shells()
    
    for shell in exist_shells:
        logger.warning(f"Delete shell '{shell.id}'")
        java_sdk_wrapper.delete_shells_by_id(shell.id)

    java_sdk_wrapper.post_shells(aas_1)


    aas_dict_string = json.dumps(aas_2, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    aas_dict = json.loads(aas_dict_string)
    client.post_shells(aas_dict)
    
    shells = client.get_shells()

    logger.info(f"Client created successfully. {shells}")

def _create_shell() -> basyx.aas.model.AssetAdministrationShell:
    # create an AAS
    aas_short_id: str = model_builder.create_unique_short_id("poc_aas")
    aas = model_builder.create_base_ass(aas_short_id)

    # create a Submodel
    sm_short_id: str = model_builder.create_unique_short_id("poc_sm")
    submodel = model_builder.create_base_submodel(sm_short_id)

    # add Submodel to AAS
    model_builder.add_submodel_to_aas(aas, submodel)
    
    return aas

def _create_client() -> AasHttpClient:
    """Create client for java servers."""

    try:
        file = Path("./aas_http_client/demo/java_server_config.json")
        client = create_client_by_config(file, password="")
    except Exception as e:
        logger.error(f"Failed to create client for {file}: {e}")
        pass

    return client
        
def _create_sdk_wrapper(config: Path) -> SdkWrapper:
    """Create client for java servers."""

    try:
        file = config
        client = create_wrapper_by_config(file, password="")
    except Exception as e:
        logger.error(f"Failed to create client for {file}: {e}")
        pass

    return client