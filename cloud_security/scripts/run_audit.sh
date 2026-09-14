#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")/.." && pwd)"

echo "1/4: Репозиторийдің қауіпсіздік baseline тексеруі"
bash "$project_dir/tests/security_check.sh"

echo "2/4: Terraform формат тексеруі"
if command -v terraform >/dev/null 2>&1; then
  terraform -chdir="$project_dir/terraform" fmt -check -recursive
else
  echo "Terraform орнатылмаған — fmt тексеруі өткізіліп кетті"
fi

echo "3/4: Trivy немесе tfsec IaC тексеруі"
if command -v trivy >/dev/null 2>&1; then
  trivy config "$project_dir/terraform"
elif command -v tfsec >/dev/null 2>&1; then
  tfsec "$project_dir/terraform"
else
  echo "Trivy/tfsec орнатылмаған — сыртқы IaC сканері өткізіліп кетті"
fi

echo "4/4: Cloud Custodian policy файлы"
if command -v custodian >/dev/null 2>&1; then
  echo "Cloud Custodian табылды. Нақты AWS аккаунтында policy-ді credentials арқылы іске қосыңыз."
else
  echo "Cloud Custodian орнатылмаған — policy қолмен тексеруге дайын"
fi

echo "Аудит сценарийі аяқталды"
