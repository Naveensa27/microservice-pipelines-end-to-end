output "node_public_ip" {
  description = "Public IP of provisioned instance"
  value       = aws_instance.k8s_node.public_ip
}

output "node_instance_id" {
  description = "AWS EC2 Instance ID"
  value       = aws_instance.k8s_node.id
}