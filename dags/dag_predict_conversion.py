from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler
from pyspark.sql.functions import when, col
import os
import findspark
from os.path import abspath
from pyspark.sql import SparkSession
from pyspark.sql import Row
from pyspark import SparkContext, SparkConf
import pandas as pd
import warnings


findspark.init("/opt/spark")
warnings.filterwarnings('ignore')



def start_spark():
    conf = SparkConf()
    conf.set("spark.master", "local[*]")
    conf.set("spark.executor.memory", "6g")
    conf.set("spark.driver.memory", "6g")
    conf.set("spark.sql.adaptive.enabled", "true")
    spark = SparkSession.builder.config(conf=conf).getOrCreate()
    return spark

def load_data(spark, file_path):
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    return df

def replace_nan_with_zero(df):
    for col_name in df.columns:
        df = df.withColumn(col_name, when(col(col_name).isNull(), 0).otherwise(col(col_name)))
    return df

def preprocess_data(df):
    df = replace_nan_with_zero(df)
    
    df = df.withColumn("statusespecificador", when(col("id_especificador").isNull(), 0).otherwise(1))
    
    string_indexer = StringIndexer(inputCol="ds_tipo_obra", outputCol="ds_tipo_obra_index")
    df = string_indexer.fit(df).transform(df)
    
    encoder = OneHotEncoder(inputCols=["ds_tipo_obra_index", "promocional"], outputCols=["ds_tipo_obra_onehot", "promocional_onehot"])
    df = encoder.fit(df).transform(df)
    
    feature_columns = ['periodo_mes', 'ds_tipo_obra_onehot', 'promocional_onehot', 'qt_itens', 'vl_orcamento', 'vl_frete']
    assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
    df = assembler.transform(df)
    
    return df

def train_classification_model(df):
    feature_columns = ['periodo_mes', 'ds_tipo_obra_onehot', 'promocional_onehot', 'qt_itens', 'vl_orcamento', 'vl_frete']
    assembler = VectorAssembler(inputCols=feature_columns, outputCol="new_features")
    
    rf = RandomForestClassifier(labelCol="convertido", featuresCol="new_features", numTrees=100)
    
    pipeline = Pipeline(stages=[assembler, rf])
    model = pipeline.fit(df)
    
    return model

def main():
    spark = start_spark()
    file_path = r"/home/guilherme/airflow_rev6/excelfiles/dataset_orca.csv"
    df = load_data(spark, file_path)
    df_preprocessed = preprocess_data(df)
    
    model = train_classification_model(df_preprocessed)
    
    predictions = model.transform(df_preprocessed)
    
    selected_columns = ["id_quote", "probability"]
    result = predictions.select(*selected_columns)
    
    result.show()



default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 8, 21),
    'depends_on_past': False,
    'retries': 1
}

dag = DAG(
    'spark_ml_pipeline',
    default_args=default_args,
    schedule_interval=None, 
    catchup=False
)

with dag:
    start_task = PythonOperator(
        task_id='start_task',
        python_callable=start_spark
    )

    load_data_task = PythonOperator(
        task_id='load_data_task',
        python_callable=load_data,
        op_args=[file_path]
    )

    preprocess_task = PythonOperator(
        task_id='preprocess_task',
        python_callable=preprocess_data
    )

    train_model_task = PythonOperator(
        task_id='train_model_task',
        python_callable=train_classification_model
    )

    end_task = PythonOperator(
        task_id='end_task',
        python_callable=main
    )

  
    start_task >> load_data_task >> preprocess_task >> train_model_task >> end_task


