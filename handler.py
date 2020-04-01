import json
import boto3
# import logging
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

#from scaler import get_desired_count


def scale_up(event, context):

    print(event)

    # retrieves the ClusterName and ServiceName
    service_dict = get_service_data_from_event(event)

    # retrieve the actual values we need about the service.  The current state and the tags that describe min/max values.
    service = describe_service(service_dict)

    scale_up_response = scale_service_up(service)

    alarm_name = get_alarm_name(event)
    set_alarm_state(alarm_name, 'OK', 'Resetting state to OK to allow for Alarm to trigger again.')

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return scale_up_response


def scale_down(event, context):

    print(event)

    # retrieves the ClusterName and ServiceName
    service_dict = get_service_data_from_event(event)

    # retrieve the actual values we need about the service.  The current state and the tags that describe min/max values.
    service = describe_service(service_dict)

    scale_down_response = scale_service_down(service)

    alarm_name = get_alarm_name(event)
    set_alarm_state(alarm_name, 'OK', 'Resetting state to OK to allow for Alarm to trigger again.')

    response = {
        "statusCode": 200,
        "body": {"message": "foooo"}
    }

    return scale_down_response

def describe_service(dict):
    client = boto3.client('ecs')

    # describe the service based on the ClusterName and ServiceName keys from the dictionary
    response = client.describe_services(
        cluster=dict['ClusterName'],
        include=['TAGS'],
        services=[
            dict['ServiceName']
        ]
    )

    print(response['services'][0])

    # We are only interested in a single service, so there will only be one returned
    return response['services'][0]

def get_service_data_from_event(event):
    message = event['Records'][0]['Sns']['Message']

    # The message from the event is in the format of JSON but it is actually a string so it has to be converted
    message_json = json.loads(message)
    dimensions = message_json['Trigger']['Dimensions']

    # Create an empty dictionary to store the ClusterName and ServiceName
    dict = {}

    for i in dimensions:
        dict[i['name']] = i['value']

    return dict

def get_alarm_name(event):
    message = event['Records'][0]['Sns']['Message']
    message_json = json.loads(message)

    return message_json['AlarmName']

def scale_service_up(service):
    print('Scaling UP')

    # Get the running, desired and pending.
    running_count = service['runningCount']
    desired_count = service['desiredCount']
    pending_count = service['pendingCount']

    maximum = get_maximum_service_size(service)

    # TODO: need to possibly add the pending into this check
    if running_count >= maximum:
        print('Max service count reached.  No further scaling can be done.')
        return "{'message': 'No scaling possible, max reached'}"
    else:
        print("Scaling up from %s to %s" % (str(running_count), str(running_count + 1)))
        update_service(service, running_count + 1)

def scale_service_down(service):
    print('Scaling DOWN')

    # Get the running, desired and pending.
    running_count = service['runningCount']
    desired_count = service['desiredCount']
    pending_count = service['pendingCount']

    minimum = get_minimum_service_size(service)

    # TODO: need to possibly add the pending into this check
    if running_count <= minimum:
        print('Min service count reached.  No further scaling can be done.')
        return "{'message': 'No scaling possible, min reached'}"
    else:
        print("Scaling down from %s to %s" % (str(running_count), str(running_count - 1)))
        update_service(service, running_count - 1)

# Returns the maximum size for the service.  This implementation may have to change if tags are not available on
# container services
def get_maximum_service_size(service):
    tags = tags_dict(service)
    maximum = tags['MaximumServiceSize']
    return int(maximum)

# Returns the maximum size for the service.  This implementation may have to change if tags are not available on
# container services
def get_minimum_service_size(service):
    tags = tags_dict(service)
    minimum = tags['MinimumServiceSize']
    return int(minimum)

def tags_dict(service):
    service_tags = service['tags']

    tags_dict = {}

    for tag in service_tags:
        tags_dict[tag['key']] = tag['value']

    return tags_dict

def update_service(service, desired_count):
    client = boto3.client('ecs')

    client.update_service(
        cluster=service['clusterArn'],
        service=service['serviceName'],
        desiredCount=desired_count
    )

def set_alarm_state(alarm_name, state_value, state_reason):
     print("set_alarm_state: %s, %s, %s" % (alarm_name, state_value, state_reason))
     client = boto3.client('cloudwatch')

     client.set_alarm_state(
         AlarmName=alarm_name,
         StateValue=state_value,
         StateReason=state_reason
     )