"""
    QApp Platform Project
    pennylane_provider_factory.py
    Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
#  Quapp Platform Project
#  pennylane_provider_factory.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.config.logging_config import logger, job_logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk
from quapp_common.factory.provider_factory import ProviderFactory

from ..model.provider.qapp_pennylane_provider import QAppPennyLaneProvider

logger = job_logger('PennyLaneProviderFactory')


class PennyLaneProviderFactory(ProviderFactory):

    @staticmethod
    def create_provider(provider_type: ProviderTag, sdk: Sdk,
            authentication: dict):
        logger.info("create_provider()")
        logger.debug(
                f"provider_type: {provider_type}, sdk: {sdk}, authentication: {authentication}")

        match provider_type:
            case ProviderTag.QUAO_QUANTUM_SIMULATOR:
                if Sdk.PENNYLANE.__eq__(sdk):
                    return QAppPennyLaneProvider()
                raise ValueError(
                        f'Unsupported SDK for provider type: {provider_type}')
            # case ProviderTag.IBM_CLOUD:
            #     return IbmCloudProvider(authentication.get('token'), authentication.get('crn'))
            # case ProviderTag.IBM_QUANTUM:
            #     return IbmQuantumProvider(authentication.get('token'))
            # case ProviderTag.AWS_BRAKET:
            #     return AwsBraketProvider(authentication.get('access_key_id'),
            #                              authentication.get('secret_access_key'),
            #                              authentication.get('region_name'))
            case _:
                raise ValueError(f'Unsupported provider type: {provider_type}')
