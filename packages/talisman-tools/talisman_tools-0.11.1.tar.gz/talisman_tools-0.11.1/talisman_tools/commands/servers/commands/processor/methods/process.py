import asyncio
import logging
from functools import partial
from logging import Logger
from operator import itemgetter
from typing import Any, List, Optional, Sequence, Tuple, Union

from fastapi import FastAPI, HTTPException, Request

from talisman_tools.commands.servers.server_helper import log_debug_data
from talisman_tools.helper.serializers import get_serializers
from tp_interfaces.abstract import AbstractProcessor, ImmutableBaseModel
from tp_interfaces.abstract.exception import WrongRequest
from tp_interfaces.helpers.batch import AbstractModelInput, async_batch_process_inputs
from tp_interfaces.helpers.serialize import get_serializer
from tp_interfaces.logging.context import update_log_extras
from tp_interfaces.logging.time import TimeMeasurer

_logger = logging.getLogger(__name__)
serializers = get_serializers()


def register_process_docs(app: FastAPI, endpoint: str, processor: AbstractProcessor, logger: Logger = _logger):
    config_model = processor.config_type
    input_model = get_serializer(serializers, processor.input_type)
    output_model = get_serializer(serializers, processor.output_type)

    class ModelInput(AbstractModelInput):
        message: input_model
        config: config_model

        def get_message(self) -> Any:
            return self.message

        def get_config(self) -> Optional[ImmutableBaseModel]:
            return self.config

    async def process_with_config(messages: Sequence[input_model], config: config_model) -> Tuple[output_model, ...]:
        docs = tuple(message.deserialize() for message in messages)
        with update_log_extras(doc_id=[doc.id for doc in docs]):
            output_docs = await processor.process_docs(docs, config)
            return tuple(output_model.serialize(output_doc) for output_doc in output_docs)

    @app.post(endpoint, response_model=Union[List[output_model], output_model], response_model_exclude_none=True)
    async def process(request: Request, *, messages: Union[List[ModelInput], ModelInput]):
        response_post_processor = lambda x: x
        if not isinstance(messages, list):
            messages = [messages]
            response_post_processor = itemgetter(0)

        with (update_log_extras(message_id=[message.message.id for message in messages])):
            log_debug_data(logger, f"got {len(messages)} documents for processing", request)

            task_wrapper = partial(async_batch_process_inputs, inputs=messages, processor=process_with_config)
            task = asyncio.create_task(task_wrapper())

            try:
                while not task.done():
                    if await request.is_disconnected():
                        task.cancel()
                        logger.error("Client disconnected.")
                        raise HTTPException(status_code=499, detail="Client disconnected.")
                    await asyncio.sleep(0.1)  # I think we should not check disconnection more frequently
                response = await task
            except asyncio.CancelledError as e:
                logger.error("Document processing was cancelled", exc_info=e)
                raise HTTPException(status_code=499, detail=format_error_response(e))
            except WrongRequest as e:
                logger.error("WrongRequest exception while processing request", exc_info=e)
                raise HTTPException(status_code=422, detail=format_error_response(e))
            except Exception as e:
                logger.error("Exception while processing request", exc_info=e)
                raise HTTPException(status_code=500)
            log_debug_data(logger, f"processed {len(response)} documents", request)

            with TimeMeasurer("response post processing", inline_time=True, logger=_logger):
                return response_post_processor(response)


def format_error_response(e: BaseException) -> str:
    return str(e) if len(str(e)) else "Internal error: " + e.__repr__()
