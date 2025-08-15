# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging

from nemo_deploy.ray_utils import find_available_port
from nemo_export_deploy_common.import_utils import MISSING_RAY_MSG, UnavailableError

try:
    import ray
    from ray import serve
    from ray.serve import Application

    HAVE_RAY = True
except (ImportError, ModuleNotFoundError):
    from unittest.mock import MagicMock

    ray = MagicMock()
    serve = MagicMock()
    Application = MagicMock()
    HAVE_RAY = False

LOGGER = logging.getLogger("NeMo")


class DeployRay:
    """A class for managing Ray deployment and serving of models.

    This class provides functionality to initialize Ray, start Ray Serve,
    deploy models, and manage the lifecycle of the Ray cluster.

    Attributes:
        address (str): The address of the Ray cluster to connect to.
        num_cpus (int): Number of CPUs to allocate for the Ray cluster.
        num_gpus (int): Number of GPUs to allocate for the Ray cluster.
        include_dashboard (bool): Whether to include the Ray dashboard.
        ignore_reinit_error (bool): Whether to ignore errors when reinitializing Ray.
        runtime_env (dict): Runtime environment configuration for Ray.
    """

    def __init__(
        self,
        address: str = "auto",
        num_cpus: int = 1,
        num_gpus: int = 1,
        include_dashboard: bool = False,
        ignore_reinit_error: bool = True,
        runtime_env: dict = None,
    ):
        """Initialize the DeployRay instance and set up the Ray cluster.

        Args:
            address (str, optional): Address of the Ray cluster. Defaults to "auto".
            num_cpus (int, optional): Number of CPUs to allocate. Defaults to 1.
            num_gpus (int, optional): Number of GPUs to allocate. Defaults to 1.
            include_dashboard (bool, optional): Whether to include the dashboard. Defaults to False.
            ignore_reinit_error (bool, optional): Whether to ignore reinit errors. Defaults to True.
            runtime_env (dict, optional): Runtime environment configuration. Defaults to None.

        Raises:
            Exception: If Ray is not installed.
        """
        if not HAVE_RAY:
            raise UnavailableError(MISSING_RAY_MSG)

        # Initialize Ray with proper configuration

        try:
            # Try to connect to existing Ray cluster
            ray.init(
                address=address,
                ignore_reinit_error=ignore_reinit_error,
                runtime_env=runtime_env,
            )
        except ConnectionError:
            # If no cluster exists, start a local one
            LOGGER.info("No existing Ray cluster found. Starting a local Ray cluster...")
            ray.init(
                num_cpus=num_cpus,
                num_gpus=num_gpus,
                include_dashboard=include_dashboard,
                ignore_reinit_error=ignore_reinit_error,
                runtime_env=runtime_env,
            )

    def start(self, host: str = "0.0.0.0", port: int = None):
        """Start Ray Serve with the specified host and port.

        Args:
            host (str, optional): Host address to bind to. Defaults to "0.0.0.0".
            port (int, optional): Port number to use. If None, an available port will be found.
        """
        if not port:
            port = find_available_port(8000, host)
        serve.start(
            http_options={
                "host": host,
                "port": port,
            }
        )

    def run(self, app: Application, model_name: str):
        """Deploy and start serving a model using Ray Serve.

        Args:
            app (Application): The Ray Serve application to deploy.
            model_name (str): Name to give to the deployed model.
        """
        serve.run(app, name=model_name)

    def stop(self):
        """Stop the Ray Serve deployment and shutdown the Ray cluster.

        This method attempts to gracefully shutdown both Ray Serve and the Ray cluster.
        If any errors occur during shutdown, they are logged as warnings.
        """
        try:
            # First try to gracefully shutdown Ray Serve
            LOGGER.info("Shutting down Ray Serve...")
            serve.shutdown()
        except Exception as e:
            LOGGER.warning(f"Error during serve.shutdown(): {str(e)}")
        try:
            # Then try to gracefully shutdown Ray
            LOGGER.info("Shutting down Ray...")
            ray.shutdown()
        except Exception as e:
            LOGGER.warning(f"Error during ray.shutdown(): {str(e)}")
