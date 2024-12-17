from consts import *
from mq.mqConsumer import MQConsumer
from mq.mqPublisher import MQPublisher
from server_files.server import Server


def init_server() -> Server:
    message_consumer = MQConsumer(MQ_BROKER, MQ_PORT, MQ_CONNECTION_KEEPALIVE, CLIENT_MESSAGES_TOPIC_NAME)
    message_publisher = MQPublisher(MQ_BROKER, MQ_PORT, MQ_CONNECTION_KEEPALIVE, SERVER_MESSAGES_TOPIC_NAME)

    user_requests_consumer = MQConsumer(MQ_BROKER, MQ_PORT, MQ_CONNECTION_KEEPALIVE, USER_REQUESTS_TOPIC_NAME)
    user_response_publisher = MQPublisher(MQ_BROKER, MQ_PORT, MQ_CONNECTION_KEEPALIVE, USER_RESPONSE_TOPIC_NAME)

    return Server(user_requests_consumer, user_response_publisher, message_consumer, message_publisher)


server = init_server()
server.start()
