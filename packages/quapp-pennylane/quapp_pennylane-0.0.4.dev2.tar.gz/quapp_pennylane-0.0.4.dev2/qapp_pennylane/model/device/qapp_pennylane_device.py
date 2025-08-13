#  Quapp Platform Project
#  qapp_pennylane_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

import math
import time

import pennylane as qml
from pennylane.measurements import ProbabilityMP
from pennylane.tape import QuantumTape
from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.data.response.authentication import Authentication
from quapp_common.data.response.custom_header import CustomHeader
from quapp_common.enum.invocation_step import InvocationStep
from quapp_common.model.device.custom_device import CustomDevice
from quapp_common.model.provider.provider import Provider

DEVICE_TYPE_9Q_SQUARE_PYQVM = '9q-square-pyqvm'

DEVICE_TYPE_9Q_SQUARE_QVM = '9q-square-qvm'

RIGETTI_QVM = 'rigetti.qvm'


class QAppPennylaneDevice(CustomDevice):
    def __init__(self, provider: Provider, device_specification: str):
        super().__init__(provider, device_specification)
        self.logger.debug('Initializing device specification')
        self.device_specification = device_specification
        # Extra initialization logging
        self.logger.info(
                f'QAppPennylaneDevice initialized | provider={getattr(provider, "name", str(provider))} '
                f'| device_spec="{self.device_specification}" | pennylane_version={qml.__version__}')

    def _create_job(self, circuit, options: CircuitRunningOption):
        """
        @param circuit: circuit to run
        @param options: options for running circuit
        ex: options.shots: number of shots

        run the circuit and return the result
        """
        self.logger.debug(
                f'Creating job with {getattr(options, "shots", None)} shots')

        if getattr(options, "shots", None) is None:
            self.logger.warning(
                    "Option 'shots' is None; falling back to device or default shots")

        with QuantumTape() as tape:
            self.logger.debug('Entering QuantumTape context to build circuit')
            circuit()
            self.logger.debug('Circuit built inside QuantumTape context')

        # Tape diagnostics
        try:
            num_wires = getattr(tape, "num_wires", None)
            ops_count = len(getattr(tape, "operations", []) or [])
            obs_count = len(getattr(tape, "observables", []) or [])
            self.logger.info(
                    f'Tape summary | wires={num_wires} | ops={ops_count} | observables={obs_count}')
        except Exception as e:
            self.logger.warning(f'Unable to summarize tape: {e}')

        parts = self.device_specification.split('/')
        device_name = parts[0]
        self.logger.debug(
                f'Device resolution | spec="{self.device_specification}" | name="{device_name}" | parts={parts}')

        """
        with rigetti device, device_specification includes 
        rigetti.qvm/9q-square-pyqvm, 9q-square-qvm: 9qubit
        rigetti.qvm/Nq-pyqvm, Nq-qvm: Nqubit (32 with QApp platform)
        """
        unsupported_default_qubit_autograd = qml.__version__ > '0.37.0' and device_name == 'default.qubit.autograd'
        if not qml.plugin_devices.__contains__(device_name):
            if unsupported_default_qubit_autograd:
                self.logger.warning(
                        f'Using default.qubit for device {device_name} in PennyLane version {qml.__version__}')
            else:
                self.logger.error(
                        f'The device {device_name} is not supported in PennyLane version {qml.__version__}.')
                raise ValueError(
                        f'The device {device_name} is not supported in PennyLane version {qml.__version__}. ')

        # Device creation with detailed logging
        try:
            if device_name == RIGETTI_QVM:
                device_type = parts[1]
                self.logger.info(
                        f'Selecting Rigetti QVM | type="{device_type}" | shots={getattr(options, "shots", None)}')
                if parts[1] in [DEVICE_TYPE_9Q_SQUARE_QVM,
                                DEVICE_TYPE_9Q_SQUARE_PYQVM]:
                    self.device = qml.device(device_name, device=device_type,
                                             shots=options.shots)
                else:
                    derived_device = str(tape.num_wires) + device_type[1:]
                    self.logger.debug(
                            f'Derived Rigetti device name: {derived_device}')
                    self.device = qml.device(device_name, device=derived_device,
                                             shots=options.shots)
            elif unsupported_default_qubit_autograd:
                self.logger.info(
                        f'Falling back to default.qubit due to unsupported "{device_name}" with autograd')
                self.device = qml.device('default.qubit', wires=tape.wires,
                                         shots=options.shots)
            else:
                self.logger.info(
                        f'Selecting device | name="{device_name}" | wires={tape.wires} | shots={getattr(options, "shots", None)}')
                self.device = qml.device(device_name, wires=tape.wires,
                                         shots=options.shots)
        except Exception as e:
            self.logger.exception(
                    f'Failed to create device "{device_name}" from spec "{self.device_specification}": {e}')
            raise

        # QNode setup
        qnode_params = {'interface': "autograd",
                        'diff_method': "parameter-shift"} if unsupported_default_qubit_autograd else {}
        self.logger.debug(
                f'QNode params: {qnode_params if qnode_params else "(default)"}')

        try:
            qnode = qml.QNode(circuit, self.device, **qnode_params)
            self.logger.debug('QNode created successfully')
        except Exception as e:
            self.logger.exception(f'Failed to create QNode: {e}')
            raise

        # Execute with timing
        start_time = time.perf_counter()
        try:
            self.logger.info('Starting circuit execution')
            job_result = qnode()
            self.logger.info('Circuit execution completed successfully')
        except Exception as e:
            self.logger.exception(f'Circuit execution failed: {e}')
            raise
        finally:
            end_time = time.perf_counter()

        exec_time = end_time - start_time
        self.logger.debug(f'Execution time (s): {exec_time:.6f}')

        # Histogram generation
        result_histogram = {}

        try:
            # generate histogram
            # Prefer the earlier 'tape' we built the circuit into; avoid qnode.tape for compatibility
            measurements = getattr(tape, "measurements", None)

            prob_idx = None
            prob_wires = None
            if measurements:
                for i, m in enumerate(measurements):
                    # Detect probability measurement by its concrete type
                    if isinstance(m, ProbabilityMP):
                        prob_idx = i
                        prob_wires = getattr(m, "wires", None)
                        break

            if prob_idx is not None:
                # Extract probabilities from the QNode result
                if isinstance(job_result, (list, tuple)):
                    probs = job_result[prob_idx]
                else:
                    # Single-measurement: a result is the prob array
                    probs = job_result

                # Derive the number of bits from wires if available, else from length
                if prob_wires is not None:
                    num_bits = len(prob_wires)
                else:
                    num_bits = math.ceil(math.log2(len(probs))) if len(
                            probs) > 0 else 0

                self.logger.debug(
                        f'Generating histogram | outcomes={len(probs)} | num_bits={num_bits}')
                for i, prob in enumerate(probs):
                    bitstring = format(i,
                                       f'0{num_bits}b') if num_bits > 0 else '0'
                    result_histogram[bitstring] = int(prob * options.shots)
                self.logger.info(
                        f'Histogram generated | entries={len(result_histogram)}')
            else:
                self.logger.info(
                        'No probability measurement found; histogram not generated')
                result_histogram = None
        except Exception as e:
            self.logger.exception(f'Failed to generate histogram: {e}')
            result_histogram = None

        shots = getattr(qnode.device, 'shots', getattr(options, "shots", None))
        if shots is None:
            self.logger.warning(
                    'Unable to determine shots from device or options; shots=None')
        else:
            self.logger.debug(f'Final shots value: {shots}')

        data = {"result": job_result, "histogram": result_histogram,
                "time_taken_execute": exec_time, "shots": shots}

        self.logger.info(
                f'Job data summary | has_result={job_result is not None} | has_histogram={result_histogram is not None} | exec_time_s={exec_time:.6f} | shots={shots}')
        return data

    def _is_simulator(self) -> bool:
        self.logger.debug('Is simulator')
        return True

    def _produce_histogram_data(self, job_result) -> dict | None:
        self.logger.info('Producing histogram data')

        histogram = job_result.get('histogram')

        if histogram is None:
            self.logger.debug("Can't produce histogram (histogram=None)")
        else:
            self.logger.debug(f'Histogram available | entries={len(histogram)}')

        return job_result.get('histogram')

    def _get_provider_job_id(self, job) -> str:
        self.logger.debug('Getting job id')
        self.logger.debug('No job id in local simulator')
        return ""

    def _get_job_status(self, job) -> str:
        self.logger.debug('Getting job status')

        return "DONE"

    def _get_job_result(self, job) -> dict:
        self.logger.debug('Getting job result')

        return job

    def _calculate_execution_time(self, job_result):
        self.logger.debug('Calculating execution time')

        self.execution_time = job_result.get('time_taken_execute')

        self.logger.debug(
                f'Execution time calculation was: {self.execution_time} seconds')

    def run_circuit(self, circuit, post_processing_fn,
            options: CircuitRunningOption, callback_dict: dict,
            authentication: Authentication, project_header: CustomHeader,
            workspace_header: CustomHeader):
        """
        @param project_header: project header
        @param callback_dict: callback url dictionary
        @param options: Options for run circuit
        @param authentication: Authentication for calling quao server
        @param post_processing_fn: Post-processing function
        @param circuit: Circuit was run
        """
        self.logger.info(
                f'run_circuit invoked | has_post_processing={post_processing_fn is not None} '
                f'| callbacks={[k.name for k in callback_dict.keys()] if callback_dict else []}')

        original_job_result, job_response = self._on_execution(
                authentication=authentication, project_header=project_header,
                workspace_header=workspace_header,
                execution_callback=callback_dict.get(
                        InvocationStep.EXECUTION) if callback_dict else None,
                circuit=circuit, options=options)

        if original_job_result is None:
            self.logger.warning(
                    'Execution returned no result; aborting pipeline')
            return

        job_response = self._on_analysis(job_response=job_response,
                                         original_job_result=original_job_result,
                                         analysis_callback=callback_dict.get(
                                                 InvocationStep.ANALYSIS) if callback_dict else None)

        if job_response is None:
            self.logger.warning(
                    'Analysis returned no response; aborting pipeline')
            return

        self.logger.info('Starting finalization step')
        self._on_finalization(job_result=original_job_result.get('result'),
                              authentication=authentication,
                              post_processing_fn=post_processing_fn,
                              finalization_callback=callback_dict.get(
                                      InvocationStep.FINALIZATION) if callback_dict else None,
                              project_header=project_header,
                              workspace_header=workspace_header)
        self.logger.info('Finalization completed')

    def _get_shots(self, job_result) -> int | None:
        """
        Retrieve the number of shots from the job result.

        This method checks if the job result contains the 'shots' attribute
        and returns its value. If the 'shots' attribute is not present,
        the method returns None.

        Args:
            job_result: An object representing the result of a job, which
                        may contain the number of shots.

        Returns:
            int | None: The number of shots if available; otherwise, None.
        """
        self.logger.debug('Calculating number of shots')

        shots = getattr(job_result, 'shots', None)
        self.logger.debug(f'Number of shots: {shots}')
        return shots
