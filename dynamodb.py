import boto3
import utils

def scale_out_adjustment(event, current_count):

    print("--------------")
    print(event)
    service_dict = utils.get_service_data_from_event(event)
    cluster_name = service_dict['ClusterName']
    service_name = service_dict['ServiceName']
    service_id = "%s-%s-%s" % (cluster_name, service_name, "out")
    print("dynamo_db.scale_out for service: %s" % (service_id))

    # Retrieve the scaling policy for the given cluster and service name
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ScaledServices')

    response = table.get_item(
        Key={"ServiceId": service_id}
    )

    adjustments_list = response['Item']['StepAdjustments']
    max_service_count = response['Item']['MaximumServiceCount']
    print("max service count: %s" % (max_service_count))

    avg = utils.get_average_alarm_data_points(event)

    adjustment = utils.find_matching_step_adjustment(adjustments_list, avg)

    if (current_count+adjustment > max_service_count):
        return max_service_count
    else:
        return int(current_count+adjustment)

def scale_in(event):
    print("dynamo_db.scale_in")
