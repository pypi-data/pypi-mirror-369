#  Quapp Platform Project
#  invocation_handler.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.data.request.invocation_request import InvocationRequest
from quapp_common.handler.handler import Handler

from ..component.backend.pennylane_invocation import PennylaneInvocation


class InvocationHandler(Handler):

    def __init__(self, request_data: dict, circuit_preparation_fn,
            post_processing_fn):
        super().__init__(request_data, post_processing_fn)
        self.circuit_preparation_fn = circuit_preparation_fn

        # Initialization logging
        self.logger.info(
                f'InvocationHandler initialized | has_circuit_prep={circuit_preparation_fn is not None} '
                f'| has_post_processing={post_processing_fn is not None}')
        self.logger.debug(
                f'InvocationHandler request_data keys={list(request_data.keys()) if isinstance(request_data, dict) else "n/a"}')

    def handle(self):
        self.logger.info('InvocationHandler.handle() invoked')

        try:
            self.logger.debug('Parsing InvocationRequest from request_data')
            invocation_request = InvocationRequest(self.request_data)
            self.logger.info('InvocationRequest created successfully')
        except Exception as exception:
            self.logger.exception(
                f'Failed to create InvocationRequest: {exception}')
            raise

        try:
            self.logger.debug('Creating PennylaneInvocation backend')
            backend = PennylaneInvocation(invocation_request)
            self.logger.info('PennylaneInvocation backend created')
        except Exception as exception:
            self.logger.exception(f'Failed to create backend: {exception}')
            raise

        try:
            self.logger.info('Submitting job to backend')
            backend.submit_job(
                    circuit_preparation_fn=self.circuit_preparation_fn,
                    post_processing_fn=self.post_processing_fn)
            self.logger.info('Job submission succeeded')
        except Exception as exception:
            self.logger.exception(f'Job submission failed: {exception}')
            raise
