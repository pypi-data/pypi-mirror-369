"""
    QApp Platform Project
    pennylane_device_factory.py
    Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
#  Quapp Platform Project
#  pennylane_device_factory.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.config.logging_config import logger, job_logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk
from quapp_common.factory.device_factory import DeviceFactory
from quapp_common.model.provider.provider import Provider

from ..model.device.qapp_pennylane_device import QAppPennylaneDevice

logger = job_logger('PennylaneDeviceFactory')


class PennylaneDeviceFactory(DeviceFactory):

    @staticmethod
    def create_device(provider: Provider, device_specification: str,
            authentication: dict, sdk: Sdk,
            **kwargs):
        logger.info("create_device()")

        provider_type = ProviderTag.resolve(provider.get_provider_type().value)

        match provider_type:
            case ProviderTag.QUAO_QUANTUM_SIMULATOR:
                if Sdk.PENNYLANE == sdk:
                    logger.debug(
                            'Creating QAppPennylaneDevice')
                    return QAppPennylaneDevice(provider, device_specification)
                raise ValueError(
                        f'Unsupported SDK for provider type: {provider_type}')
            # case ProviderTag.AWS_BRAKET:
            #     logger.debug('Creating AwsBraketDevice')
            #     return AwsBraketDevice(provider, device_specification, kwargs['backend_name'],
            #                            kwargs['num_qubits'], kwargs['s3_bucket_name'],
            #                            kwargs['s3_prefix'], kwargs['inputs'])
            # case ProviderTag.IBM_QUANTUM:
            #     return IbmQuantumDevice(provider, device_specification,
            #                             api_token=authentication.get('api_token'),
            #                             instance=authentication.get('instance'))
            case _:
                raise ValueError(f"Unsupported provider type: {provider_type}")
