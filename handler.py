import datetime
import json

import cloudwatch
import dynamodb
import ecs
import utils


# import logging
# logger = logging.getLogger()
# logger.setLevel(logging.DEBUG)

def reset_alarm(event, context):
    print(event)
    now = datetime.datetime.now()
    now_formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    alarm_name = cloudwatch.alarm_name_from_event(event)
    print("reset_alarm called on: %s" % now_formatted)
    cloudwatch.set_alarm_state(alarm_name, "OK", "Resetting for Autoscaling purposes")

    response = {
        "statusCode": 200,
        "body": "thanks: "
    }
    return response


def scale_out(event, context):
    DIRECTION = "out"

    print(event)
    service = ecs.describe_service(event)
    current_size = int(service['runningCount'])

    dynamodb_item = dynamodb.get_item(event, DIRECTION)
    new_size = dynamodb.scale_out_adjustment(event, dynamodb_item, current_size)

    print("current size: %s" % current_size)
    print("adjusting to: %s" % new_size)

    if (current_size != new_size):
        ecs.update_service(service, new_size)

    cooldown = int(dynamodb_item['Item']['Cooldown'])
    cloudwatch.set_rule(utils.service_id(event, DIRECTION), cooldown)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def scale_in(event, context):
    DIRECTION = "in"

    print(event)
    service = ecs.describe_service(event)
    current_size = int(service['runningCount'])
    dynamodb_item = dynamodb.get_item(event, DIRECTION)
    new_size = dynamodb.scale_in_adjustment(event, dynamodb_item, current_size)

    print("current size: %s" % current_size)
    print("adjusting to: %s" % new_size)

    if (current_size != new_size):
        ecs.update_service(service, new_size)

    cooldown = int(dynamodb_item['Item']['Cooldown'])
    cloudwatch.set_rule(utils.service_id(event, DIRECTION), cooldown)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response
