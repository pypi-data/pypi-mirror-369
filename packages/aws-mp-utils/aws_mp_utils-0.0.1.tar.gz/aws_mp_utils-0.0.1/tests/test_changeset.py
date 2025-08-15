import json

import botocore.session
import botocore.errorfactory
import pytest

from unittest.mock import call, Mock

from aws_mp_utils.image import create_add_version_change_doc
from aws_mp_utils.changeset import (
    get_change_set,
    get_change_set_status,
    start_mp_change_set
)

# botocore ClientExceptionFactory
model = botocore.session.get_session().get_service_model('marketplace-catalog')
factory = botocore.errorfactory.ClientExceptionsFactory()
exceptions = factory.create_client_exceptions(model)

data = {
    'ChangeType': 'AddDeliveryOptions',
    'Entity': {
        'Type': 'AmiProduct@1.0',
        'Identifier': '123'
    }
}
details = {
    'Version': {
        'VersionTitle': 'New image',
        'ReleaseNotes': 'Release Notes'
    },
    'DeliveryOptions': [{
        'Details': {
            'AmiDeliveryOptionDetails': {
                'UsageInstructions': 'Login with SSH...',
                'RecommendedInstanceType': 't3.medium',
                'AmiSource': {
                    'AmiId': 'ami-123',
                    'AccessRoleArn': 'arn',
                    'UserName': 'ec2-user',
                    'OperatingSystemName': 'OTHERLINUX',
                    'OperatingSystemVersion': '15.3'
                },
                'SecurityGroups': [{
                    'FromPort': 22,
                    'IpProtocol': 'tcp',
                    'IpRanges': ['0.0.0.0/0'],
                    'ToPort': 22
                }]
            }
        }
    }]
}
data['Details'] = json.dumps(details)
start_changeset_params = {
    'Catalog': 'AWSMarketplace',
    'ChangeSet': [data],
}


def test_get_change_set():
    response = {
        'ChangeSetId': '123',
        'ChangeSetArn': 'string',
        'ChangeSetName': 'string',
        'Intent': 'APPLY',
        'StartTime': '2018-02-27T13:45:22Z',
        'EndTime': '2018-02-27T13:45:22Z',
        'Status': 'SUCCEEDED',
        'ChangeSet': [
            {
                'ChangeType': 'string',
                'Entity': {
                    'Type': 'string',
                    'Identifier': 'string'
                },
                'Details': 'string',
                'DetailsDocument': {'changeset': 'details'},
                'ChangeName': 'string'
            },
        ]
    }

    client = Mock()
    client.describe_change_set.return_value = response

    response = get_change_set(client, '123')
    assert response['ChangeSetId'] == '123'


def test_get_change_set_status():
    response = {
        'Status': 'SUCCEEDED',
        'ChangeSet': [
            {
                'ChangeType': 'string',
                'Entity': {
                    'Type': 'string',
                    'Identifier': 'string'
                },
                'Details': 'string',
                'DetailsDocument': {'changeset': 'details'},
                'ChangeName': 'string'
            },
        ]
    }

    client = Mock()
    client.describe_change_set.return_value = response

    response = get_change_set_status(client, '123')
    assert response == 'succeeded'


def test_start_mp_change_set():
    client = Mock()
    client.start_change_set.return_value = {
        'ChangeSetId': '123'
    }

    change_set = create_add_version_change_doc(
        entity_id='123',
        version_title='New image',
        ami_id='ami-123',
        access_role_arn='arn',
        release_notes='Release Notes',
        os_name='OTHERLINUX',
        os_version='15.3',
        usage_instructions='Login with SSH...',
        recommended_instance_type='t3.medium',
        ssh_user='ec2-user'
    )

    response = start_mp_change_set(
        client,
        [change_set]
    )

    assert response['ChangeSetId'] == '123'
    client.start_change_set.assert_called_once_with(**start_changeset_params)


def test_start_mp_change_set_ongoing_change_ResourceInUseException():

    def generate_exception():
        error_code = 'ResourceInUseException'
        error_message = (
            "Requested change set has entities locked by change sets"
            " - entity: '6066beac-a43b-4ad0-b5fe-f503025e4747' "
            " change sets: dgoddlepi9nb3ynwrwlkr3be4"
        )
        exc_data = {
            "Error": {
                "Code": error_code,
                "Message": error_message
            },
            "ResponseMetadata": {
                "RequestId": "aaaabbbb-cccc-dddd-eeee-ffff00001111",
                "HTTPStatusCode": 400,
                "HTTPHeaders": {
                    "transfer-encoding": "chunked",
                    "date": "Fri, 01 Jan 2100 00:00:00 GMT",
                    "connection": "close",
                    "server": "AmazonEC2"
                },
                "RetryAttempts": 0
            }
        }

        return exceptions.AccessDeniedException(
            error_response=exc_data,
            operation_name='start_change_set'
        )

    client = Mock()
    client.exceptions.AccessDeniedException = exceptions.AccessDeniedException
    client.start_change_set.side_effect = generate_exception()

    change_set = create_add_version_change_doc(
        entity_id='123',
        version_title='New image',
        ami_id='ami-123',
        access_role_arn='arn',
        release_notes='Release Notes',
        os_name='OTHERLINUX',
        os_version='15.3',
        usage_instructions='Login with SSH...',
        recommended_instance_type='t3.medium',
        ssh_user='ec2-user'
    )

    with pytest.raises(Exception) as error:
        start_mp_change_set(
            client,
            change_set=[change_set],
            max_rechecks=10,
            conflict_wait_period=0
        )
    assert 'AWSMPUtilsException' in str(error)
    client.start_change_set.assert_has_calls(
        [
            call(**start_changeset_params),
            call(**start_changeset_params)
        ],
        any_order=True
    )


def test_start_mp_change_set_ongoing_change_GenericBotoException():

    def generate_exception():
        error_code = 'AccessDeniedException'
        error_message = "AccessDeniedException"
        exc_data = {
            "Error": {
                "Code": error_code,
                "Message": error_message
            },
            "ResponseMetadata": {
                "RequestId": "aaaabbbb-cccc-dddd-eeee-ffff00001111",
                "HTTPStatusCode": 400,
                "HTTPHeaders": {
                    "transfer-encoding": "chunked",
                    "date": "Fri, 01 Jan 2100 00:00:00 GMT",
                    "connection": "close",
                    "server": "AmazonEC2"
                },
                "RetryAttempts": 0
            }
        }

        return exceptions.AccessDeniedException(
            error_response=exc_data,
            operation_name='start_change_set'
        )

    client = Mock()
    client.exceptions.AccessDeniedException = exceptions.AccessDeniedException
    client.start_change_set.side_effect = generate_exception()

    change_set = create_add_version_change_doc(
        entity_id='123',
        version_title='New image',
        ami_id='ami-123',
        access_role_arn='arn',
        release_notes='Release Notes',
        os_name='OTHERLINUX',
        os_version='15.3',
        usage_instructions='Login with SSH...',
        recommended_instance_type='t3.medium',
        ssh_user='ec2-user'
    )

    with pytest.raises(Exception) as error:
        start_mp_change_set(
            client,
            change_set=[change_set],
            max_rechecks=10,
            conflict_wait_period=0
        )
    assert 'AccessDeniedException' in str(error)
    client.start_change_set.assert_has_calls(
        [
            call(**start_changeset_params),
        ],
    )
