import boto3
import utils
import datetime

def set_rule(rule_name, cron):
    rule_name = 'alarm-out-rule'
    now = datetime.datetime.utcnow()
    now_plus_cool_down = now + datetime.timedelta(minutes=5)
    cron = utils.create_cron_from_datetime(now_plus_cool_down)
    client = boto3.client('events')
    description = "this is just a test update from Lambda with cron: %s" % (cron)
    client.put_rule(
        Name=rule_name,
        ScheduleExpression=cron,
        State='ENABLED',
        Description=description
    )