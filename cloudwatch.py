import boto3
import utils
import datetime


def set_rule(rule_name, cooldown):
    now = datetime.datetime.utcnow()
    now_plus_cool_down = now + datetime.timedelta(minutes=cooldown)
    cron = utils.create_cron_from_datetime(now_plus_cool_down)

    client = boto3.client('events')
    description = "this is just a test update from Lambda with cron: %s" % (cron)
    client.put_rule(
        Name=rule_name,
        ScheduleExpression=cron,
        State='ENABLED',
        Description=description
    )


def set_alarm_state(alarm_name, state_value, state_reason):
    print("set_alarm_state: %s, %s, %s" % (alarm_name, state_value, state_reason))
    client = boto3.client('cloudwatch')

    client.set_alarm_state(
        AlarmName=alarm_name,
        StateValue=state_value,
        StateReason=state_reason
    )


def alarm_name_from_event(event):
    alarm = event['resources'][0]
    alarm_name = alarm.split('/')[1]
    return alarm_name
