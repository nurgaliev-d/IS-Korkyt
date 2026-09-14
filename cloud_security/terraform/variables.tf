variable "aws_region" {
  description = "AWS аймағы. Құпия дерек емес."
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Жоба атауы."
  type        = string
  default     = "cloud-security-lab"
}

variable "environment" {
  description = "Инфрақұрылым ортасы."
  type        = string
  default     = "lab"
}

variable "vpc_cidr" {
  description = "Жеке VPC желісінің CIDR диапазоны."
  type        = string
  default     = "10.20.0.0/16"
}

variable "log_retention_days" {
  description = "Аудит журналдарын сақтау мерзімі."
  type        = number
  default     = 90

  validation {
    condition     = var.log_retention_days >= 30
    error_message = "Журналдар кемінде 30 күн сақталуы керек."
  }
}
