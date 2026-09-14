# Қауіпсіздік аудиті туралы есеп

## Аудит нысаны

Аудит нысаны — `terraform/` каталогындағы AWS қауіпсіздік baseline конфигурациясы және Cloud Custodian policy-лері.

## Репозиторийдегі статикалық тексеру

Жергілікті қауіпсіздік тесті мына талаптарды тексереді:

- жеке subnet-тер бар;
- интернетке ашық ingress ережесі жоқ;
- S3 Public Access Block толық қосылған;
- S3 және аудит журналдары KMS арқылы шифрланады;
- KMS кілтінің автоматты ротациясы қосылған;
- IAM workload рөлі тек қажетті S3 prefix-ке ғана рұқсат алады;
- әкімші рөлі MFA талап етеді;
- Terraform каталогында hardcoded secret жоқ.

Іске қосу:

```bash
bash tests/security_check.sh
```

Күтілетін нәтиже:

```text
cloud security static checks passed
```

Осы жобадағы бастапқы іске қосу нәтижесі: **PASS**. Скрипт public ingress, hardcoded secret, S3 public access, KMS rotation, TLS талабы және MFA шарттарын тексерді.

## Құралдық аудит

Егер компьютерде құралдар орнатылған болса:

```bash
trivy config terraform/
tfsec terraform/
custodian run policies/cloud-custodian.yml --output-dir reports/custodian-output
```

Бұл репозиторийдегі статикалық тесттер қауіпсіз baseline-тің негізгі қасиеттерін тәуелсіз тексереді. Trivy, tfsec және Cloud Custodian нәтижелері қолданылған нұсқаға және нақты AWS аккаунтындағы ресурстарға тәуелді, сондықтан оларды жалған түрде «нөл қате» деп көрсетпей, нақты іске қосылғаннан кейін осы есепке қосу керек.
