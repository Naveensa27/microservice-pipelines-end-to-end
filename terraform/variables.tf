variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type    = string
  default = "production"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "subnet_cidr" {
  type    = string
  default = "10.0.1.0/24"
}

variable "instance_type" {
  type    = string
  default = "t3.small"
}

variable "ami_id" {
  description = "Ubuntu 22.04 LTS AMI"
  type        = string
  default     = "ami-0c7217cdde317cfec"
}

variable "key_name" {
  type        = string
  description = "EC2 SSH Key Pair Name"
}

variable "allowed_ssh_cidr" {
  type    = string
  default = "0.0.0.0/0"
}