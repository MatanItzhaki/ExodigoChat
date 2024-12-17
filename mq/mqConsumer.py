import json
import paho.mqtt.client as mqtt

from mq.message import Message


class MQConsumer:
    def __init__(self, broker: str, port: int, connection_keepalive: int, topic_name: str) -> None:
        self.__client = mqtt.Client()
        self.__client.connect(broker, port, connection_keepalive)
        self.__client.subscribe(topic_name)
        self.__topic_name = topic_name

    def start(self, callback) -> None:

        def message_callback(client, userdata, message) -> None:
            callback(Message(json.loads(message.payload)))

        self.__client.on_message = message_callback
        self.__client.loop_forever()

    def close(self) -> None:
        self.__client.disconnect()
