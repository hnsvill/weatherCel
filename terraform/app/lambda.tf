terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.66.0"
    }
  }
}

provider "aws" {
  default_tags {
    tags = {
      environment = "test"
      project     = "weatherCel"
    }
  }
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "iam_for_lambda" {
  name               = "weatherCelRole"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_lambda_function" "test_lambda" {
  function_name = "persistForecast"
  role          = aws_iam_role.iam_for_lambda.arn
  package_type  = "Image"
  image_uri     = "587838441384.dkr.ecr.us-west-1.amazonaws.com/persistforecast:latest"
}


# module "lambda_function_container_image" {
#   source = "terraform-aws-modules/lambda/aws"

#   function_name = "persistforecast"
#   description   = "Ive a feeling we're sometimes in kansas, Todo"

#   # create_package = false

#   image_uri    = "587838441384.dkr.ecr.us-west-1.amazonaws.com/persistforecast:latest"
#   package_type = "Image"
# }
