from client_files.consts import *
from client_files.client import Client
from mq.mqConsumer import MQConsumer
from mq.mqPublisher import MQPublisher


def init_client(username: str) -> Client:
    message_consumer = MQConsumer(MQ_BROKER, MQ_PORT, MQ_CONNECTION_KEEPALIVE, SERVER_MESSAGES_TOPIC_NAME)
    message_publisher = MQPublisher(MQ_BROKER, MQ_PORT, MQ_CONNECTION_KEEPALIVE, CLIENT_MESSAGES_TOPIC_NAME)

    user_response_consumer = MQConsumer(MQ_BROKER, MQ_PORT, MQ_CONNECTION_KEEPALIVE, USER_RESPONSE_TOPIC_NAME)
    user_requests_publisher = MQPublisher(MQ_BROKER, MQ_PORT, MQ_CONNECTION_KEEPALIVE, USER_REQUESTS_TOPIC_NAME)

    return Client(username, user_response_consumer, user_requests_publisher, message_consumer,
                  message_publisher, DIRECT_MESSAGE_PORT)


print("Enter username:")
username = input()

client = init_client(username)
client.start()
