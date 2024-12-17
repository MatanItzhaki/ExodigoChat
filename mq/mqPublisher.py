import json
import paho.mqtt.client as mqtt

from mq.message import Message


class MQPublisher:
    def __init__(self, broker: str, port: int, connection_keepalive: int, topic_name: str) -> None:
        self.__client = mqtt.Client()
        self.__client.connect(broker, port, connection_keepalive)
        self.__topic_name = topic_name

    def publish_message(self, message: Message) -> None:
        self.__client.publish(self.__topic_name, json.dumps(message.content).encode())

    def close(self) -> None:
        self.__client.disconnect()
