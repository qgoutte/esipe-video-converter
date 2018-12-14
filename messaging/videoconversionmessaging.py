
import time
from google.cloud import pubsub_v1
from threading import Thread
import logging
import json
from database.dynamodb import videoconversiondynamodb

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)
#logging.getLogger("pika").setLevel(logging.INFO)

# rabbitmqadmin -H localhost -u ezip -p pize -V ezip purge queue name=video-conversion-queue
# rabbitmqadmin -H localhost -u ezip -p pize -V ezip get queue=video-conversion-queue

class VideoConversionMessaging(Thread):

    def __init__(self, _config_, db_service):
        self.db_service=db_service
        project_id = _config_.get_project_id()
        subscription_name = _config_.get_subscription_name()
        subscriber = pubsub_v1.SubscriberClient()
        subscription_path = subscriber.subscription_path(project_id, subscription_name)

        logging.info("Subscription_path : {}"+subscription_path)

        def callback(message):
            logging.info("Received message : {}".format(message))
            message.ack()
            self.processing(json.loads(message.data.decode('utf-8')))


        subscriber.subscribe(subscription_path, callback=callback)
        logging.info("Listen message on : {}".format(subscription_path))
        while True:
            time.sleep(60000)

    def processing(self,_data_):
        origin_path = _data_['originPath']
        target_path = _data_['targetPath']

        logging.info("test : {}".format(_data_))

        self.db_service.update_statut(_data_['uuid'], 'IN PROGRESS')
        try:
            self.db_service.convert(origin_path, target_path)
        except:
            self.db_service.update_statut(_data_['uuid'], 'ABORTED')
        else:
            self.db_service.update_statut(_data_['uuid'], 'FINISHED')

    #def run(self):
     #   while True : # "_CONSUMING_" == self.consuming :
#            logging.info("Starts consuming on message bus before RDV")
#            self.channel.start_consuming()
#            logging.info("WAITING Rendez-Vous")
#            self.rendez_vous.get()
#            logging.info("Rendez-Vous")
#            self.channel = self.connection.channel()
#            self.channel.basic_consume(self.on_message, self.rmq, no_ack=True)
       #     if "_CONSUMING_" == self.consuming :
      #          method, prop, body = self.channel.basic_get(self.rmq, no_ack=True)
        #        if body :
         #           self._on_message_(body)
          #          pass
           #     else :
            #        try :
             #           self.pause.get(timeout=1)
              #      except queue.Empty :
               #         pass
                    # self._on_message_(message)


    #def on_message(self, channel, method_frame, header_frame, body):
        #logging.info(body)
        # logging.info('id = %s, URI = %s', body["id"], body['originPath'])
        # logging.info('URI = %s', body['originPath'])
        #logging.info('URI = %s', body.decode())
        #convert_request = json.loads(body.decode())
        #logging.info(convert_request)
        #self.converting_service.convert(convert_request["id"], convert_request['originPath'])

    #def _on_message_(self,  body):
        #logging.info(body)
        # logging.info('id = %s, URI = %s', body["id"], body['originPath'])
        # logging.info('URI = %s', body['originPath'])
        #logging.info('URI = %s', body.decode())
        #convert_request = json.loads(body.decode())
        #logging.info(convert_request)
        #self.converting_service.convert(convert_request["id"], convert_request['originPath'])

    #def stop_consuming(self):
        #logging.info("Stops consuming on message bus")
        # self.channel.stop_consuming()
        #self.consuming = "_IDLE_"

    #def start_consuming(self):
        #logging.info("Starts consuming on message bus")
        #self.channel.start_consuming()
        # self.rendez_vous.put("_CONSUMING_")
        #self.consuming = "_CONSUMING_"
        # self.start()

   #def is_consuming(self):
        #return self.consuming
