locals {
  Project      = "project_compute_setup"
  Environment  = "prod"
  server_names = ["instance-a", "instance-b", "instance-c"]
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

data "aws_iam_instance_profile" "ec2_profil" {
  name = "ec2-basic-profile"
}

resource "aws_instance" "demo" {
  for_each      = toset(local.server_names)
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  iam_instance_profile = data.aws_iam_instance_profile.ec2_profile.name

  monitoring    = true
  ebs_optimized = true

  metadata_options {
    http_tokens = "required"
  }

  root_block_device {
    encrypted = true
  }

  tags = {
    Name        = "${local.Project}-server-${each.key}"
    Environment = local.Environment
  }
}
