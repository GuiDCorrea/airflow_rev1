
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 16),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'spark_frequent_patterns_dag',
    default_args=default_args,
    schedule_interval='0 8,12,15,17 * * 1-5', 
    catchup=False,
)

def run_spark_job():
    from pyspark.sql import SparkSession
    from pyspark.ml.feature import StringIndexer
    from pyspark.ml.recommendation import ALS
    from pyspark.sql.functions import col
    import os
    from pyspark.ml.fpm import FPGrowth
    import findspark

    findspark.init(r"/opt/spark")

    os.environ["SPARK_HOME"] = r"/opt/spark"
    os.environ["HADOOP_HOME"] = r"/opt/hadoop"
    #os.environ["JAVA_HOME"] = r"C:\Program Files\Java\jdk-20"

    def process_csv(file_path):
        spark = SparkSession.builder \
            .appName("CSVProcessing") \
            .config("spark.executor.memory", "4g") \
            .config("spark.driver.memory", "2g") \
            .getOrCreate()

        df = spark.read.csv(file_path, sep=";", header=True, inferSchema=True)

        numeric_columns = [item[0] for item in df.dtypes if item[1].startswith('int') or item[1].startswith('double')]
        for col_name in numeric_columns:
            df = df.withColumn(col_name, col(col_name).cast("float"))

        df = df.na.fill(0)

        df = df.withColumn("preco", col("preco").cast("float"))
        df = df.withColumn("custo", col("custo").cast("float"))
        df = df.withColumn("margem", col("margem").cast("float"))
        df = df.withColumn("total", col("total").cast("float"))
        df = df.withColumn("precoconcorrente", col("precoconcorrente").cast("float"))

        return df

    def mine_frequent_patterns(file_path):
        spark = SparkSession.builder \
            .appName("FPGrowth") \
            .config("spark.executor.memory", "4g") \
            .config("spark.driver.memory", "2g") \
            .config("spark.sql.shuffle.partitions", "8") \
            .getOrCreate()

        processed_df = process_csv(file_path)
        processed_df.cache()

        transactions_df = processed_df.groupBy("clienteid").agg({"cod_produto": "collect_list"})
        transactions_df = transactions_df.join(processed_df, on="clienteid")
        transactions_df = transactions_df.repartition(8, "clienteid")

        fp_growth = FPGrowth(itemsCol="collect_list(cod_produto)", minSupport=0.2, minConfidence=0.5)

        model = fp_growth.fit(transactions_df)

        itemsets = model.freqItemsets
        itemsets.show()

        association_rules = model.associationRules
        association_rules.show()

        spark.stop()

    file_path = r"D:\dev0608\vendasals.csv"
    mine_frequent_patterns(file_path)

run_spark_job_task = PythonOperator(
    task_id='run_spark_job_task',
    python_callable=run_spark_job,
    dag=dag,
)

run_spark_job_task
