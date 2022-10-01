import time
import pandas as pd
from pyspark.sql.dataframe import DataFrame
import requests
import warnings
import flickrapi
from pyspark.sql import SparkSession
import json
from elasticsearch import Elasticsearch
import socket
import os
warnings.filterwarnings("ignore")



kafka_server = os.getenv('KAFKA_SERVER')
kafka_topic = 'sink_topic'
classifier_url = f'{os.getenv("CLASSIFIER_HOST")}/classify'
elastic_host = os.getenv('ELASTIC_HOST')
elastic_index = "tap_project"
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
size = os.getenv('IMAGES_SIZE')
recently_processed_ids = []
cache_len = 30


def getToken(api_key, api_secret, response_format="parsed-json"):
    flickr = flickrapi.FlickrAPI(api_key, api_secret, format=response_format)
    return flickr
    """
    if not flickr.token_valid(perms='read'):
        flickr.get_request_token(oauth_callback='oob')
        authorize_url = flickr.auth_url(perms='read')

        print('\n================= USE THIS URL TO GIVE AUTHORIZATION =================\n')
        print(authorize_url)
        print('\n================= TO SEND CODE ATTACH A SHELL AND USE \'nc -u 0 2222\' COMMAND =================\n')
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', 2222))
        data, addr = sock.recvfrom(24)
        verifier = data.decode('utf-8').strip()
        
        flickr.get_access_token(verifier)
    return flickr
    """

def checkDownloadableAndGetDescr(df: pd.DataFrame):
    global flickr
    descr, downloadable = [], []
    for i, row in df.iterrows():
      try:
        info = flickr.photos.getInfo(photo_id=row['photo_id'])['photo']
        downloadable.append(bool(info['usage']['candownload']))
        descr.append(info['description']['_content'])
      except:
        downloadable.append(False)
        descr.append('N/A')
    return downloadable, descr 



def classifyAllImages(df: pd.DataFrame):
    pred_classes, confidence_scores = [], []
    
    for i, row in df.iterrows():
      pred, conf = call_remote_classifier(row['url'])
      pred_classes.append(pred)
      confidence_scores.append(conf)

    return pred_classes, confidence_scores





def call_remote_classifier(image_url):
  global classifier_url
  body = {'url': image_url}
  headers = {'content-type': 'application/json'}
  #max_attempts = 5
  #attempts = 0
  while True:
    try:
      #attempts += 1
      res = requests.post(classifier_url, data=json.dumps(body), headers=headers).json()
      return res['class'], res['conf']
    except Exception as e:
      print('Unable to contact classification endpoint. Retrying...')
      time.sleep(2)
      #if attempts >= max_attempts:
      #  return 'N/A', 0




def connect_to_ES():
  global elastic_host
  global es
  
  while True:
    try:
      es = Elasticsearch(hosts=elastic_host)
      break
    except:
      time.sleep(2)



#date_hour_minute_second_millis
#{"type": "date", "format": "date_time"},
def create_es_index():
  global elastic_host
  global elastic_index

  es_mapping = {
      "mappings": {
          "properties": {
              "ingestion_timestamp": {"type": "date"},
              "photo_id": {"type": "keyword"},
              "owner_id": {"type": "keyword"},
              "title": {"type": "text"},
              "public": {"type": "boolean"},
              "url": {"type":"text"},
              "width" : {"type":"integer"},
              "height": {"type": "integer"},
              "description": {"type":"text"},
              "downloadable": {"type":"boolean"},
              "class": {"type":"keyword"},
              "confidence": {"type":"float"}
          }
      }
  }
  while True:
    try:
      es = Elasticsearch(hosts=elastic_host)
      print('Connection to Elasticsearch established.')
      break
    except:
      print('Unable to connect to Elasticsearch. Retrying...')
      time.sleep(2)

  while True:
    try:
      response = es.indices.create(index=elastic_index, body=es_mapping, ignore=400)
      if 'acknowledged' in response and response['acknowledged'] == True:
        print('Index created successfully.')
        break
      elif response['status'] == 400:
        print('Index already exists.')
        break;
    except Exception as e:
      print(f'Index NOT created: {e}. Retrying...')
      time.sleep(2)



def check_existing(id):
  global es
  global elastic_index
  res = es.exists(index=elastic_index, id=id)
  return res


# timestamp == Ingestion Timestamp
# ogni "row" è un oggetto json che contiene il numero di immagini retrieved da una sola call all'api rest di flickr
def extract_info(row: DataFrame):
  global size
  global recently_processed_ids
  global cache_len
  photos = json.loads(row['raw_data'])['photos']['photo']

  photos_info = {'photo_id':[], 'owner_id':[], 'title':[], 'public': [], 'url':[],\
                'width':[], 'height':[]}

  for photo in photos:
    if photo['id'] not in recently_processed_ids and bool(photo['ispublic']) and f'url_{size}' in photo:
      photos_info['photo_id'].append(photo['id'])
      photos_info['owner_id'].append(photo['owner'])
      photos_info['title'].append(photo['title'])
      photos_info['public'].append(bool(photo['ispublic']))
      photos_info['url'].append(photo[f'url_{size}'])
      photos_info['width'].append(photo[f'width_{size}'])
      photos_info['height'].append(photo[f'height_{size}'])

    recently_processed_ids.append(photo['id'])

  photos_info['ingestion_timestamp'] = [row['timestamp']]*len(photos_info['photo_id'])

  recently_processed_ids = recently_processed_ids[-cache_len:]

  return pd.DataFrame(photos_info)



def all(row: DataFrame):
  new_df = extract_info(row) # è un pd.Dataframe

  new_df['photo_id'] = new_df['photo_id'].astype('int64')

  #connect_to_ES()

  #for i, id in new_df['photo_id'].items():
  #  already_exists = check_existing(id)
  #  if already_exists:
  #    new_df = new_df.drop(i)

  new_df['downloadable'], new_df['description'] = checkDownloadableAndGetDescr(new_df)

  new_df = new_df[new_df['downloadable']]

  #if new_df.size > 0:
  new_df['class'], new_df['confidence'] = classifyAllImages(new_df)
  new_df = new_df[new_df['class'] != 'N/A']

  return new_df
  

def merge_dfs(df1: pd.DataFrame, df2: pd.DataFrame):
  return pd.concat([df1, df2], ignore_index=True)



def elaborate_and_save_to_es(df: DataFrame, epoch_id):
  df.show()
  if not df.rdd.isEmpty():
    out_df = df.rdd.map(all).reduce(merge_dfs)

    if out_df.size > 0:
      global spark

      out_df = spark.createDataFrame(out_df)
      out_df.show()

      global elastic_host
      global elastic_index

    while True:
      try:
        out_df.write \
          .format("org.elasticsearch.spark.sql") \
          .option("es.mapping.id", "photo_id") \
          .mode('append') \
          .save(elastic_index)
        break
      except Exception as e:
        print(f'Unable to save out_df to Elasticsearch: {e}. Retrying...')
        time.sleep(2)



flickr = getToken(api_key, api_secret)

#.config("spark.es.nodes.discovery", False)\
#.config("spark.es.nodes.data.only", False)\
spark = SparkSession\
        .builder\
        .appName('Tap Project')\
        .master('local[*]')\
        .config("spark.es.nodes", elastic_host)\
        .getOrCreate()


create_es_index()


df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafka_server) \
  .option("maxOffsetsPerTrigger", 3) \
  .option("subscribe", kafka_topic) \
  .load()

#"CAST(timestamp as STRING)"   .withColumn("timestamp", from_unixtime("timestamp"))\
#  .selectExpr("raw_data", "to_timestamp(timestamp, 'yyyy-MM-dd HH:mm:ss.SSS') as timestamp")\
df.selectExpr("CAST(value AS STRING) as raw_data", "timestamp")\
  .writeStream\
  .option("checkpointLocation", "/var/tmp/checkpoints")\
  .foreachBatch(elaborate_and_save_to_es)\
  .start()\
  .awaitTermination()
