# """
#     QApp Platform Project
#     aws_braket_provider.py
#     Copyright © CITYNOW Co. Ltd. All rights reserved.
# """
# import boto3
# from braket.aws import AwsDevice, AwsSession
# from qapp_common.config.logging_config import logger
# from qapp_common.enum.provider_tag import ProviderTag
# from qapp_common.model.provider.provider import Provider


# class AwsBraketProvider(Provider):
#     def __init__(self, access_key_id, secret_access_key, region_name):
#         super().__init__(ProviderTag.AWS_BRAKET)
#         self.access_key_id = access_key_id
#         self.secret_access_key = secret_access_key
#         self.region_name = region_name

#     def get_backend(self, device_specification):
#         logger.debug('[AwsBraketProvider] get_backend()')

#         session = self.collect_provider()

#         return AwsDevice(arn=device_specification, aws_session=session)

#     def collect_provider(self):
#         logger.debug('[AwsBraketProvider] collect_provider()')

#         session = boto3.Session(aws_access_key_id=self.access_key_id,
#                                 aws_secret_access_key=self.secret_access_key,
#                                 region_name=self.region_name)
#         return AwsSession(boto_session=session)
