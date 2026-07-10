# Задача 001. Deploy веб-приложения on-premise

**Роль:** DevOps-инженер  
**Формат:** проектная задача (end-to-end)  
**Среда:** собственный ЦОД / серверная комната (on-premise — развёртывание на своей инфраструктуре, без публичного облака как основной площадки)

---

## Контекст

Компания запускает внутренний веб-сервис (REST API + SPA). Нужно развернуть его **on-premise** на Linux-серверах так, чтобы приложение было доступно сотрудникам по HTTPS, пережило перезагрузку хоста и имело понятный процесс обновления.

Стек приложения (условно):

- backend: Python/FastAPI или аналог
- frontend: статика (React/Vue build)
- БД: PostgreSQL
- артефакты: Docker-образы в локальном registry **или** deb/rpm + systemd (на выбор команды)

---

## Цель

Поднять рабочий контур **dev → staging → prod** (минимум staging + prod) на своих серверах и задокументировать, как деплоить, откатывать и чинить.

---

## Scope (что входит)

### 1. Инфраструктура

- 2+ Linux-хоста (VM или bare metal): `app`, `db` (допустимо совместить на одном хосте для staging).
- Сеть: приватная подсеть, DNS-имя сервиса (внутренний DNS или `/etc/hosts` для лаборатории).
- Firewall: открыть только нужные порты (SSH, 80/443; БД — только с app-хоста).

**Термины**

- **Bare metal** — физический сервер без гипервизора как целевой ОС.
- **VM (Virtual Machine)** — виртуальная машина; типичные гипервизоры: [Proxmox VE](https://www.proxmox.com/), [VMware vSphere](https://www.vmware.com/products/vsphere.html), [KVM](https://www.linux-kvm.org/) / libvirt.
- **Firewall** — фильтрация трафика; на Linux часто [nftables](https://wiki.nftables.org/) / firewalld / ufw.

### 2. Runtime приложения

Выбрать один вариант и обосновать:

| Вариант | Суть |
|--------|------|
| **A. Контейнеры** | Docker Engine / Podman + compose или простой orchestrator |
| **B. Без контейнеров** | пакет/бинарь + [systemd](https://systemd.io/) unit |

**Термины**

- **Docker** — платформа контейнеризации ([docker.com](https://www.docker.com/)); образ = неизменяемый пакет приложения + зависимости.
- **Podman** — daemonless-альтернатива Docker от Red Hat ([podman.io](https://podman.io/)).
- **systemd** — init-система Linux (PID 1): автозапуск, рестарты, логи через journald.
- **Reverse proxy** — фронт, принимающий HTTPS и проксирующий на backend; типично [Nginx](https://nginx.org/) или [Caddy](https://caddyserver.com/).

Обязательно:

- reverse proxy на 443 с TLS;
- backend слушает только localhost / внутренний интерфейс;
- статика отдаётся proxy или отдельным location;
- unit/compose с `Restart=` / restart policy.

### 3. База данных

- PostgreSQL на отдельном томе/диске (данные не на корневом разделе «на удачу»).
- Доступ только с app-хоста (bind address + firewall + роли/пароли).
- Бэкап: `pg_dump` / continuous backup — минимум nightly dump + проверка восстановления на staging.

**Вендор:** [PostgreSQL](https://www.postgresql.org/).

### 4. TLS и доступ

- Сертификат: внутренний CA **или** Let's Encrypt, если есть публичное имя ([Let's Encrypt](https://letsencrypt.org/) / ACME).
- HTTP → HTTPS redirect.
- Базовая hardening: отключить слабые cipher suites, скрыть лишние заголовки server.

### 5. Деплой и версии

Описать и реализовать pipeline (хотя бы скриптами):

1. Сборка артефакта (image tag / package version).
2. Выкладка на staging.
3. Smoke-check (health endpoint, миграции БД).
4. Выкладка на prod.
5. Rollback на предыдущую версию (tag / предыдущий unit + бинарь).

**Термины**

- **CI/CD** — Continuous Integration / Continuous Delivery: автосборка и доставка. Примеры: [GitLab CI](https://docs.gitlab.com/ee/ci/), [Jenkins](https://www.jenkins.io/), [GitHub Actions](https://github.com/features/actions).
- **Artifact / registry** — хранилище образов; on-prem: [Harbor](https://goharbor.io/), GitLab Container Registry, или простой registry.
- **Migration** — изменение схемы БД вместе с релизом (например Alembic, Flyway, golang-migrate).
- **Rollback** — возврат к предыдущей рабочей версии при сбое релиза.
- **Health check** — HTTP `/health` (или аналог), по которому proxy/оркестратор понимает, что сервис жив.

### 6. Наблюдаемость (минимум)

- Логи приложения в journald или файл + ротация ([logrotate](https://github.com/logrotate/logrotate)).
- Метрики или хотя бы: нагрузка CPU/RAM/диск, доступность HTTP (blackbox или простой cron + curl).
- Алерт «сервис недоступен» — даже в Telegram/email скриптом допустим для учебного контура.

Опционально (плюс к оценке): [Prometheus](https://prometheus.io/) + [Grafana](https://grafana.com/), [Loki](https://grafana.com/oss/loki/) / ELK.

### 7. Документация (обязательный deliverable)

В репозитории задачи:

- `README.md` — архитектура (схема хостов/портов), как поднять с нуля, как задеплоить, как откатить.
- `runbook.md` — 5 типовых инцидентов: не стартует unit, 502 от proxy, БД недоступна, диск заполнен, сертификат истёк.
- инвентарь: версии ОС, пакетов, порты, учётки (без секретов в git; секреты — в env/vault-файле вне VCS).

---

## Вне scope

- Kubernetes / полный cloud-native стек (можно упомянуть «как бы мигрировали», но не делать).
- Multi-region, active-active.
- Полноценный SSO/IdP (достаточно одного сервисного пользователя / basic auth на staging).
- Нагрузочное тестирование «на миллион RPS».

---

## Критерии приёмки

- [ ] Staging и prod доступны по HTTPS по согласованному DNS-имени.
- [ ] После `reboot` сервисы поднимаются сами (systemd/docker restart policy).
- [ ] БД недоступна снаружи периметра; приложение ходит в БД по приватному адресу.
- [ ] Есть процедура деплоя новой версии и rollback, проверенная на staging.
- [ ] Есть хотя бы один успешный restore БД из бэкапа на staging.
- [ ] README + runbook покрывают поднятие с нуля и типовые сбои.
- [ ] Секреты не лежат в git.

---

## Ожидаемый результат (артефакты)

1. IaC или воспроизводимые скрипты/ansible (желательно): разметка дисков, пакеты, users, firewall, units.
2. Конфиги Nginx/Caddy + systemd/compose.
3. Скрипт/CI job деплоя и rollback.
4. Скрипт бэкапа PostgreSQL + инструкция restore.
5. Документация выше.

**IaC** — Infrastructure as Code: инфраструктура описана кодом. Примеры: [Ansible](https://www.ansible.com/), [Terraform](https://www.terraform.io/) (для VM/DNS, если гипервизор позволяет API).

---

## Оценка трудозатрат (ориентир)

| Этап | Оценка |
|------|--------|
| Хосты, сеть, firewall, DNS | 0.5–1 дн |
| App + proxy + TLS + systemd/compose | 1–1.5 дн |
| PostgreSQL + бэкап/restore | 0.5–1 дн |
| Деплой/rollback pipeline | 0.5–1 дн |
| Docs + прогон критериев | 0.5 дн |
| **Итого** | **~3.5–5 дн** |

---

## Подсказки по стеку (не обязательно)

- ОС: Ubuntu LTS или RHEL-совместимый (Rocky/Alma).
- Proxy: Nginx.
- App runtime: Docker Compose **или** systemd + venv/bin.
- БД: PostgreSQL 16+.
- Конфиг-менеджмент: Ansible.
- Секреты: `.env` вне git / [SOPS](https://github.com/getsops/sops) / HashiCorp [Vault](https://www.vaultproject.io/) (обзорно).

---

## Definition of Done

Задача закрыта, когда любой другой DevOps из команды по README поднимает контур на чистых VM и по runbook чинит «502 после деплоя» без созвона с автором.

---

## Sample application

Минимальный стенд приложения лежит в [`app/`](./app/): FastAPI + static UI + PostgreSQL + Docker Compose (образы под локальный registry).

```bash
cd app && docker compose up --build -d
# http://localhost:8080 — регистрация → отправка сообщения → «My messages»
```
