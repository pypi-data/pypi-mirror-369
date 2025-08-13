# """
#     QApp Platform Project
#     pennylane_device.py
#     Copyright © CITYNOW Co. Ltd. All rights reserved.
# """
# from abc import ABC
#
# from qapp_common.config.logging_config import logger
# from qapp_common.model.device.device import Device
# from qapp_common.model.provider.provider import Provider
#
#
# class PennylaneDevice(Device, ABC):
#     def _produce_histogram_data(self, job_result) -> dict | None:
#         logger.info('[PennylaneDevice] Producing histogram data')
#
#
#         try:
#             histogram_data = job_result.get_counts()
#         except Exception as pennylane_error:
#             logger.debug("[PennylaneDevice] Can't produce histogram with error: {0}".format(
#                 str(pennylane_error)))
#             histogram_data = None
#
#         return histogram_data
#
#     def _get_provider_job_id(self, job) -> str:
#         logger.debug('[PennylaneDevice] Getting job id')
#
#         return None
#
#     def _get_job_status(self, job) -> str:
#         logger.debug('[PennylaneDevice] Getting job status')
#
#         return "DONE"
#
#     def _get_job_result(self, job) -> dict:
#         logger.debug('[PennylaneDevice] Getting job result')
#         return job
#
#     def _calculate_execution_time(self, job_result):
#         logger.debug('[PennylaneDevice] Calculating execution time')
#
#
#         # metadata = job_result.metadata
#
#         # if metadata is None or not bool(metadata) or 'time_taken_execute' not in metadata:
#         #     return None
#
#         # self.execution_time = metadata['time_taken_execute']
#
#         # logger.debug('[PennylaneDevice] Execution time calculation was: {0} seconds'.format(
#         #     self.execution_time))
#
#         return None
#
#     def __init__(self, provider: Provider, device_specification: str, backend_name: str):
#         super().__init__(provider, device_specification)
#         self.backend = self.device
#         self.device = backend_name