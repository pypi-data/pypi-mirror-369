import unittest
from unittest.mock import patch, Mock

from sagemaker_studio_jupyter_scheduler.util.environment_detector import (
    JupyterLabEnvironmentDetector,
    JupyterLabEnvironment,
)


class TestJupyterLabEnvironmentDetector(unittest.TestCase):
    @patch("subprocess.run")
    def test_get_installed_extensions_success(self, mock_subprocess):
        mock_subprocess.return_value = Mock(
            returncode=0,
            stderr="@amzn/sagemaker-ui v5.1007.2 enabled OK (python, amzn_sagemaker_ui)",
        )

        detector = JupyterLabEnvironmentDetector()
        result = detector._get_installed_extensions()

        self.assertEqual(
            result,
            "@amzn/sagemaker-ui v5.1007.2 enabled OK (python, amzn_sagemaker_ui)",
        )

    @patch("subprocess.run")
    def test_get_installed_extensions_failure(self, mock_subprocess):
        mock_subprocess.return_value = Mock(returncode=1, stderr="Error occurred.")

        detector = JupyterLabEnvironmentDetector()
        result = detector._get_installed_extensions()

        self.assertEqual(result, "")

    @patch("subprocess.run")
    def test_detect_environment_sagemaker(self, mock_subprocess):
        mock_subprocess.return_value = Mock(
            returncode=0,
            stderr="@amzn/sagemaker-ui v5.1007.2 enabled OK (python, amzn_sagemaker_ui)",
        )

        detector = JupyterLabEnvironmentDetector()
        environment = detector._detect_environment()

        self.assertEqual(environment, JupyterLabEnvironment.SAGEMAKER_STUDIO)

    @patch("subprocess.run")
    def test_detect_environment_vanilla(self, mock_subprocess):
        mock_subprocess.return_value = Mock(returncode=0, stderr="")

        detector = JupyterLabEnvironmentDetector()
        environment = detector._detect_environment()

        self.assertEqual(environment, JupyterLabEnvironment.VANILLA_JUPYTERLAB)
