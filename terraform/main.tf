terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1" 
}

resource "aws_s3_bucket" "raw_zone" {
  bucket        = "shreya-stock-pipeline-raw-zone" #storage layer
  force_destroy = true 
}

resource "aws_s3_bucket" "analytics_zone" {
  bucket        = "shreya-stock-pipeline-analytics-zone" 
  force_destroy = true
}

resource "aws_iam_role" "lambda_role" {   # IAM Role for AWS Lambda
  name = "stock_pipeline_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}


resource "aws_iam_role_policy_attachment" "lambda_logs" {                       
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"     # Basic Execution (CloudWatch Logs creation) to Lambda Role attachment
}


resource "aws_iam_role_policy" "lambda_s3_write" {
  name = "lambda_s3_write_policy"
  role = aws_iam_role.lambda_role.id   #files into raw s3 bucket

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:PutObject"]
      Resource = "${aws_s3_bucket.raw_zone.arn}/*"
    }]
  })
}


resource "aws_iam_role" "glue_role" {       
  name = "stock_pipeline_glue_role"     # IAM Role for AWS Glue

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "glue.amazonaws.com" }
    }]
  })
}


resource "aws_iam_role_policy_attachment" "glue_service" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}


resource "aws_iam_role_policy" "glue_s3_policy" {
  name = "glue_s3_access_policy"
  role = aws_iam_role.glue_role.id   #Read Raw data, write clean Parquet data

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:ListBucket"]
        Resource = [aws_s3_bucket.raw_zone.arn, "${aws_s3_bucket.raw_zone.arn}/*"]
      },
      {
        Effect   = "Allow"
        Action   = ["s3:PutObject", "s3:GetObject", "s3:DeleteObject", "s3:ListBucket"]
        Resource = [aws_s3_bucket.analytics_zone.arn, "${aws_s3_bucket.analytics_zone.arn}/*"]
      }
    ]
  })
}


data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/../src/lambda/lambda_function.py"
  output_path = "${path.module}/lambda_function.zip"   #INGESTION LAYER (AWS LAMBDA) packages local python script into development zip
}

resource "aws_lambda_function" "ingestion_lambda" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "StockDataIngestion"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime          = "python3.12"
  timeout          = 300 # 5 minutes execution window to handle web scraping

  
  environment {
    variables = {
      RAW_BUCKET_NAME = aws_s3_bucket.raw_zone.id
    }
  }
}



resource "aws_cloudwatch_event_rule" "friday_market_close" {  
  name                = "friday_market_close_trigger"
  description         = "Triggers Ingestion Lambda every Friday at 6:00 PM UTC"
  schedule_expression = "cron(0 18 ? * FRI *)"    #Eventbridge schedule
}

resource "aws_cloudwatch_event_target" "trigger_lambda" {
  rule      = aws_cloudwatch_event_rule.friday_market_close.name
  target_id = "TriggerStockLambda"
  arn       = aws_lambda_function.ingestion_lambda.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingestion_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.friday_market_close.arn
}




resource "aws_s3_object" "glue_script" {
  bucket = aws_s3_bucket.analytics_zone.id
  key    = "scripts/glue_etl.py"
  source = "${path.module}/../src/glue/glue_etl.py"
  etag   = filemd5("${path.module}/../src/glue/glue_etl.py")    #AWS Glue ETL job. uploading of local script to S3 to read by glue cluster
}

resource "aws_glue_job" "etl_job" {
  name         = "StockRevenueTransformJob"
  role_arn     = aws_iam_role.glue_role.arn
  glue_version = "4.0"
  worker_type  = "G.1X"
  number_of_workers = 2 # Small footprint to optimize for low cost

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.analytics_zone.id}/${aws_s3_object.glue_script.key}"
    python_version  = "3"
  }

 
  default_arguments = {
    "--RAW_BUCKET"          = aws_s3_bucket.raw_zone.id
    "--ANALYTICS_BUCKET"    = aws_s3_bucket.analytics_zone.id
    "--job-bookmark-option" = "job-bookmark-disable"
  }
}