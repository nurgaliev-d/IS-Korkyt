# Презентация: Chaos Engineering көмегімен микросервистердің fault tolerance-ын тестілеу

## 1. Тақырып және мақсат

**ResiliLab: Chaos Engineering арқылы микросервистік жүйелердің ақауға төзімділігін бағалау.**

Мақсат: қателер шынайы ортада болғанға дейін оларды бақыланатын тәжірибе арқылы тауып, қолданушыға әсерін өлшеу.

## 2. Мәселе

- Микросервистер бір-біріне желі арқылы тәуелді.
- Бір сервис баяуласа не өшсе, cascade failure туындауы мүмкін.
- Кәдімгі unit/integration test көбіне желі үзілуі, latency, overload сияқты өндірістік қателерді толық модельдемейді.

## 3. Chaos Engineering деген не?

Бұл — жүйеге бақылаулы түрде ақау енгізіп, оның төзімділігі туралы гипотезаны тексеру әдісі.

Цикл: **Hypothesis → Inject fault → Observe metrics → Learn → Improve**.

Маңыздысы: мақсат жүйені «сындыру» емес, оны сенімдірек ету.

## 4. Ұсынылған архитектура

`Client → API Gateway → Order Service → Payment Service және Inventory Service`

- Gateway: timeout және rate limiting;
- Payment: retry және circuit breaker;
- Inventory: cache/fallback;
- Observability: logs, metrics, traces;
- Platform: эксперименттерді қосып, SLI/SLO-ны өлшейді.

## 5. Гипотеза және метрикалар

Мысал гипотеза: «Inventory pod істен шыққанда fallback бар болса, checkout success rate 99%-дан төмендемейді».

| SLI | SLO |
|---|---|
| Availability | ≥ 99.9% |
| Success rate | ≥ 99% |
| p95 latency | ≤ 500 ms |
| Error budget | ≥ 30% |

Fault Tolerance Score — осы көрсеткіштерден жасалған демонстрациялық агрегаттық баға.

## 6. Chaos сценарийлері

1. **Latency injection** — Payment-ке +1500 ms кідіріс.
2. **Pod failure** — Inventory replica-сын өшіру.
3. **Network loss** — Gateway → Order жолында 30% packet loss.
4. **Traffic overload** — сұраныс санын 5 есе өсіру.

## 7. Қорғаныс механизмдері

- **Timeout**: ұзақ күткен сұранысты тоқтатады.
- **Retry + exponential backoff**: уақытша қатені қайта орындап көреді.
- **Circuit breaker**: істен шыққан тәуелділікке сұранысты шектейді.
- **Fallback / cache**: балама жауап қайтарады.
- **Autoscaling**: жүктемеде replica санын көбейтеді.

## 8. Платформа демонстрациясы

1. `index.html` ашыңыз, baseline-ды көрсетіңіз.
2. Әр экспериментті қосыңыз.
3. Қызмет түстері, Experiment log және метрикаларды түсіндіріңіз.
4. SLO бұзылса, қандай механизм іске қосылғанын көрсетіңіз.
5. Reset жасап, recovery-ді көрсетіңіз.

## 9. Нәтиже және қорытынды

Платформа қате түрлерінің әсерін көрнекі бағалайды және әлсіз жерді ерте табуға көмектеседі.

Негізгі қорытынды: fault tolerance тек replica саны емес; ол observability, нақты SLO, дұрыс timeout/retry және graceful degradation комбинациясы.

## 10. Болашақ даму

- Docker/Kubernetes-пен нақты сервиске қосу;
- Prometheus + Grafana метрикаларын жалғау;
- LitmusChaos немесе Chaos Mesh пайдалану;
- эксперименттерге қауіпсіздік шегі (blast radius) мен автоматты тоқтату шартын қосу.
