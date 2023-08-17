import requests
import pandas as pd
import json 
import sqlalchemy as db
from dotenv import load_dotenv
from datetime import date
import os
import toml 
import subprocess
import boto3
import os
import logging


def mysql_connect(host, user, password, database, port,schema):
    """
    Connect to the database
    """
    engine = db.create_engine(f'mysql+mysqlconnector://{user}:{password}@{database}.{host}:3306/superstore')
    return engine

def get_customer_id(cusid_file):
    """
    Read customer_id_file and return a string list of customer_id
    """
    li=[]
    with open(cusid_file,'rb') as f:
        data = json.load(f)
        for value in data["customerID"].values():
            li.append(str(value))
        
    id_string = "("+ ",".join(li)+")"
    return id_string


def get_customer_data(engine, sql):
    """
    Get customer data from database
    """
    mysql_result = engine.execute(sql)
    records=[]
    for row in mysql_result:
        doc={"id":row[0], "name":row[1], "date":date.today().strftime('%Y-%m-%d')}
        records.append(doc)
    data=json.dumps(records)
    return data
##########

# def get_customer_data_pandas(engine, sql):
    # """
    # Get customer data from database with pandas way
    # """
    # df=pd.read_sql(sql, con=engine)
    # data=df.to_json(orient='records')
    # return data


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))
    
    app_config = toml.load('config.toml')
    
    api_url = app_config['api']['api_url']
    
    host=app_config['db']['host']
    port=app_config['db']['port']
    database=app_config['db']['database']
    schema=app_config['db']['schema']


    load_dotenv()
    user=os.getenv('user')
    password=os.getenv('password')
   
    # read customer_id_file to local
    
    # s3_client = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    s3_client = boto3.client('s3')
    
      
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    
    filepath = "/tmp/" + key
    download_key = key
    
    
    print("bucket:", bucket)
    print("key:", key)
    print("filepath:", filepath)
    print("download_key:", download_key)

   
    directory = "/tmp/input/"
    if not os.path.exists(directory):
        os.makedirs(directory)
        
        
    s3_client.download_file(Bucket=bucket, Key= download_key, Filename=filepath)
    print("File downloaded successfully.")

    directory = "/tmp/input/"
    print("Contents of /tmp/input/ directory:", os.listdir(directory))
    
    # build the connection to the database
    engine = mysql_connect(host, user, password, database, port,schema)
    
    # get the customer id and insert it into the sql statement
    ids = get_customer_id(filepath)

    sql=f"""select customerID, CustomerName
            from customers
            where customerID in {ids} ;
         """
    # print(engine)

    # get the customer data from database
    ### method 1 execute to get result
    data = get_customer_data(engine, sql)

    #  # method 2 use pandas to_json to get result
    # # data = get_customer_data_pandas(engine, sql)

    # post data to api
    request = requests.post(api_url, data=data)
    logging.info("Status code: %s", request.status_code)
    
    return request.status_code