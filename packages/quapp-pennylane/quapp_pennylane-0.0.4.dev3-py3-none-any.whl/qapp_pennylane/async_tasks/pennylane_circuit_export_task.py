#  Quapp Platform Project
#  pennylane_circuit_export_task.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.
import sys
import time
from abc import ABC
from io import BytesIO

import pennylane as qml
from quapp_common.async_tasks.export_circuit_task import CircuitExportTask


class PennylaneCircuitExportTask(CircuitExportTask, ABC):

    def _convert(self):
        self.logger.debug("Preparing circuit figure...")
        circuit = self.circuit_data_holder.circuit
        circuit_figure, _ = qml.draw_mpl(circuit)()
        self.logger.debug("Converting circuit figure to svg file...")
        figure_buffer = BytesIO()
        circuit_figure.savefig(figure_buffer, format="svg")

        self.logger.debug("Circuit figure converted successfully")
        return figure_buffer

    def _transpile_circuit(self):
        self.logger.info("Transpiling circuit: start")
        try:
            self.logger.debug(
                    f"Runtime | python_impl={getattr(sys.implementation, 'name', 'unknown')}"
                    f" | version={sys.version.split()[0]}")
        except Exception as env_err:
            self.logger.warning(f"Unable to log Python runtime info: {env_err}")

        start = time.perf_counter()
        try:
            circuit = getattr(self, "circuit", None)
            if circuit is None:
                self.logger.warning(
                        "No circuit found on instance; skipping transpilation")
                return None

            # TODO: Replace this placeholder with an actual transpilation step if available.
            transpiled_circuit = circuit

            self.logger.info("Transpiling circuit: completed successfully")
            return transpiled_circuit
        except Exception as e:
            self.logger.exception(f"Transpiling circuit failed: {e}")
            raise
        finally:
            duration = time.perf_counter() - start
            self.logger.debug(f"Transpiling circuit: duration_s={duration:.6f}")
