import logging

from uuid import UUID
from fastapi import APIRouter

from app.core.database import mongo_client
from app.schemas.registry import Service


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registry", tags=["Registry"])


@router.get("/services", response_model=Service)
async def get_services():
    """
    This call List available services by their name and description
    ---
    tags:
        - Registry
    parameters:
        - name: service_name
        in: path
        type: string
        required: true
        description: name of service
    responses:
        200:
        description: listed available services
        schema:
            type: object
        examples:
            application/json: |-
            [
                {
                    "name": "SERVICE NAME",
                    "description": "SERVICE DESCRIPTION"
                }
            ]

    """
    return Service(name="some_name")


@router.post("/services")
async def register_service():
    return None


@router.delete("/services")
async def deregister_service():
    """
    This call de-register a new service in database
    ---
    tags:
      - Registry
    parameters:
      - name: name
        in: post
        type: string
        required: true
        description: the service name
      - name: node_id
        in: post
        type: string
        required: true
        description: unique node ID. Must be in UUID format.
    responses:
      200:
        description: service de-registered
        schema:
          type: object
        examples:
              application/json:
                message: MESSAGE TEXT
      400:
        description: some error in input format of data
      404:
        description: service not found
    """
    return None


@router.get("/services/<service_name>")
async def get_service(service_name: str):
    """
    This call get service_name details
    ---
    tags:
        - Registry
    parameters:
        - name: service_name
        in: path
        type: string
        required: true
        description: name of service which we want the details
    responses:
        200:
        description: everything was good
        schema:
            type: object
        examples:
            application/json: |-
            [
                {
                    "name": "SERVICE NAME",
                    "description": "SERVICE DESCRIPTION",
                    "nodes":
                        [
                            {
                                "address": "IP OR DOMAIN_NAME",
                                "service_port": "PORT"
                            }
                        ]
                }
            ]
        204:
        description: service name not found
    """
    return Service(name=service_name)
