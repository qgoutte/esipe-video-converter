import logging
import boto3
from botocore.exceptions import ClientError
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
            response = self.table.update_item(
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
