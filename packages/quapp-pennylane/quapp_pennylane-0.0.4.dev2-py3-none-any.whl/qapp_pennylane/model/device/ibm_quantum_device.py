# """
#     QApp Platform Project
#     ibm_quantum_device.py
#     Copyright © CITYNOW Co. Ltd. All rights reserved.
# """
# from qapp_common.config.logging_config import logger
# from qapp_common.data.device.circuit_running_option import CircuitRunningOption
# from qiskit import transpile
#
# from ..device.pennylane_device import PennylaneDevice
#
#
# class IbmQuantumDevice(PennylaneDevice):
#     def __init__(self, provider, device_specification, api_token, instance):
#         super().__init__(provider, device_specification, 'qiskit.remote')
#         self.channel = 'ibm_quantum'
#         self.instance = instance
#         self.token = api_token
#
#     def _create_job(self, circuit, options: CircuitRunningOption):
#         logger.debug('[IbmQuantumDevice] Creating job with {0} shots'.format(options.shots))
#         transpiled_circuit = transpile(circuit, self.device)
#         return self.device.run(transpiled_circuit, shots=options.shots)
#
#     def _is_simulator(self) -> bool:
#         logger.debug('[IbmQuantumDevice] Is simulator')
#         return self.device.configuration().simulator
