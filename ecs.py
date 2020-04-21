import json
import boto3


# def service_current_size(dict):
#     #service_dict = get_service_data_from_event(event)
#     service = describe_service(dict)
#     return service['runningCount']
#     # Get the running, desired and pending.
#     # running_count = service['runningCount']
#     # desired_count = service['desiredCount']
#     # pending_count = service['pendingCount']

def update_service(service_dict, desired_count):
    print("update service: %s" % (desired_count))
    client = boto3.client('ecs')

    client.update_service(
        cluster=service_dict['clusterArn'],
        service=service_dict['serviceName'],
        desiredCount=desired_count
    )


def describe_service(event):
    dict = get_service_data_from_event(event)
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
