# Бұлттық қауіптер матрицасы

Бұл матрица жобаның AWS-бағытталған зертханалық архитектурасы үшін жасалды. Ықтималдық пен әсер 1-ден 5-ке дейін бағаланады. Жалпы тәуекел ұпайы осы екі мәннің көбейтіндісімен есептеледі.

| ID | Қауіп | Актив | Ықтималдық | Әсер | Ұпай | Қорғаныс шарасы | Бақылау құралы |
|---|---|---|---:|---:|---:|---|---|
| T01 | Қате IAM құқықтары | IAM, S3 | 4 | 5 | 20 | Ең аз құқық, бөлек рөлдер, MFA | IAM Policy, Trivy |
| T02 | Қоғамға ашық сақтау қоймасы | S3 | 4 | 5 | 20 | Public Access Block, bucket policy | Cloud Custodian |
| T03 | Құпия кілттің жария болуы | API кілттері | 3 | 5 | 15 | Кілтті кодқа жазбау, Secret Manager | Trivy secret scan |
| T04 | API аутентификациясының әлсіздігі | REST API | 3 | 5 | 15 | MFA, қысқа мерзімді токен, TLS | OWASP API Top 10 |
| T05 | Шифрлаудың болмауы | S3, EBS, RDS | 3 | 5 | 15 | KMS, сақтау және тасымалдау кезінде шифрлау | Trivy, Terraform |
| T06 | Желі портының ашық қалуы | VPC, security group | 3 | 5 | 15 | Жеке subnet, тар ingress ережелері | Trivy, tfsec |
| T07 | Аудит журналдарының өшірілуі | CloudTrail, CloudWatch | 2 | 5 | 10 | Multi-region Trail, log validation, retention | CloudTrail |
| T08 | Ескі осал компонент | VM, контейнер | 4 | 4 | 16 | Нұсқаларды бекіту, жаңарту, сканерлеу | Trivy |
| T09 | SSRF немесе metadata API шабуылы | Қолданба | 3 | 5 | 15 | Шығыс трафикті шектеу, metadata hardening | OWASP, runtime logs |
| T10 | Ресурсты заңсыз пайдалану | Есептеу ресурстары | 3 | 4 | 12 | Лимиттер, мониторинг, anomaly alert | CloudWatch |
| T11 | Деректерді жою немесе ransomware | S3, backup | 2 | 5 | 10 | Versioning, backup, deny-delete рөлі | CloudTrail |
| T12 | Сенімді байланысқа жасалған шабуыл | CI/CD, сыртқы API | 3 | 4 | 12 | Қолтаңба, тәуелділіктерді тексеру | Trivy, review |

## Қауіптерді жіктеу негізі

- OWASP API Security Top 10: аутентификация, объект деңгейіндегі авторизация, SSRF, қауіпсіздік конфигурациясы және ресурсты шектеу мәселелері.
- MITRE ATT&CK Cloud: Valid Accounts, Cloud Administration Command, Cloud Infrastructure Discovery, Data from Cloud Storage және Resource Hijacking сияқты шабуыл техникасы.
- Terraform security baseline: ашық желіге ingress бермеу, public storage-ті жабу, KMS шифрлауы, MFA және аудит журналдары.

Ұпайы 15 немесе одан жоғары қауіптер бірінші кезекте азайтылуы керек.
