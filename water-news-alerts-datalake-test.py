from pyspark.sql import SparkSession

# Create a Spark session
spark = SparkSession.builder \
    .appName("MinIOParquetQuery") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.2.0") \
    .getOrCreate()

# Set the Hadoop configuration for MinIO
spark._jsc.hadoopConfiguration().set("spark.hadoop.fs.s3a.endpoint", "localhost:9000")
spark._jsc.hadoopConfiguration().set("spark.hadoop.fs.s3a.access.key", "wwshPJOj3n2eKrSOAf0O")
spark._jsc.hadoopConfiguration().set("spark.hadoop.fs.s3a.secret.key", "dGNHTGdvm95GHEWY02qweeZmSo7TSYgsdQePEdRk")
spark._jsc.hadoopConfiguration().set("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
spark._jsc.hadoopConfiguration().set("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")

# Read Parquet file from MinIO
df = spark.read.parquet("s3a://water-news-alerts/processed/media/water-news-alert_20250217_162945.parquet")

# Show the first few rows of the data
df.show()

# You can now perform Spark SQL queries or transformations on the DataFrame

# Initialize Spark Session
spark = SparkSession.builder.appName("MinIOParquetQuery").getOrCreate()

# Read the Parquet file from MinIO
df = spark.read.parquet("s3a://water-news-alerts/processed/media/water-news-alert_20250217_162945.parquet")

# Show the first few rows
df.show()
