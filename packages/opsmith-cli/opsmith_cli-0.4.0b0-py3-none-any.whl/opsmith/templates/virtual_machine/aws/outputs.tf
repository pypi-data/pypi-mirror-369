output "public_ip" {
  description = "The public IP address of the EC2 instance."
  value       = aws_instance.app_server.public_ip
}

output "instance_id" {
  description = "The ID of the EC2 instance."
  value       = aws_instance.app_server.id
}

output "user" {
  description = "The user for Ansible to connect with."
  value       = "ec2-user"
}
