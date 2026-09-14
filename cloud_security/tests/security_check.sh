#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"
terraform_dir="$project_dir/terraform"

test -f "$project_dir/README.md"
test -f "$project_dir/docs/threat-matrix.md"
test -f "$project_dir/docs/architecture.md"
test -f "$project_dir/docs/incident-response.md"
test -f "$project_dir/docs/tool-comparison.md"
test -f "$project_dir/policies/cloud-custodian.yml"
test -f "$project_dir/scripts/run_audit.sh"
test -f "$terraform_dir/main.tf"
test -f "$terraform_dir/network.tf"
test -f "$terraform_dir/iam.tf"
test -f "$terraform_dir/data-protection.tf"
test -f "$terraform_dir/audit.tf"

grep -q 'enable_key_rotation' "$terraform_dir/data-protection.tf"
grep -q 'block_public_acls' "$terraform_dir/data-protection.tf"
grep -q 'aws:SecureTransport' "$terraform_dir/data-protection.tf"
grep -q 'aws:MultiFactorAuthPresent' "$terraform_dir/iam.tf"
grep -Eq 'sse_algorithm[[:space:]]*=[[:space:]]*"aws:kms"' "$terraform_dir/audit.tf"
grep -q '0.0.0.0/0' "$terraform_dir/network.tf" && {
  echo "network.tf must not expose an ingress rule to the whole internet"
  exit 1
}
if rg -n '(access_key|secret_key|secret_id|password)\s*=\s*"' "$terraform_dir"; then
  echo "Terraform must not contain hardcoded secrets"
  exit 1
fi

echo "cloud security static checks passed"
