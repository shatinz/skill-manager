---
id: devops-cloud-serverless.iac-cloud.terraform-aws-modules
name: terraform-aws-modules
title: Terraform AWS Modular Infrastructure as Code (IaC)
category: devops-cloud-serverless
subcategory: iac-cloud
version: 1.3.0
tags:
- terraform
- aws
- iac
- modules
- vpc
- ecs
- s3
- state-locking
trust_rating: 0.97
estimated_tokens: 1600
description: Structure clean, reusable Terraform modules for AWS with S3 remote state
  backends, DynamoDB state locking, least-privilege security groups, and automated
  plan verifications.
trigger_patterns:
- terraform aws module architecture
- terraform s3 backend dynamodb state lock
- terraform vpc security group module
- terraform plan automated validation
---

# Terraform AWS Modular Infrastructure as Code (IaC)

## Objective
Author modular, maintainable, and secure Terraform configurations for AWS cloud infrastructure with remote state locking and strict variable validation.

## Remote Backend & Modular VPC (`main.tf`)
```hcl
terraform {
  required_version = ">= 1.8.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket         = "production-terraform-state-vault"
    key            = "core/infrastructure.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.1"

  name = "${var.environment}-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = var.environment != "production"
}
```

## Anti-Patterns
- ❌ Storing `.tfstate` files in local git repositories.
- ❌ Authoring wide-open ingress rules (`0.0.0.0/0`) on internal database ports.
