import logging

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_mongo_db, mongo_client
from app.schemas.registry import ServiceRegister, ServiceResponse
from app.schemas.commands import RegisterServiceCommand

from app.core.message_bus import MessageBus, get_message_bus


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/registry", tags=["Registry"])


@router.get("/services", response_model=ServiceResponse)
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
    return ServiceResponse(name="some_name")


@router.post("/services")
async def register_service(
    service_data: ServiceRegister,
    mongo=Depends(get_mongo_db),
    bus: MessageBus = Depends(get_message_bus),
):
    """
    This call register a new service in database
    ---
    tags:
      - Registry
    parameters:
      - name: name
        in: post
        type: string
        required: true
        description: the service name
      - name: address
        in: post
        type: string
        required: true
        description: service address (IP or domain name)
      - name: service_port
        in: post
        type: string
        required: true
        description: service port for communicate to with
      - name: node_id
        in: post
        type: string
        required: true
        description: unique node ID. Must be in UUID format.
    responses:
      201:
        description: service added
        schema:
          type: object
        examples:
              application/json:
                message: MESSAGE TEXT
      400:
        description: some error in input format of data
      409:
        description: service already exits
    """
    command = RegisterServiceCommand()

    try:
        result = await bus.execute_command(command, mongo=mongo)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register service: {str(e)}",
        )


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
    return ServiceResponse(name=service_name)
