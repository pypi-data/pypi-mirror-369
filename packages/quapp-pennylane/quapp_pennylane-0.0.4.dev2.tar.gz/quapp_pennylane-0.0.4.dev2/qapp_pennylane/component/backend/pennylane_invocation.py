#  Quapp Platform Project
#  pennylane_invocation.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from pennylane.tape import QuantumTape
from quapp_common.component.backend.invocation import Invocation
from quapp_common.config.thread_config import circuit_exporting_pool
from quapp_common.data.async_task.circuit_export.backend_holder import \
    BackendDataHolder
from quapp_common.data.async_task.circuit_export.circuit_holder import \
    CircuitDataHolder
from quapp_common.data.request.invocation_request import InvocationRequest
from quapp_common.model.provider.provider import Provider

from ...async_tasks.pennylane_circuit_export_task import \
    PennylaneCircuitExportTask
from ...factory.pennylane_device_factory import PennylaneDeviceFactory
from ...factory.pennylane_provider_factory import PennyLaneProviderFactory


class PennylaneInvocation(Invocation):

    def __init__(self, request_data: InvocationRequest, **kwargs):
        super().__init__(request_data)
        self.num_qubits = kwargs.get('num_qubits')
        # Initialization logging
        try:
            backend_name = getattr(self.backend_information, 'device_name',
                                   None)
            provider_tag = getattr(self.backend_information, "provider_tag",
                                   None)
            has_auth = getattr(self.backend_information, "authentication",
                               None) is not None
            self_input_keys = list(self.input.keys()) if isinstance(self.input,
                                                                    dict) else None
            self.logger.info(
                    f'Initialized | device="{backend_name}" | provider_tag="{provider_tag}" '
                    f'| has_auth={has_auth} | num_qubits_hint={self.num_qubits} | input_keys={self_input_keys}')
        except Exception as e:
            self.logger.warning(f'Initialization summary failed: {e}')

    def _export_circuit(self, circuit):
        self.logger.info('Exporting circuit')
        try:
            export_url_present = bool(getattr(self, "circuit_export_url", None))
            self.logger.debug(
                    f"Preparing circuit export | has_export_url={export_url_present}")

            circuit_export_task = PennylaneCircuitExportTask(
                    circuit_data_holder=CircuitDataHolder(circuit,
                                                          self.circuit_export_url),
                    backend_data_holder=BackendDataHolder(
                            self.backend_information,
                            self.authentication.user_token))
            future = circuit_exporting_pool.submit(circuit_export_task.do)
            self.logger.info("Circuit export submitted to thread pool")

            # Optional: add a done callback for visibility
            def _on_done(f):
                try:
                    f.result()
                    self.logger.info("Circuit export task completed")
                except Exception as task_err:
                    self.logger.exception(
                            f"Circuit export task failed: {task_err}")

            future.add_done_callback(_on_done)
        except Exception as exception:
            self.logger.exception(f'Failed to export circuit: {exception}')
            raise

    def _create_provider(self):
        self.logger.debug('Creating provider')
        try:
            provider_tag = getattr(self.backend_information, "provider_tag",
                                   None)
            self.logger.debug(
                    f'Creating provider | tag="{provider_tag}" | sdk="{self.sdk}"')
            provider = PennyLaneProviderFactory.create_provider(
                    provider_type=provider_tag, sdk=self.sdk,
                    authentication=self.backend_information.authentication)
            self.logger.info('Provider created successfully')
            return provider
        except Exception as exception:
            self.logger.exception(f'Failed to create provider: {exception}')
            raise

    def _create_device(self, provider: Provider):
        self.logger.info('Creating device')
        try:
            device_name = getattr(self.backend_information, "device_name", None)
            self.logger.debug(
                    f'Device params | device="{device_name}" | sdk="{self.sdk}" '
                    f'| num_qubits={self.num_qubits} | input_keys={list(self.input.keys()) if isinstance(self.input, dict) else None}')
            device = PennylaneDeviceFactory.create_device(provider=provider,
                                                          device_specification=device_name,
                                                          authentication=self.backend_information.authentication,
                                                          sdk=self.sdk,
                                                          num_qubits=self.num_qubits,
                                                          input=self.input)
            self.logger.info('Device created successfully')
            return device
        except Exception as exception:
            self.logger.exception(f'Failed to create device: {exception}')
            raise

    def _get_qubit_amount(self, circuit):
        self.logger.debug('Getting qubit amount')
        try:
            with QuantumTape() as tape:
                circuit()
            num_wires = getattr(tape, "num_wires", None)
            self.logger.info(f'Qubit amount detected | wires={num_wires}')
            return num_wires
        except Exception as exception:
            self.logger.exception(
                    f'Failed to determine qubit amount: {exception}')
            raise
