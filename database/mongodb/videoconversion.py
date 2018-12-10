
import logging

from pymongo import MongoClient
import ffmpy
import time
import os
import websocket
import json
import ssl



logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)
#  ffmpeg -i Game.of.Thrones.S07E07.1080p.mkv -vcodec mpeg4 -b 4000k -acodec mp2 -ab 320k converted.avi


class VideoConversion(object):
    def __init__(self, _config_):
        self.client = MongoClient(_config_.get_database_host(), _config_.get_database_port())
        self.db = self.client[_config_.get_database_name()]
        self.video_conversion_collection = self.db[_config_.get_video_conversion_collection()]
        self.url = _config_.get_video_status_callback_url()


    def find_one(self):
        conversion = self.video_conversion_collection.find_one()
        uri = conversion['originPath']
        id = conversion['_id']
        logging.info('id = %s, URI = %s',  id, uri  )
        ff = ffmpy.FFmpeg(
                inputs={uri: None},
                outputs={'converted.avi' : '-y -vcodec mpeg4 -b 4000k -acodec mp2 -ab 320k' }
            )
        logging.info("FFMPEG = %s", ff.cmd)
        # ff.run()
        self.video_conversion_collection.update({'_id' : id}, { '$set' : {'targetPath' : 'converted.avi'}})
        self.video_conversion_collection.update({'_id' : id}, { '$set' : {'tstamp' : time.time()  }})

        #for d in self.video_conversion_collection.find():
        #    logging.info(d)

    def convert(self, _id_, _uri_):
        converted = _uri_.replace(".mkv", "-converted.avi")
        logging.info('ID = %s, URI = %s —› %s',  _id_, _uri_ , converted )
        ff = ffmpy.FFmpeg(
                inputs={_uri_: None},
                outputs={converted : '-y -vcodec mpeg4 -b 4000k -acodec mp2 -ab 320k' }
            )
        logging.info("FFMPEG = %s", ff.cmd)
        ff.run()


        self.video_conversion_collection.update({'_id' : _id_}, { '$set' : {'targetPath' : converted}})
        self.video_conversion_collection.update({'_id' : _id_}, { '$set' : {'tstamp' : time.time()  }})

        payload = dict()
        payload["id"] = _id_;
        payload["status"] = 0;

        json_payload = json.dumps(payload)
        logging.info("payload = %s", json_payload)

        ws = websocket.create_connection(self.url, sslopt={"cert_reqs": ssl.CERT_REQUIRED, "ca_certs" : "ca.cert.pem"})
#        ws = websocket.create_connection(self.url)
        ws.send(json_payload);
        ws.close()

