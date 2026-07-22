# Проект 01. Event pipeline: Spring → Kafka → Postgres + observability

**Уровень:** новичок → junior DevOps (средняя сложность)  
**Формат:** учебный end-to-end проект на одной машине (laptop / VM)  
**Срок ориентир:** 2–4 недели по вечерам  
**Результат:** рабочий стек в Docker Compose + README «как поднять / починить / посмотреть логи и дашборды»

---

## Идея одной фразой

Генератор фейковых событий (Spring producer) шлёт сообщения в Kafka → consumer читает топик и пишет в PostgreSQL → логи Java-приложений **и Postgres** собираются в Loki → на дашбордах видно поток сообщений, ошибки и состояние инфраструктуры.

Это не «hello world compose», но и не кластер Kubernetes на три ноды. Ровно тот уровень, где уже есть сеть сервисов, персистентность, брокер и наблюдаемость.

---

## Архитектура (целевой контур)

```text
┌─────────────┐     ┌─────────┐     ┌─────────────┐     ┌────────────┐
│  producer   │────▶│  Kafka  │────▶│  consumer   │────▶│ PostgreSQL │
│ Spring Boot │     │ 1 node  │     │ Spring Boot │     │            │
└──────┬──────┘     └────┬────┘     └──────┬──────┘     └─────┬──────┘
       │                 │                 │                  │
       └────────────┬────┴─────────────────┴──────────────────┘
                    ▼
            ┌───────────────┐
            │  logs (Loki)  │  ← Java + Postgres (+ опционально Kafka)
            └───────┬───────┘
                    ▼
            ┌───────────────┐
            │   Grafana     │◀── metrics (Prometheus)
            └───────────────┘
```

**Поток данных:** fake events → Kafka topic → consumer → таблица в Postgres.

---

## Стек (рекомендация)

| Компонент | Выбор | Почему так |
|-----------|--------|------------|
| Оркестрация | **Docker Compose** | Один `docker compose up`, быстрый цикл обучения; K8s — следующий проект |
| Producer | Spring Boot (напишешь позже) | Генератор нагрузки / фейковых событий |
| Broker | **Kafka 1 брокер**, режим **KRaft** (без ZooKeeper) | Для учёбы хватает; кластер — overkill |
| Consumer | Твой существующий Spring consumer | Реальный код, не учебный stub |
| БД | **PostgreSQL 16** | Куда пишет consumer |
| Логи | **Grafana Loki** + **Alloy** (или Promtail) | Java **и Postgres** (и при желании Kafka) в один стор |
| Дашборды | **Grafana** | И логи, и метрики в одном UI |
| Метрики | **Prometheus** + JMX / Actuator exporters | Видно Kafka lag, JVM, Postgres |

### Почему не ELK и не полный Kafka-кластер

- **ELK (Elasticsearch + Logstash + Kibana)** тяжелее по RAM и настройке. Для первого проекта Loki + Grafana дают тот же навык «собрать логи → искать → алертить» с меньшей болью.
- **3 брокера Kafka** учат репликации, но отнимают время на отладку quorum. Сначала один брокер + понятный pipeline; кластер — этап 2.

---

## Что имитируем (домен)

Выбери один простой домен и держись его — так проще писать producer и схему БД.

**Вариант по умолчанию — платежные/заказы (order events):**

```json
{
  "eventId": "uuid",
  "eventType": "ORDER_CREATED",
  "occurredAt": "2026-07-22T19:00:00Z",
  "orderId": "ORD-10042",
  "userId": "u-778",
  "amount": 1299.50,
  "currency": "RUB",
  "status": "NEW"
}
```

Producer шлёт 10–100 msg/sec (настраиваемо). Consumer пишет строки в `orders` / `events`. На дашборде видно rate, ошибки deserialize, consumer lag.

Другие домены тоже ок: IoT telemetry, клики на сайте, логины — суть одна.

---

## Scope проекта (что обязательно сделать)

### Этап 0. Каркас репозитория

- `docker-compose.yml` (+ `.env.example`)
- папки: `producer/`, `consumer/`, `infra/` (Grafana dashboards, Prometheus config)
- README: схема, порты, команды up/down, smoke-check

### Этап 1. Инфраструктура без своих Java-приложений

Поднять и проверить:

1. PostgreSQL + volume + healthcheck  
2. Kafka (KRaft, 1 node) + создание топика (скрипт или init-контейнер)  
3. Grafana + Loki + Prometheus (пока «пустые», но открываются)

Smoke:

- `kafka-topics.sh --list`
- `psql` → `\dt` / `SELECT 1`
- UI Grafana на `localhost:3000`

### Этап 2. Consumer

- Dockerfile для существующего Spring consumer
- env: `SPRING_KAFKA_*`, `SPRING_DATASOURCE_*`
- миграции схемы (Flyway/Liquibase или SQL init)
- health endpoint (`/actuator/health`)

Проверка: вручную положить сообщение в топик (console producer или kcat) → строка в Postgres.

### Этап 3. Producer (когда дойдёшь)

- Spring Boot: scheduler / loop генерит JSON в топик
- параметры: `messagesPerSecond`, `duration`, вероятность «битого» сообщения (чтобы увидеть ошибки в логах)
- Dockerfile + сервис в compose

### Этап 4. Логи

- Java пишет в stdout (JSON или plain — лучше JSON)
- Postgres тоже пишет в stdout контейнера (официальный образ так и делает по умолчанию)
- Alloy/Promtail забирает логи контейнеров → Loki (один пайплайн на все сервисы)
- В Grafana: Explore по `{service="consumer"}` / `{service="producer"}` / `{service="postgres"}`

Навык: «упал consumer → нашёл stacktrace за 30 секунд без `docker logs` вручную по всем контейнерам». То же для ошибок БД (connection refused, deadlock, slow query — если включишь `log_min_duration_statement`).

#### Add02: логи Postgres в Loki — да

**Да, можно и нужно.** Loki не привязан к Java: он принимает любые текстовые/JSON-логи. В Docker Compose самый простой путь:

1. Контейнер `postgres` уже пишет логи в **stdout/stderr**.
2. Alloy/Promtail читает Docker logging API (или файлы `/var/lib/docker/containers/...`) и шлёт в Loki с лейблом `service=postgres`.
3. В Grafana ищешь: `{service="postgres"} |= "ERROR"` или `|= "FATAL"`.

Что полезно подкрутить в Postgres (через `command` / `postgresql.conf` / env образа):

| Настройка | Зачем |
|-----------|--------|
| `logging_collector` не обязателен в Docker | Достаточно stderr → Docker → Loki |
| `log_min_messages = warning` (или `info`) | Не заливать диск болтовнёй |
| `log_connections` / `log_disconnections = on` | Видно, кто коннектится (удобно при отладке consumer) |
| `log_min_duration_statement = 500` | Медленные запросы ≥ 500 ms в логах |

Не путать: **логи БД** (Loki) и **метрики БД** (Prometheus + postgres_exporter) — разные вещи. Логи отвечают на «что случилось / какая ошибка», метрики — на «сколько коннектов / размер / TPS».

### Этап 5. Дашборды и метрики

Минимум панелей в Grafana:

| Панель | Откуда |
|--------|--------|
| Messages in / out (topic) | Kafka exporter или JMX |
| Consumer lag | Kafka exporter |
| JVM heap / GC | Spring Actuator → Micrometer → Prometheus |
| Postgres connections / size | postgres_exporter |
| Error rate в логах | Loki (LogQL count) |
| Rows inserted / min | SQL / метрика из app |

Бонус: один простой alert (например lag > N или consumer down).

---

## Порты (черновик)

| Сервис | Порт |
|--------|------|
| Producer (если есть HTTP) | 8081 |
| Consumer Actuator | 8082 |
| Kafka | 9092 |
| Postgres | 5432 |
| Grafana | 3000 |
| Prometheus | 9090 |
| Loki | 3100 |

На одной машине не публикуй лишнее наружу — только то, чем пользуешься сам.

---

## Что сознательно НЕ входит (чтобы не расползтись)

- Kubernetes / Helm (следующий проект: перенос этого же стека)
- Мульти-брокер Kafka, MirrorMaker, Schema Registry (можно как optional later)
- Облако (AWS/GCP) — всё локально
- Полноценный CI/CD в GitHub Actions — опционально в конце (build images + compose smoke)

---

## Критерии «проект готов»

- [ ] `docker compose up -d` поднимает весь контур без ручных костылей
- [ ] Producer (или console) → Kafka → Consumer → строка в Postgres
- [ ] Логи producer / consumer / **postgres** видны в Grafana/Loki
- [ ] Есть хотя бы один дашборд с lag / throughput / ошибками
- [ ] README: как запустить, как проверить, типичные поломки (consumer не коннектится к Kafka, миграции, диск volume)
- [ ] (опционально) `docker compose down -v` и снова up — данные/топик пересоздаются предсказуемо

---

## Чему научишься (DevOps-смысл)

1. **Compose как контракт инфраструктуры** — сервисы, сети, volumes, healthchecks, depends_on.  
2. **Асинхронный pipeline** — брокер, топик, consumer group, lag (это любят на собесах).  
3. **Stateful vs stateless** — Postgres/Kafka с диском vs app-контейнеры.  
4. **Observability 101** — логи ≠ метрики; куда смотреть при инциденте.  
5. **12-factor лёгкая версия** — конфиг через env, логи в stdout, healthchecks.

---

## План работ по неделям

| Неделя | Фокус |
|--------|--------|
| 1 | Compose: Postgres + Kafka + Grafana/Loki/Prometheus; README-скелет |
| 2 | Consumer в Docker, запись в БД, первые логи в Loki |
| 3 | Producer + настройка нагрузки; дашборд lag/throughput |
| 4 | Полировка: алерты, скрипт smoke-test, разбор 2–3 инцидентов в NOTES.md |

---

## Optional later (когда базовый контур скучно)

1. Schema Registry + Avro/JSON Schema (совместимость контрактов).  
2. Kafka UI (AKHQ / Redpanda Console) для отладки топиков.  
3. Перенос в Minikube/kind: Deployment + StatefulSet + PVC.  
4. GitHub Actions: build & push images, `compose` integration test.  
5. Второй consumer group / dead-letter topic для «ядовитых» сообщений.

---

## Итог предложения

**Делаем:** локальный event-driven стенд на Docker Compose — Spring producer → Kafka (1 node, KRaft) → Spring consumer → PostgreSQL; логи Java **и Postgres** в Loki; дашборды в Grafana (+ Prometheus).

**Сложность:** средняя — есть брокер и observability, но без K8s и без multi-broker.

**Порядок:** сначала infra + consumer (у тебя уже есть), потом producer и красивые дашборды.

Когда скажешь «поехали» — можно разложить конкретный `docker-compose.yml`, список env и скелет репозитория под этот план.
