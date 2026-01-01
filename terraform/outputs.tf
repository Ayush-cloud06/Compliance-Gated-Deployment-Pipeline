output "aws_instance_demo" {
  value = {
    for name, instance in aws_instance.demo : name => {
      id = instance.id
      ip = instance.public_ip
    }
  }
}
