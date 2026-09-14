data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.secure.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 1)
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.project_name}-private-${count.index + 1}"
    Tier = "private"
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.secure.id

  tags = {
    Name = "${var.project_name}-private-routes"
  }
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "application" {
  name        = "${var.project_name}-application"
  description = "Қолданба қабаты үшін жеке қауіпсіздік тобы"
  vpc_id      = aws_vpc.secure.id

  egress {
    description = "Тек VPC ішіндегі шығатын трафик"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.vpc_cidr]
  }
}

resource "aws_security_group" "database" {
  name        = "${var.project_name}-database"
  description = "Дерекқорға тек қолданба тобынан кіру"
  vpc_id      = aws_vpc.secure.id

  ingress {
    description     = "PostgreSQL тек қолданба қабатынан"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.application.id]
  }

  egress {
    description = "VPC ішіндегі жауап трафигі"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.vpc_cidr]
  }
}
