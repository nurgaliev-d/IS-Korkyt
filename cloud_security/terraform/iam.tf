data "aws_iam_policy_document" "vpc_flow_logs_assume" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["vpc-flow-logs.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "vpc_flow_logs" {
  name               = "${var.project_name}-vpc-flow-logs"
  assume_role_policy = data.aws_iam_policy_document.vpc_flow_logs_assume.json
}

data "aws_iam_policy_document" "vpc_flow_logs" {
  statement {
    effect    = "Allow"
    actions   = ["logs:CreateLogStream", "logs:DescribeLogGroups", "logs:DescribeLogStreams", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.vpc_flow_logs.arn}:*"]
  }
}

resource "aws_iam_role_policy" "vpc_flow_logs" {
  name   = "${var.project_name}-vpc-flow-logs"
  role   = aws_iam_role.vpc_flow_logs.id
  policy = data.aws_iam_policy_document.vpc_flow_logs.json
}

data "aws_iam_policy_document" "workload_assume" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "workload" {
  name               = "${var.project_name}-workload"
  assume_role_policy = data.aws_iam_policy_document.workload_assume.json
}

data "aws_iam_policy_document" "workload_access" {
  statement {
    sid       = "ListApprovedPrefix"
    effect    = "Allow"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.data.arn]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["tenant-a/*"]
    }
  }

  statement {
    sid       = "ReadApprovedObjects"
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.data.arn}/tenant-a/*"]
  }
}

resource "aws_iam_role_policy" "workload_access" {
  name   = "${var.project_name}-workload-access"
  role   = aws_iam_role.workload.id
  policy = data.aws_iam_policy_document.workload_access.json
}

data "aws_iam_policy_document" "security_admin_assume" {
  statement {
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }

    actions = ["sts:AssumeRole"]

    condition {
      test     = "Bool"
      variable = "aws:MultiFactorAuthPresent"
      values   = ["true"]
    }
  }
}

resource "aws_iam_role" "security_admin" {
  name               = "${var.project_name}-security-admin"
  assume_role_policy = data.aws_iam_policy_document.security_admin_assume.json
  managed_policy_arns = [
    "arn:aws:iam::aws:policy/SecurityAudit"
  ]
}
