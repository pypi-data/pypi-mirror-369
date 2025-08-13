import logging
from logging import Logger
from typing import Any

from fastapi import FastAPI
from pydantic.main import BaseModel

from tp_interfaces.abstract import AbstractProcessor

_logger = logging.getLogger(__name__)


def register_schema(app: FastAPI, endpoint: str, processor: AbstractProcessor, logger: Logger = _logger):
    config_model: BaseModel = processor.config_type

    @app.get(endpoint, response_model=dict[str, Any])
    async def schema() -> dict[str, Any]:
        return config_model.model_json_schema()
