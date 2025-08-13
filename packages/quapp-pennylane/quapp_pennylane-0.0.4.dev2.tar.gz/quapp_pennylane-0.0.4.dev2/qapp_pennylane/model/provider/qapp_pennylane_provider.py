#  Quapp Platform Project
#  qapp_pennylane_provider.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.config.logging_config import job_logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.model.provider.provider import Provider

logger = job_logger('QuappPennyLaneProvider')


class QAppPennyLaneProvider(Provider):
    def __init__(self):
        super().__init__(ProviderTag.QUAO_QUANTUM_SIMULATOR)
        logger.info(
                f'QAppPennyLaneProvider initialized | tag={ProviderTag.QUAO_QUANTUM_SIMULATOR}')

    def get_backend(self, device_specification):
        logger.debug(
                f'Getting backend for PennyLane device with spec: {device_specification}')

        try:
            # with pennylane, create a backend later
            logger.info('Deferred backend creation for PennyLane device')
            return None
        except Exception as exception:
            logger.error(f'Failed to get backend for PennyLane device for spec'
                         f' {device_specification}: {exception}', exc_info=True)
            raise ValueError('Unsupported device')

    def collect_provider(self):
        logger.debug('Collecting provider session')
        # No external provider to collect for local PennyLane setup
        logger.info('No provider session required (local simulator)')
        return None
