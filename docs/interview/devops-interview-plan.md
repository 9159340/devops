# План беседы на собеседовании DevOps-инженера

Документ — примерный сценарий технической беседы (middle / middle+). Темы и вопросы собраны по типичным источникам 2025–2026: разборы реальных интервью, подборки вопросов по Linux / Docker / Kubernetes / CI/CD / IaC, материалы по подготовке к DevOps/SRE.

**Как пользоваться:** идите по темам сверху вниз — так часто строится интервью: от Linux и сетей к контейнерам, оркестрации, пайплайнам и эксплуатации. На каждый вопрос готовьте короткий ответ + пример из опыта (метод STAR: Situation → Task → Action → Result).

**Что ценят сейчас:** не определения инструментов, а диагностику инцидентов, trade-off’ы и умение объяснить «что происходит под капотом».

---

## Примерный ход беседы (60–90 мин)

| Этап | Время | Что проверяют |
|------|-------|----------------|
| Знакомство и опыт | 5–10 мин | Стек, зона ответственности, сложный кейс |
| Linux + сеть | 15–20 мин | Диагностика, процессы, TCP/DNS |
| Docker + Kubernetes | 20–25 мин | Контейнеры, поды, probes, отладка |
| CI/CD + IaC | 10–15 мин | Пайплайн, Terraform/Ansible, секреты |
| Мониторинг / инциденты / облако | 10–15 мин | Observability, on-call, HA |
| Вопросы кандидата | 5 мин | Интерес к команде и продукту |

---

## Тема 1. DevOps как подход

**DevOps** (Development + Operations) — практика сближения разработки и эксплуатации: автоматизация поставки, общая ответственность за сервис, быстрая обратная связь.

### Вопрос 1. Что такое DevOps и чем он отличается от «просто администрирования»?
Кратко: культура + процессы + инструменты. Цель — сократить цикл от коммита до продакшена без потери стабильности. Админ часто «держит серверы»; DevOps строит **CI/CD** (Continuous Integration / Continuous Delivery — непрерывная интеграция и доставка), инфраструктуру как код и наблюдаемость.

### Вопрос 2. Опишите свой самый сложный прод-кейс: что сломалось и как чинили?
Готовьте 1–2 истории: симптомы → гипотезы → команды/метрики → root cause → профилактика.

---

## Тема 2. Linux: процессы и сигналы

**Процесс** — программа в выполнении со своим адресным пространством и PID (Process ID). **Поток (thread)** — единица исполнения внутри процесса, делит память с другими потоками.

### Вопрос 1. Чем процесс отличается от потока? Зачем это DevOps?
Лимиты CPU/RAM в контейнере и **cgroup** (control groups — группы контроля ресурсов ядра) действуют на все потоки процесса. От этого зависят `requests`/`limits` в Kubernetes и поведение при OOM.

```bash
ps aux --sort=-%cpu | head -10
ps -eLf | head          # потоки (NLWP)
pstree -p $$
```

### Вопрос 2. Чем SIGTERM отличается от SIGKILL? Почему это важно для контейнеров?
**SIGTERM** (15) — «завершись корректно» (можно обработать). **SIGKILL** (9) — убить сразу, нельзя перехватить. При удалении Pod Kubernetes шлёт SIGTERM, ждёт `terminationGracePeriodSeconds`, затем SIGKILL.

```bash
kill -TERM <pid>        # мягко
kill -9 <pid>           # жёстко (SIGKILL)
# в контейнере: что получает PID 1
docker top <container>
```

---

## Тема 3. Linux: диагностика «тормозов»

Метод **USE**: Utilization (загрузка), Saturation (очереди), Errors (ошибки) — по CPU, памяти, диску, сети.

### Вопрос 1. Сервер «тупит». С чего начнёте?
Смотрите load average, CPU, память/swap, диск (iowait), сеть, логи ядра (OOM).

```bash
uptime
top -bn1 | head -20
free -h
vmstat 1 5
iostat -xz 1 3
ss -tunapl
dmesg -T | grep -iE 'oom|error|fail' | tail
journalctl -k -b --no-pager | grep -i oom
```

### Вопрос 2. Load Average 4.50 2.30 1.10 на 4 ядрах — это плохо?
**Load average** — среднее число задач в очереди на CPU (running + waiting) за 1 / 5 / 15 минут. На 4 ядрах ~4.0 — «все ядра заняты». Важен тренд: 4.5 → 2.3 → 1.1 — нагрузка падает; обратный тренд — проблема нарастает. Высокий LA при низком CPU часто значит **iowait** / процессы в состоянии D.

```bash
nproc
cat /proc/loadavg
mpstat -P ALL 1 3
```

---

## Тема 4. Файловая система, диск, права

**inode** — метаданные файла (права, владелец, указатели на блоки данных). **Soft link (symlink)** — ссылка по пути; **hard link** — ещё одно имя на тот же inode.

### Вопрос 1. `df` показывает свободное место, а писать нельзя. Почему?
Частые причины: кончились inode; нет прав; read-only mount; квота; заполнен конкретный раздел/volume.

```bash
df -h
df -i
mount | column -t
ls -ld /var/log
du -xh /var | sort -h | tail -20
```

### Вопрос 2. Как найти, что забило диск, и безопасно почистить?
Ищите крупные каталоги и открытые удалённые файлы (процесс держит handle — место не освобождается).

```bash
du -xh --max-depth=1 / | sort -h
lsof +L1 | head            # удалённые, но открытые файлы
# ротация логов (пример)
journalctl --disk-usage
journalctl --vacuum-size=500M
```

---

## Тема 5. Сеть: DNS, TCP, HTTP

**DNS** (Domain Name System) — разрешение имён в IP. **TCP** (Transmission Control Protocol) — надёжный поток с handshake. **TLS** (Transport Layer Security) — шифрование поверх TCP. **HTTP** — протокол приложения.

### Вопрос 1. Что происходит, когда вы делаете `curl https://example.com`?
Разбор `curl` → DNS → TCP handshake (SYN/SYN-ACK/ACK) → TLS → HTTP-запрос/ответ → закрытие или keep-alive. Интервьюер ждёт именно эту цепочку, а не «скачивает страницу».

```bash
curl -vI https://example.com
dig +short example.com A
getent hosts example.com
ss -tn dst example.com:443
```

### Вопрос 2. Чем TCP отличается от UDP? Примеры из DevOps.
**TCP** — упорядоченно и с подтверждениями (HTTP, SSH, PostgreSQL). **UDP** — без гарантий доставки, быстрее (DNS-запросы, метрики StatsD, часть VPN).

```bash
ss -tulpn
# DNS обычно UDP/53 (крупные ответы — TCP)
dig @8.8.8.8 example.com
```

---

## Тема 6. Git и ветвление

**Git** — распределённая система контроля версий. **PR/MR** (Pull/Merge Request) — запрос на слияние с ревью.

### Вопрос 1. Какую branching strategy вы использовали?
Часто: trunk-based / GitHub Flow / GitFlow. Важно объяснить: как попадает в prod, как откатываете, как защищаете `main`.

```bash
git status
git log --oneline -10
git branch -vv
git diff main...HEAD
```

### Вопрос 2. Как разрешите конфликт и не сломаете историю команды?
Понять обе стороны, смержить/ребейзнуть осознанно, прогнать тесты, не делать force-push в общие ветки без договорённости.

```bash
git fetch origin
git merge origin/main
# или
git rebase origin/main
git status   # правим конфликты, затем:
git add <files>
git rebase --continue
```

---

## Тема 7. Docker: основы контейнеров

**Контейнер** — изолированный процесс на общем ядре Linux (через **namespaces** — пространства имён, и **cgroups**). Это не полноценная VM.

### Вопрос 1. Чем контейнер отличается от виртуальной машины?
VM — своё ядро и гипервизор; контейнер — изоляция процессов на хостовом ядре, легче и быстрее стартует.

```bash
docker run --rm -it alpine uname -a
docker inspect <container> --format '{{.State.Pid}}'
ps -fp $(docker inspect -f '{{.State.Pid}}' <container>)
```

### Вопрос 2. Контейнер сразу падает. Как отладите?
Логи, exit code, `docker inspect`, запуск с shell/override entrypoint, проверка volume/env/сети.

```bash
docker ps -a
docker logs --tail 100 <container>
docker inspect <container> | less
docker run --rm -it --entrypoint /bin/sh <image>
```

---

## Тема 8. Dockerfile и образы

**Образ** — слоистая файловая система + метаданные. **Layer cache** — переиспользование слоёв при сборке. **Multi-stage build** — сборка в одном stage, runtime-артефакт в другом (меньше итоговый образ).

### Вопрос 1. Чем CMD отличается от ENTRYPOINT?
**ENTRYPOINT** — основная команда контейнера. **CMD** — аргументы по умолчанию (или команда, если ENTRYPOINT нет). Аргументы `docker run` обычно заменяют CMD, но не ENTRYPOINT.

```dockerfile
ENTRYPOINT ["python", "app.py"]
CMD ["--port", "8080"]
```

```bash
docker run --rm myapp --port 9090
docker history myapp:latest
```

### Вопрос 2. Как уменьшить размер образа и ускорить сборку?
Правильный порядок слоёв (редко меняющееся — выше), multi-stage, `.dockerignore`, очистка кэша пакетного менеджера в том же `RUN`, минимальный base image.

```bash
docker build -t myapp:1 .
docker images myapp
dive myapp:1            # если установлен: анализ слоёв
```

---

## Тема 9. Kubernetes: архитектура

**Kubernetes (K8s)** — оркестратор контейнеров. **Control plane** — API Server, etcd, Scheduler, Controller Manager. **Worker node** — kubelet, контейнерный runtime, kube-proxy (или CNI/eBPF).

### Вопрос 1. Из чего состоит кластер Kubernetes?
Опишите control plane vs nodes, роль **etcd** (хранилище состояния кластера), как `kubectl` ходит в API Server.

```bash
kubectl cluster-info
kubectl get nodes -o wide
kubectl get componentstatuses 2>/dev/null || kubectl get --raw='/readyz?verbose'
```

### Вопрос 2. Deployment vs StatefulSet vs DaemonSet — когда что?
**Deployment** — статeless-приложения, rolling update. **StatefulSet** — стабильные имена/диски (БД, очереди). **DaemonSet** — по одному поду на ноду (агенты логов/мониторинга).

```bash
kubectl get deploy,sts,ds -A
kubectl describe deploy <name>
```

---

## Тема 10. Kubernetes: Pod, probes, ресурсы

**Pod** — минимальная единица запуска (один или несколько контейнеров). **Liveness probe** — «жив ли процесс» (иначе рестарт). **Readiness probe** — «готов ли принимать трафик». **Startup probe** — защита медленного старта.

### Вопрос 1. Чем liveness отличается от readiness?
Неправильный liveness на «долго думающий» эндпоинт → рестарты в цикле. Readiness только убирает под из Service endpoints.

```bash
kubectl get pods -o wide
kubectl describe pod <pod>
kubectl get endpoints <service>
```

### Вопрос 2. Что такое requests и limits? Что будет при OOMKilled?
**requests** — гарантия/учёт для scheduler. **limits** — потолок. Превышение memory limit → **OOMKilled** (Out Of Memory). CPU limit — троттлинг, не всегда kill.

```bash
kubectl top pod
kubectl describe pod <pod> | grep -A5 -E 'Limits|Requests|OOM|State'
kubectl get pod <pod> -o jsonpath='{.status.containerStatuses[*].lastState.terminated.reason}{"\n"}'
```

---

## Тема 11. Kubernetes: сеть и типичные сбои

**Service** — стабильный VIP/DNS к подам. **Ingress** — L7-вход (HTTP-маршрутизация). **CNI** (Container Network Interface) — плагин сети подов. **CoreDNS** — DNS внутри кластера.

### Вопрос 1. Как работает DNS внутри кластера?
Под резолвит `my-svc.my-ns.svc.cluster.local` через CoreDNS → ClusterIP Service → endpoints (IP подов).

```bash
kubectl -n kube-system get pods -l k8s-app=kube-dns
kubectl run -it --rm debug --image=busybox:1.36 --restart=Never -- nslookup kubernetes-dns.kube-system
kubectl get svc,endpoints <svc>
```

### Вопрос 2. Pod в CrashLoopBackOff — ваш чеклист?
Events → logs / previous logs → describe (probes, mounts, secrets) → ресурсы/OOM → конфиг/образ → сеть/зависимости.

```bash
kubectl describe pod <pod>
kubectl logs <pod> --tail=200
kubectl logs <pod> --previous
kubectl get events --field-selector involvedObject.name=<pod> --sort-by=.lastTimestamp
```

---

## Тема 12. CI/CD

**CI** (Continuous Integration) — автоматическая сборка/тесты на каждый коммит. **CD** (Continuous Delivery/Deployment) — автоматическая доставка/выкат. **Pipeline** — конвейер стадий (lint → test → build → push → deploy).

### Вопрос 1. Опишите пайплайн «от коммита до прода» для вашего сервиса.
Стадии, артефакты (образ с тегом commit SHA), окружения, ручные approval, откат.

```bash
# примеры локальной проверки «как в CI»
docker build -t myapp:$GIT_SHA .
docker run --rm myapp:$GIT_SHA pytest -q
```

### Вопрос 2. Blue-Green vs Canary vs Rolling — плюсы и минусы?
**Rolling** — постепенная замена (просто, но смешанные версии). **Blue-Green** — два окружения, мгновенный switch/rollback (дорого по ресурсам). **Canary** — малый % трафика на новую версию (нужен хороший мониторинг).

```bash
kubectl rollout status deploy/<name>
kubectl rollout history deploy/<name>
kubectl rollout undo deploy/<name>
```

---

## Тема 13. Infrastructure as Code: Terraform

**IaC** (Infrastructure as Code) — инфраструктура описывается кодом и применяется автоматически. **Terraform** — инструмент declarative IaC (провайдеры AWS/GCP/Azure и др.). **State** — снимок того, что Terraform считает созданным.

### Вопрос 1. Чем Terraform отличается от Ansible?
Terraform чаще про **создание** облачных ресурсов (declarative, state). Ansible — чаще **конфигурация** ОС/ПО (procedural playbooks, agentless по SSH). На практике часто используют вместе.

```bash
terraform init
terraform plan
terraform apply
terraform state list
```

### Вопрос 2. Что такое state и почему его нельзя хранить «как попало»?
В state есть ID ресурсов и иногда секреты. Нужны remote state (S3/GCS + блокировка), ограничение доступа, backend encryption. Drift — расхождение реальности и state.

```bash
terraform plan -detailed-exitcode
terraform refresh   # осторожно в проде; лучше plan и разбор drift
```

---

## Тема 14. Конфигурация: Ansible

**Ansible** — система управления конфигурацией без агента: control node подключается по SSH и применяет **playbook** (YAML-сценарий).

### Вопрос 1. Идемпотентность — что это и зачем?
Повторный запуск playbook приводит систему к тому же желаемому состоянию, не ломая уже настроенное.

```bash
ansible all -m ping -i inventory.ini
ansible-playbook -i inventory.ini site.yml --check   # dry-run
ansible-playbook -i inventory.ini site.yml --limit web
```

### Вопрос 2. Как организуете роли и секреты?
Roles/collections, group_vars/host_vars, Ansible Vault или внешний secret manager (не коммитить пароли в git).

```bash
ansible-vault encrypt group_vars/prod/vault.yml
ansible-vault view group_vars/prod/vault.yml
```

---

## Тема 15. Мониторинг и observability

**Observability** — способность понять состояние системы по внешним сигналам. Три столпа: **metrics** (метрики), **logs** (логи), **traces** (трассировки). Часто стек: **Prometheus** (сбор метрик) + **Grafana** (дашборды) + Loki/ELK для логов.

### Вопрос 1. Какие метрики «золотых сигналов» смотрите для HTTP-сервиса?
Latency, traffic, errors, saturation (по Google SRE). Плюс RED (Rate, Errors, Duration) для сервисов.

```bash
# примеры локальной проверки экспортера
curl -s localhost:9090/metrics | head
curl -s localhost:9100/metrics | grep -E 'node_cpu|node_memory' | head
```

### Вопрос 2. Как отличить симптом от причины в алерте?
Алерт «5xx выросли» — симптом. Дальше: была ли выкладка, зависимость (БД/кэш), saturation ноды, ошибки в логах, изменение трафика.

```bash
# корреляция по времени выкладки и событиям K8s
kubectl get events -A --sort-by=.lastTimestamp | tail -30
```

---

## Тема 16. Облако (часто AWS как пример)

**VPC** (Virtual Private Cloud) — изолированная сеть в облаке. **IAM** (Identity and Access Management) — кто что может. **AZ** (Availability Zone) — изолированная зона доступности в регионе.

### Вопрос 1. Как спроектируете публичный веб-сервис в облаке?
Публичный ALB/NLB → private subnet с compute (ASG/EKS) → private DB subnet; NAT для исходящего; Security Groups по принципу least privilege; Multi-AZ.

```bash
# пример AWS CLI (если настроен профиль)
aws sts get-caller-identity
aws ec2 describe-instances --filters Name=instance-state-name,Values=running --query 'Reservations[].Instances[].InstanceId'
```

### Вопрос 2. Как безопасно зайти на инстанс в private subnet?
Bastion / SSM Session Manager (предпочтительнее открытого SSH 0.0.0.0/0), короткоживущие доступы, audit trail.

```bash
aws ssm start-session --target i-0123456789abcdef0
```

---

## Тема 17. Безопасность и секреты

**Secret** — чувствительные данные (пароли, токены, ключи). **RBAC** (Role-Based Access Control) — доступ по ролям. **Least privilege** — минимум необходимых прав.

### Вопрос 1. Почему env с паролями — плохая идея и что лучше?
Env виден в `docker inspect`, `/proc`, часто попадает в логи/дампы. Лучше: Vault / cloud secret manager / sealed secrets / CSI drivers; ротация; не писать секреты в образ и git.

```bash
# плохо: секрет в истории образа / env
docker inspect <container> --format '{{range .Config.Env}}{{println .}}{{end}}'
# в K8s секреты всё равно base64, не «шифрование»
kubectl get secret <name> -o yaml
```

### Вопрос 2. Как ограничить права сервиса в Kubernetes?
ServiceAccount + Role/RoleBinding, запрет privileged, read-only root FS, drop capabilities, NetworkPolicy, admission policies.

```bash
kubectl auth can-i list secrets --as=system:serviceaccount:default:my-sa
kubectl get sa,role,rolebinding -n <ns>
```

---

## Тема 18. SRE, инциденты, надёжность

**SRE** (Site Reliability Engineering) — инженерия надёжности сервисов. **SLA/SLO/SLI** — договорённость / целевой уровень / индикатор. **MTTR** — среднее время восстановления. **Postmortem** — разбор инцидента без поиска виноватых.

### Вопрос 1. Как ведёте себя при ночном инциденте?
Стабилизировать (mitigate) → коммуникация → диагностика → fix → мониторинг → postmortem и action items.

```bash
# быстрый «пульс» сервиса
curl -sI https://app.example.com/healthz
kubectl get pods -n prod
kubectl top nodes
```

### Вопрос 2. Что такое error budget и зачем он нужен?
**Error budget** — допустимая доля ошибок/даунтайма в рамках SLO. Если бюджет исчерпан — тормозим фичи, чиним надёжность.

---

## Тема 19. Балансировка и высокая доступность

**Load balancer** — распределение трафика. **Reverse proxy** — прокси «перед» бэкендами (TLS, кэш, маршрутизация). **HA** (High Availability) — устойчивость к отказу узлов. **L4** — по IP/порту; **L7** — по HTTP-заголовкам/пути.

### Вопрос 1. Чем L4-балансировка отличается от L7?
L4 быстрее и проще; L7 умнее (path-based routing, canary по заголовку), но дороже по CPU и сложнее.

```bash
# локальный пример проверки бэкендов за nginx
curl -sI http://127.0.0.1/health
nginx -t && systemctl reload nginx
```

### Вопрос 2. Как обеспечите zero-downtime деплой?
Readiness probes, rolling/canary, graceful shutdown (SIGTERM), connection draining, миграции БД backward-compatible, быстрый rollback.

```bash
kubectl set image deploy/myapp myapp=registry/myapp:1.2.3
kubectl rollout status deploy/myapp
```

---

## Тема 20. Базы данных глазами DevOps

Не «напишите сложный SQL», а доступность: бэкапы, репликация, миграции, диски, соединения.

### Вопрос 1. Синхронная vs асинхронная репликация — trade-off?
Синхронная — меньше риск потери данных, выше latency записи. Асинхронная — быстрее запись, риск lag и потери при падении primary.

```bash
# PostgreSQL: грубая проверка репликации (на primary/replica)
psql -c "SELECT client_addr, state, sync_state FROM pg_stat_replication;"
psql -c "SELECT pg_is_in_recovery();"
```

### Вопрос 2. Как встроить миграции БД в CI/CD без даунтайма?
Expand/contract: сначала совместимые с старой версией изменения → выкат приложения → удаление старого. Бэкап/rollback plan до миграции. Не делать breaking change в одном шаге с деплоем, который это требует.

```bash
# пример идеи, не привязанной к конкретному инструменту
pg_dump -Fc -f backup_$(date +%F).dump mydb
# migrate up (flyway/liquibase/alembic — по стеку команды)
```

---

## Чеклист перед собеседованием

- [ ] 5 историй из опыта (инцидент, ускорение пайплайна, экономия $, миграция, security fix)
- [ ] Уметь вслух пройтись по `curl https://...` и по CrashLoopBackOff
- [ ] Локально поднять mini-lab: Docker Compose или kind/minikube и «сломать/починить»
- [ ] Повторить команды: `ps`/`top`/`ss`/`journalctl`, `docker logs/inspect`, `kubectl describe/logs/rollout`
- [ ] Подготовить вопросы работодателю: on-call, стек, размер кластера, как измеряют успех DevOps

## Полезные ориентиры для углубления

- Подборки реальных вопросов DevOps/SRE 2026 (Linux, Docker, Kubernetes, CI/CD, IaC)
- Репозитории вроде DevOps Interview Questions / hands-on DevOps interview tasks
- Разборы этапов собеседований (HR → Linux/сеть → K8s → архитектура)
- Официальная документация: Kubernetes docs, Docker docs, Terraform docs

---

*Документ учебный: адаптируйте глубину ответов под Junior / Middle / Senior и под стек вакансии (AWS vs GCP, GitLab CI vs GitHub Actions, Ansible vs Salt и т.д.).*
