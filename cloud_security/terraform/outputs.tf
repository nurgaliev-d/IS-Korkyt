output "vpc_id" {
  description = "Қауіпсіз VPC идентификаторы."
  value       = aws_vpc.secure.id
}

output "private_subnet_ids" {
  description = "Жеке subnet идентификаторлары."
  value       = aws_subnet.private[*].id
}

output "workload_role_arn" {
  description = "Ең аз құқықтармен берілген workload рөлінің ARN мәні."
  value       = aws_iam_role.workload.arn
}

output "audit_bucket_name" {
  description = "Аудит журналдарына арналған жабық S3 bucket атауы."
  value       = aws_s3_bucket.audit.id
}
