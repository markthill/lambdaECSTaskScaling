# lambdaECSTaskScaling

View the [wiki](https://github.com/markthill/lambdaECSTaskScaling/wiki) for the documentation

### Testing Examples

serverless invoke local -f scale_out -p tmp/ecs-service-alarm-event-example.json

serverless invoke local -f scale_in -p tmp/sample-event-scale-in.json

serverless invoke local -f reset_alarm -p tmp/sample-rule-event.json
