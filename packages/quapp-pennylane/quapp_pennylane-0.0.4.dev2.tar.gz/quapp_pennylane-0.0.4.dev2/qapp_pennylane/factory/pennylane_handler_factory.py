"""
    QApp Platform Project pennylane_handler_factory.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""

#  Quapp Platform Project
#  pennylane_handler_factory.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.config.logging_config import logger, job_logger
from quapp_common.factory.handler_factory import HandlerFactory
from quapp_common.handler.handler import Handler

from ..handler.invocation_handler import InvocationHandler

logger = job_logger('PennylaneHandlerFactory')

class PennylaneHandlerFactory(HandlerFactory):

    @staticmethod
    def create_handler(event, circuit_preparation_fn,
            post_processing_fn) -> Handler:
        logger.debug('Creating handler')

        request_data = event.json()

        logger.debug("Create InvocationHandler")
        return InvocationHandler(
                request_data=request_data,
                circuit_preparation_fn=circuit_preparation_fn,
                post_processing_fn=post_processing_fn,
        )
