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
resource "aws_instance" "demo" {
  for_each      = toset(local.server_names)
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  tags = {
    Name        = "${local.Project}-server-${each.key}"
    Environment = "${local.Environment}"
  }
}


