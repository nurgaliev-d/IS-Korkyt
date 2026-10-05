# ResiliLab — Chaos Engineering демо-платформасы

Бұл жоба микросервистік жүйенің ақауға төзімділігін (fault tolerance) Chaos Engineering тәсілімен көрсететін интерактивті оқу демонстрациясы.

## Іске қосу

Ешқандай орнату қажет емес: `index.html` файлын браузерде ашыңыз. Немесе VS Code Live Server қолдануға болады.

## Демода не көрсету керек

1. Қалыпты күй: Availability 99.98%, p95 latency 142 ms.
2. **Latency injection**: Payment сервисі баяулайды; retry және circuit breaker әсерін түсіндіріңіз.
3. **Pod failure**: Inventory replica өшеді; cache/fallback қолданылып, пайдаланушыға сервис үзілмейтінін көрсетіңіз.
4. **Network loss**: Gateway мен Order арасындағы байланыс бұзылады; бұл ең қауіпті эксперимент екенін SLO арқылы көрсетіңіз.
5. **Traffic overload**: autoscaling үш replica-ға дейін өтіп, жүктемені ұстайтынын айтыңыз.
6. Барлық сценарийді өшіріп, Recovery мен baseline-ға қайтуды көрсетіңіз.

## Негізгі ұғымдар

| Ұғым | Мағынасы |
|---|---|
| Chaos Engineering | Жүйеге қауіпсіз ортада әдейі ақау енгізіп, төзімділігін тексеру әдісі. |
| Hypothesis | «Inventory pod өшсе де, checkout success rate 99%-дан төмендемейді» сияқты тексерілетін болжам. |
| SLI | Өлшенетін көрсеткіш: availability, success rate, p95 latency. |
| SLO | SLI үшін мақсат: мысалы, availability ≥99.9%. |
| Error budget | SLO бұзылмай тұрып қабылдауға болатын қате қоры. |
| Circuit breaker | Қате сервиске сұранысты уақытша тоқтатып, cascade failure-ді болдырмайды. |

