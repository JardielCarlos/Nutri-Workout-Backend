from typing import Dict
from pika import ConnectionParameters, PlainCredentials, BlockingConnection, BasicProperties
from json import dumps

class RabbitmqPublisher:
  def __init__(self):
    self.__host = "localhost"
    self.__port = 5672
    self.__username = "admin"
    self.__password = "123456"
    self.__exchange = "NutriWorkoutSolicitacoes"
    self.__routing_key="personalTrainer"
    self.__channel = self.__create_channel()

  def __create_channel(self):
    connection_parameters = ConnectionParameters(
      host=self.__host,
      port=self.__port,
      credentials= PlainCredentials(
        username=self.__username,
        password=self.__password
      )
    )

    channel = BlockingConnection(connection_parameters).channel()
    return channel
  
  def send_message(self, body: Dict):
    self.__channel.basic_publish(
      exchange=self.__exchange,
      routing_key=self.__routing_key,
      body=dumps(body),
      properties=BasicProperties(
        delivery_mode=2       
      )
    )
