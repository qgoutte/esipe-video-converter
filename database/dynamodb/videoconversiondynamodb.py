import logging
import boto3
from botocore.exceptions import ClientError
from random import randint
import ffmpy
import json
import decimal

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

class VideoConversionDynamoDB(object):
    def _init_(self,_config_):
        dynamodb = boto3.resource(_config_.get_db_name(), region_name=_config_.get_db_region())
        self.table = dynamodb.Table(_config_.get_database_table())
        logging.info(self.table.creation_date_time)

    def update_statut(self,uuid,status):
        try:
            logging.info("BEGIN UPDATE")
            self.table.update_item(
                Key={'uuid': uuid},
                UpdateExpression='set status = :status',
                ExpressionAttributeValues={':status': status},
                ReturnValues="FINISHED"
            )
            logging.info("END UPDATE")
        except ClientError as e:
            logging.error("Error during the update: ", e)
        else:
            logging.info('Update finished')

    def convert(self, path):
        key = self.get_last_split(path, '/')
        extension = self.get_last_split(key, '.')
        n = str(randint(0, 100))
        try:
            self.s3.Bucket(self.configuration.get_bucket_name()).download_file(key, 'local_temp_' + n + '.' + extension)
            ff = ffmpy.FFmpeg(
                inputs={'local_tmp_' + n + '.' + extension: None},
                outputs={'output_tmp_' + n + '.avi': '-y -vcodec mpeg4 -b 4000k -acodec mp2 -ab 320k'}
            )
            ff.run()
            self.client.upload_file('output_temporary_' + n + '.avi', self.configuration.get_s3_name(),
                                    key.replace(extension, 'avi'))
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                logging.error('Dont exist.')
            else:
                raise