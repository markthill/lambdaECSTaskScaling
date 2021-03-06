import boto3
import utils


def scale_out_adjustment(event, item, current_count):
    print(event)
    adjustments_list = item['Item']['StepAdjustments']
    max_service_count = item['Item']['MaximumServiceCount']
    print("max service count: %s" % (max_service_count))

    avg = utils.get_average_alarm_data_points(event)
    threshold = utils.get_threshold(event)

    bound_adjustment = avg - threshold
    print("bound adjustment: %s" % (bound_adjustment))

    adjustment = utils.find_matching_step_adjustment(adjustments_list, bound_adjustment)

    if (current_count + adjustment > max_service_count):
        return int(max_service_count)
    else:
        return int(current_count + adjustment)


def scale_in_adjustment(event, item, current_count):
    print(event)

    adjustments_list = item['Item']['StepAdjustments']
    min_service_count = item['Item']['MinimumServiceCount']
    print("min service count: %s" % (min_service_count))

    avg = utils.get_average_alarm_data_points(event)
    threshold = utils.get_threshold(event)

    bound_adjustment = avg - threshold
    print("bound adjustment: %s" % (bound_adjustment))

    adjustment = utils.find_matching_step_adjustment(adjustments_list, bound_adjustment)

    if (current_count + adjustment < min_service_count):
        return int(min_service_count)
    else:
        return int(current_count + adjustment)


def get_item(event, direction):
    print("Finding event for service: %s" % direction)
    print(event)
    service_id = utils.service_id(event, direction)
    print("dynamo_db.get_item for service_id: %s" % (service_id))

    # Retrieve the scaling policy for the given cluster and service name
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ScaledServices')

    response = table.get_item(
        Key={"ServiceId": service_id}
    )

    return response
