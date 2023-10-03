from pika import ConnectionParameters, PlainCredentials, BlockingConnection
import threading

class RabbitmqConsumer:
  def __init__(self, queue, callback):
    self.__host = "localhost"
    self.__port = 5672
    self.__username = "admin"
    self.__password = "123456"
    self.__queue = queue
    self.__callback = callback
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
    channel.queue_declare(
      queue=self.__queue,
      durable=True
    )
    channel.basic_consume(
      queue=self.__queue,
      auto_ack=True,
      on_message_callback=self.__callback
    )

    return channel
  
  def start(self):
    print(f"Listen RabbitMQ on Port 5672")
    threading.Thread(target=self.__channel.start_consuming).start()
    # self.__channel.start_consuming()


