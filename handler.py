import json
import boto3

#from scaler import get_desired_count

def scale_up(event, context):

    print(event)

    # retrieves the ClusterName and ServiceName
    response = describe_service(get_service(event))

    print(response)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def scale_down(event, context):

    print(event)

    get_desired_count()

    response = {
        "statusCode": 200,
        "body": {"message": "foooo"}
    }

    return response

def get_service(event):
    message = event['Records'][0]['Sns']['Message']

    # The message from the event is in the format of JSON but it is actually a string so it has to be converted
    message_json = json.loads(message)
    dimensions = message_json['Trigger']['Dimensions']

    # Create an empty dictionary to store the ClusterName and ServiceName
    dict = {}

    for i in dimensions:
        dict[i['name']] = i['value']

    return dict

def desribe_service(dict):
    client = boto3.client('ecs')

    # describe the service based on the ClusterName and ServiceName keys from the dictionary
    response = client.describe_services(
        cluster=dict['ClusterName'],
        include=['TAGS'],
        services=[
            dict['ServiceName']
        ]
    )

    return response