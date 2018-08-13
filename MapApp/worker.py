from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 as features
import boto3
import json

sqs = boto3.resource('sqs')
sns = boto3.client('sns')
queue = sqs.get_queue_by_name(QueueName='TwittTrends')
arn = 'arn:aws:sns:us-east-1:053461287737:Twitt'


def worker(queue):
    while True:
        messages = queue.receive_messages(MessageAttributeNames=['Tweet', 'Latitude', 'Longitude'])
        natural_language_understanding = NaturalLanguageUnderstandingV1(
            version='2017-02-27',
            username='c353af43-3172-455f-934a-daa55225e687',
            password='TLD5MMIRRGIh')
        if len(messages) > 0:
            for message in messages:

                if message.message_attributes is not None:
                    tweet = message.message_attributes.get('Tweet').get('StringValue')
                    lat = message.message_attributes.get('Latitude').get('StringValue')
                    lng = message.message_attributes.get('Longitude').get('StringValue')

                    try:
                        response = natural_language_understanding.analyze(
                            text=tweet,
                            features=[features.Sentiment()]
                        )
                        sentiment = response['sentiment']['document']['label']
                    except Exception as e:
                        sentiment = "neutral"

                    sns_message = {"tweet": tweet, "lat": lat, "lng": lng, "sentiment": sentiment}
                    print("SNS messsage: " + str(sns_message))
                    print [lat,lng]
                    sns.publish(TargetArn=arn, Message=json.dumps({'default': json.dumps(sns_message)}))

                message.delete()


if __name__ == '__main__':
    worker(queue)