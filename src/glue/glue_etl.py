import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, to_date


args = getResolvedOptions(sys.argv, ['JOB_NAME', 'RAW_BUCKET', 'ANALYTICS_BUCKET'])   #Glue context intialization
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

RAW_PATH = f"s3://{args['RAW_BUCKET']}/raw/"
OUTPUT_PATH = f"s3://{args['ANALYTICS_BUCKET']}/analytics-zone/"

def process_stock(file_name, output_folder):
    df = spark.read.json(RAW_PATH + file_name)
    
    clean_df = df.withColumn("Date", to_date(col("Date"), "yyyy-MM-dd")) \
                 .withColumn("Close", col("Close").cast("double")) \
                 .withColumn("Open", col("Open").cast("double")) \
                 .withColumn("High", col("High").cast("double")) \
                 .withColumn("Low", col("Low").cast("double")) \
                 .withColumn("Volume", col("Volume").cast("long")) \
                 .filter(col("Date").isNotNull())   #schema cleaning and casting
                 
    clean_df.write.mode("overwrite").parquet(OUTPUT_PATH + output_folder)

def process_revenue(file_name, output_folder):
    df = spark.read.json(RAW_PATH + file_name)
    
   
    clean_df = df.withColumn("Revenue_Clean", regexp_replace(col("Revenue"), "[\\$,]", "")) \
                 .filter((col("Revenue_Clean") != "") & (col("Revenue_Clean").isNotNull())) \
                 .withColumn("Revenue", col("Revenue_Clean").cast("double")) \
                 .withColumn("Date", to_date(col("Date"), "yyyy-MM-dd")) \
                 .select("Date", "Revenue") \
                 .filter(col("Date").isNotNull())    # string changes, filtering etc
                 
    clean_df.write.mode("overwrite").parquet(OUTPUT_PATH + output_folder)


print("Processing Stock Data...")   # execution 
process_stock("tesla_stock.json", "tesla_stock")
process_stock("gme_stock.json", "gme_stock")

print("Processing Revenue Data...")
process_revenue("tesla_revenue.json", "tesla_revenue")
process_revenue("gme_revenue.json", "gme_revenue")

job.commit()