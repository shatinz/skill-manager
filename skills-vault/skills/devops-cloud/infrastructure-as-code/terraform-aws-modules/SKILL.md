---
id: devops-cloud.infrastructure-as-code.terraform-aws-modules
name: terraform-aws-modules
title: Terraform AWS Modular Architecture & State Management
category: devops-cloud
subcategory: infrastructure-as-code
version: 1.1.0
tags:
- terraform
- aws
- iac
- cloud
- s3
- state-locking
trust_rating: 0.93
estimated_tokens: 1450
description: Design reusable, secure Terraform modules for AWS (VPC, ECS, RDS, IAM,
  S3) with remote S3 backend state locking and zero-hardcoded secrets.
trigger_patterns:
- write terraform module aws
- terraform remote state s3
- iac aws infrastructure terraform
- terraform best practices
---

# Terraform AWS Modular Architecture

## Core Guidelines
- Store state in encrypted S3 bucket with DynamoDB table for state locking.
- Maintain separate environments (`dev`, `staging`, `prod`) using Terragrunt or distinct workspace state prefixes.
- Follow least privilege for IAM role definitions.
