# -*- coding: utf-8 -*-
import traceback
import logging

import docker
from .base_client import BaseClient


logger = logging.getLogger(__name__)


class DockerClient(BaseClient):
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            raise RuntimeError(
                f"Docker client initialization failed: {str(e)}\n"
                "Solutions:\n"
                "• Ensure Docker is running\n"
                "• Check Docker permissions\n"
                "• For Colima: "
                "export DOCKER_HOST=unix://$HOME/.colima/docker.sock",
            ) from e

    def _try_pull_from_acr(self, image):
        """
        Attempt to pull the image from the Alibaba Cloud Container Registry
        (ACR) and retag it.
        """
        try:
            acr_registry = "agentscope-registry.ap-southeast-1.cr.aliyuncs.com"
            acr_image = f"{acr_registry}/{image}"

            logger.debug(f"Attempting to pull from ACR: {acr_image}")
            self.client.images.pull(acr_image)
            logger.debug(f"Successfully pulled image from ACR: {acr_image}")

            # Retag the image
            acr_img_obj = self.client.images.get(acr_image)
            acr_img_obj.tag(image)
            logger.debug(f"Successfully tagged image as: {image}")

            # Optionally remove the original tag to save space
            try:
                self.client.images.remove(acr_image)
                logger.debug(f"Removed original tag: {acr_image}")
            except Exception as e:
                logger.debug(f"Failed to remove original tag: {e}")
            return True
        except Exception as e:
            logger.error(f"Failed to pull from ACR: {e}")
            return False

    def create(
        self,
        image,
        name=None,
        ports=None,
        volumes=None,
        environment=None,
        runtime_config=None,
    ):
        """Create a new Docker container."""
        if runtime_config is None:
            runtime_config = {}

        try:
            try:
                # Check if the image exists locally
                self.client.images.get(image)
                logger.debug(f"Image '{image}' found locally.")
            except docker.errors.ImageNotFound:
                logger.debug(
                    f"Image '{image}' not found locally. "
                    f"Attempting to pull it...",
                )
                try:
                    self.client.images.pull(image)
                    logger.debug(
                        f"Image '{image}' successfully pulled from default "
                        f"registry.",
                    )
                    pull_success = True
                except docker.errors.APIError as e:
                    logger.warning(
                        f"Failed to pull from default registry: {e}",
                    )
                    logger.debug("Trying to pull from ACR fallback...")
                    pull_success = self._try_pull_from_acr(image)

                if not pull_success:
                    logger.error(
                        f"Failed to pull image '{image}' from both "
                        f"default and ACR",
                    )
                    return False

            except docker.errors.APIError as e:
                logger.error(f"Error occurred while checking the image: {e}")
                return False

            # Create and run the container
            container = self.client.containers.run(
                image,
                detach=True,
                ports=ports,
                name=name,
                volumes=volumes,
                environment=environment,
                **runtime_config,
            )
            container.reload()
            return True
        except Exception as e:
            logger.error(f"An error occurred: {e}, {traceback.format_exc()}")
            return False

    def start(self, container_id):
        """Start a Docker container."""
        try:
            container = self.client.containers.get(
                container_id,
            )
            container.start()
            return True
        except Exception as e:
            logger.error(f"An error occurred: {e}, {traceback.format_exc()}")
            return False

    def stop(self, container_id, timeout=None):
        """Stop a Docker container."""
        try:
            container = self.client.containers.get(
                container_id,
            )
            container.stop(timeout=timeout)
            return True
        except Exception as e:
            logger.error(f"An error occurred: {e}, {traceback.format_exc()}")
            return False

    def remove(self, container_id, force=False):
        """Remove a Docker container."""
        try:
            container = self.client.containers.get(
                container_id,
            )
            container.remove(force=force)
            return True
        except Exception as e:
            logger.error(f"An error occurred: {e}, {traceback.format_exc()}")
            return False

    def inspect(self, container_id):
        """Inspect a Docker container."""
        try:
            # Get the container object
            container = self.client.containers.get(container_id)
            # Access the detailed information
            return container.attrs
        except Exception:
            return None

    def get_status(self, container_id):
        """Get the current status of the specified container."""
        container_attrs = self.inspect(container_id=container_id)
        if container_attrs:
            return container_attrs["State"]["Status"]
        return None
