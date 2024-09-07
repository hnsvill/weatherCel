# This would belong in another central repo where state buckets could also be managed. 

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
    }
  }
}

resource "aws_ecr_repository" "persistforecast" {
  name = "persistforecast"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    project = "weatherCel"
  }
}
