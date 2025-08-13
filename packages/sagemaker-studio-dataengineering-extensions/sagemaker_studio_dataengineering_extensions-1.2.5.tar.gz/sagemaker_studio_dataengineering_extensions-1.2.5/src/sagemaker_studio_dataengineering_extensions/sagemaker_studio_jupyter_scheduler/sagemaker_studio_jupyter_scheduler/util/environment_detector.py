from enum import Enum
import os
import json
import subprocess

from sagemaker_studio_jupyter_scheduler.util.constants import SAGEMAKER_RESOURCE_METADATA_FILE


class JupyterLabEnvironment(Enum):
    SAGEMAKER_STUDIO = "SageMakerStudio"
    SAGEMAKER_JUPYTERLAB = "SageMakerJupyterLab"
    VANILLA_JUPYTERLAB = "VanillaJupyterLab"
    SAGEMAKER_UNIFIED_STUDIO = "SageMakerUnifiedStudio"


class JupyterLabEnvironmentDetector:
    SAGEMAKER_JUPYTERLAB_APP_TYPE_ENVIRON = "JupyterLab"
    SAGEMAKER_STUDIO_UI_EXTENSION_NAME = "@amzn/sagemaker-ui"

    def __init__(self):
        self.current_environment = self._detect_environment()

    def _get_installed_extensions(self):
        try:
            result = subprocess.run(
                ["jupyter", "labextension", "list"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            if result.returncode != 0:
                # TODO: Add a logger to publish logs to Jupyter Server
                # self.log.error(
                #     f"An error occurred while fetching JupyterLab extensions: {result.stderr}"
                # )
                return ""
            else:
                return result.stderr
        except subprocess.CalledProcessError as e:
            # TODO: Add a logger to publish logs to Jupyter Server
            # self.log.error(
            #     f"An error occurred while fetching JupyterLab extensions: {str(e)}"
            # )
            return ""

    def _detect_environment(self):
        if (
            os.environ.get("SAGEMAKER_APP_TYPE", None)
            == self.SAGEMAKER_JUPYTERLAB_APP_TYPE_ENVIRON
        ):
            if (self._check_datazone_domain_id()):
                return JupyterLabEnvironment.SAGEMAKER_UNIFIED_STUDIO

            return JupyterLabEnvironment.SAGEMAKER_JUPYTERLAB
        if self.SAGEMAKER_STUDIO_UI_EXTENSION_NAME in self._get_installed_extensions():
            return JupyterLabEnvironment.SAGEMAKER_STUDIO
        else:
            return JupyterLabEnvironment.VANILLA_JUPYTERLAB
        
    def _check_datazone_domain_id(self):
        try:
            # This is a public contract - https://docs.aws.amazon.com/sagemaker/latest/dg/notebooks-run-and-manage-metadata.html#notebooks-run-and-manage-metadata-app
            app_metadata_file_location = SAGEMAKER_RESOURCE_METADATA_FILE
            
            # Check if file exists
            if not os.path.exists(app_metadata_file_location):
                return False
                
            # Read and parse the JSON file
            with open(app_metadata_file_location, 'r') as file:
                metadata = json.load(file)
                
            # Check if AdditionalMetadata exists and DataZoneDomainId is present
            return (
                'AdditionalMetadata' in metadata and 
                'DataZoneDomainId' in metadata['AdditionalMetadata'] and 
                metadata['AdditionalMetadata']['DataZoneDomainId'] is not None and 
                metadata['AdditionalMetadata']['DataZoneDomainId'] != ''
            )
                
        except Exception as e:
            print(f"Error reading or parsing file: {str(e)}")
            return False
