import json
import re

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
        x = x+1
        total += num

    avg = total/x
    print(avg)
    return avg


def find_matching_step_adjustment(step_list, matching_value):
    print(step_list)
    for step in step_list:
        print(step)
        if 'MetricIntervalUpperBound' in step:
            upper_bound = step['MetricIntervalUpperBound']
            print(upper_bound)
        else:
            # Set an arbitrarily high upper bound
            upper_bound = 10000

        if 'MetricIntervalLowerBound' in step:
            lower_bound = step['MetricIntervalLowerBound']
            print(upper_bound)
        else:
            # Set 0 lower bound
            lower_bound = 0

        if (matching_value >= lower_bound and matching_value <= upper_bound):
            adjustment = step['ScalingAdjustment']
            print("match for adjustment of: %s" % (adjustment))
            break

    return adjustment

def create_cron_from_datetime(dt):
    print(dt.minute)
    print(dt.hour)
    print(dt.day)
    print(dt.month)
    print('?')
    print(dt.year)
    print("cron(%s %s %s %s ? %s)" % (dt.minute, dt.hour, dt.day, dt.month, dt.year))
    return "cron(%s %s %s %s ? %s)" % (dt.minute, dt.hour, dt.day, dt.month, dt.year)