import json
import re

# Takes the event sent from an SNS message and parses it to return the service data that we are interested in
# for scaling purposes.
def get_service_data_from_event(event):
    message = event['Records'][0]['Sns']['Message']

    # The message from the event is in the format of JSON but it is actually a string so it has to be converted
    message_json = json.loads(message)
    dimensions = message_json['Trigger']['Dimensions']

    # Create an empty dictionary to store the ClusterName and ServiceName
    service_dict = {}

    for i in dimensions:
        service_dict[i['name']] = i['value']

    return service_dict


# The message from an alarm event will contain a NewStateReason that looks similar to the following
# {"NewStateReason": "Threshold Crossed: 2 out of the last 2 datapoints [11.79340974842514 (20/04/20 16:15:00), 11.925176609329313 (20/04/20 16:14:00)] was greater than or equal to the threshold (10.0) (minimum 2 datapoint for OK -> ALARM transition)."
# We need all the data points to average them in order to pull the correct scaling value from our scaling adjustments
def get_average_alarm_data_points(event):
    message = event['Records'][0]['Sns']['Message']
    message_json = json.loads(message)

    new_state_reason = message_json['NewStateReason']
    results = re.finditer(r'(?<=\[).+?(?=\])', new_state_reason)

    for item in results:
        alarm_values = item.group(0)

    alarm_values_list = alarm_values.split(', ')
    numeric_values = []
    for av in alarm_values_list:
        numeric = av.split(' ')[0]
        numeric_values.append(float(numeric))

    x = 0
    total = 0
    for num in numeric_values:
        x = x + 1
        total += num

    avg = total / x
    print("The average of the data points are %s" % (avg))
    return avg

def get_threshold(event):
    message = event['Records'][0]['Sns']['Message']
    message_json = json.loads(message)

    new_state_reason = message_json['NewStateReason']
    threshold = re.finditer(r'(?<= (threshold \()).+?(?=\))', new_state_reason)

    for item in threshold:
        threshold_value = item.group(0)
    print("found threshold of: %s" % threshold_value)

    return float(threshold_value)


def find_matching_step_adjustment(step_list, matching_value):
    print("Finding a match in steps for value: %s" % matching_value)

    # Cycle through all the step adjustments until one is found matching the passed in "matching_value".  Once
    # the correct upper and lower bound match return the adjustment
    for step in step_list:
        print(step)
        # Find the upper bound of the step
        if 'MetricIntervalUpperBound' in step:
            upper_bound = step['MetricIntervalUpperBound']
        else:
            # Set an arbitrarily high upper bound
            upper_bound = 10000

        # Find the lower bound of the step
        if 'MetricIntervalLowerBound' in step:
            lower_bound = step['MetricIntervalLowerBound']
        else:
            # Set 0 lower bound
            lower_bound = 0

        # See if the value being matched against is in between the upper and lower bound.  If it is return the
        # ScalingAdjustment for that step
        adjustment = 0
        if (matching_value >= lower_bound and matching_value <= upper_bound):
            adjustment = step['ScalingAdjustment']
            print("match for adjustment of: %s" % (adjustment))
            break
        else:
            print("no match found with upper bound: %s and lower bound: %s" % (upper_bound, lower_bound))

    return adjustment


def create_cron_from_datetime(dt):
    print("returning cron formatted to: cron(%s %s %s %s ? %s)" % (dt.minute, dt.hour, dt.day, dt.month, dt.year))
    return "cron(%s %s %s %s ? %s)" % (dt.minute, dt.hour, dt.day, dt.month, dt.year)


def service_id(event, direction):
    service_dict = get_service_data_from_event(event)
    cluster_name = service_dict['ClusterName']
    service_name = service_dict['ServiceName']
    service_id = "%s-%s-%s" % (cluster_name, service_name, direction)
    return service_id
