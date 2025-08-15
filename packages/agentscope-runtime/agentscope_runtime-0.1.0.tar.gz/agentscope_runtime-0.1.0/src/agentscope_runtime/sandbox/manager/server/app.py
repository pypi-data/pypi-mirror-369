# -*- coding: utf-8 -*-
# pylint: disable=protected-access, unused-argument
import inspect
import logging
import traceback

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ...manager.server.config import settings
from ...manager.server.models import (
    ErrorResponse,
    HealthResponse,
)
from ...manager.sandbox_manager import SandboxManager
from ...model.manager_config import SandboxManagerEnvConfig
from ....version import __version__

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Runtime Manager Service",
    description="Service for managing runtime containers",
    version=__version__,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer(auto_error=False)

# Global SandboxManager instance
_runtime_manager = None
_config = SandboxManagerEnvConfig(
    container_prefix_key=settings.CONTAINER_PREFIX_KEY,
    file_system=settings.FILE_SYSTEM,
    redis_enabled=settings.REDIS_ENABLED,
    container_deployment=settings.CONTAINER_DEPLOYMENT,
    default_mount_dir=settings.DEFAULT_MOUNT_DIR,
    storage_folder=settings.STORAGE_FOLDER,
    port_range=settings.PORT_RANGE,
    pool_size=settings.POOL_SIZE,
    oss_endpoint=settings.OSS_ENDPOINT,
    oss_access_key_id=settings.OSS_ACCESS_KEY_ID,
    oss_access_key_secret=settings.OSS_ACCESS_KEY_SECRET,
    oss_bucket_name=settings.OSS_BUCKET_NAME,
    redis_server=settings.REDIS_SERVER,
    redis_port=settings.REDIS_PORT,
    redis_db=settings.REDIS_DB,
    redis_user=settings.REDIS_USER,
    redis_password=settings.REDIS_PASSWORD,
    redis_port_key=settings.REDIS_PORT_KEY,
    redis_container_pool_key=settings.REDIS_CONTAINER_POOL_KEY,
)


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Verify Bearer token"""
    if not hasattr(settings, "BEARER_TOKEN") or not settings.BEARER_TOKEN:
        logger.warning("BEARER_TOKEN not configured, skipping authentication")
        return credentials

    if credentials is None:
        logger.error("Authentication required but no token provided")
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.credentials != settings.BEARER_TOKEN:
        logger.error(
            f"Invalid token provided: {credentials.credentials[:10]}...",
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials


def get_runtime_manager():
    """Get or create the global SandboxManager instance"""
    global _runtime_manager
    if _runtime_manager is None:
        _runtime_manager = SandboxManager(
            config=_config,
            default_type=settings.DEFAULT_SANDBOX_TYPE,
        )
    return _runtime_manager


def create_endpoint(method):
    async def endpoint(
        request: Request,
        token: HTTPAuthorizationCredentials = Depends(verify_token),
    ):
        try:
            data = await request.json()
            logger.info(
                f"Calling {method.__name__} with data: {data}",
            )
            result = method(**data)
            if hasattr(result, "model_dump_json"):
                return JSONResponse(content={"data": result.model_dump_json()})
            return JSONResponse(content={"data": result})
        except Exception as e:
            logger.error(
                f"Error in {method.__name__}: {str(e)},"
                f" {traceback.format_exc()}",
            )
            raise HTTPException(status_code=500, detail=str(e)) from e

    return endpoint


def register_routes(_app, instance):
    for _, method in inspect.getmembers(
        instance,
        predicate=inspect.ismethod,
    ):
        if getattr(method, "_is_remote_wrapper", False):
            http_method = method._http_method.lower()
            path = method._path

            endpoint = create_endpoint(method)

            if http_method == "get":
                _app.get(path)(endpoint)
            elif http_method == "post":
                _app.post(path)(endpoint)
            elif http_method == "delete":
                _app.delete(path)(endpoint)


@app.on_event("startup")
async def startup_event():
    """Initialize the SandboxManager on startup"""
    get_runtime_manager()
    register_routes(app, _runtime_manager)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    global _runtime_manager
    if _runtime_manager and settings.AUTO_CLEANUP:
        _runtime_manager.cleanup()
        _runtime_manager = None


@app.get(
    "/health",
    response_model=HealthResponse,
    responses={500: {"model": ErrorResponse}},
)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=_runtime_manager.default_type.value,
    )


def main():
    """Main entry point for the Runtime Manager Service"""
    import uvicorn

    uvicorn.run(
        "agentscope_runtime.sandbox.manager.server.app:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
