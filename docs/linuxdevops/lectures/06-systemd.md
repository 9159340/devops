# 6. systemd

Подробнее по [краткой лекции](../linux-lectures.md) и [плану изучения](../linux-plan-dim.md).

## Роль systemd

**systemd** — менеджер инициализации и сервисов, процесс **PID 1**. Заменяет классический SysV init. Управляет:

- параллельным запуском сервисов по зависимостям;
- монтированием ФС;
- логами (**journald**);
- таймерами, сокетами, cgroups.

```bash
systemctl --version
ps -p 1 -o comm=
```

## Типы юнитов

**Юнит (unit)** — объект конфигурации systemd:

| Тип | Суффикс | Назначение |
|-----|---------|------------|
| service | `.service` | Демон или служба |
| socket | `.socket` | Сокет activation |
| timer | `.timer` | Расписание (аналог cron) |
| target | `.target` | Группа юнитов (аналог runlevel) |
| mount | `.mount` | Точка монтирования |
| path | `.path` | Запуск по изменению файла |
| slice | `.slice` | Группа cgroups |
| scope | `.scope` | Внешние процессы (сессии) |

```bash
systemctl list-units --type=service --state=running | head
systemctl list-unit-files --type=service | head
```

## Анатомия service-юнита

Файл обычно в `/etc/systemd/system/` или `/usr/lib/systemd/system/`:

```ini
[Unit]
Description=My App
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/myapp
EnvironmentFile=/etc/myapp/env
ExecStartPre=/opt/myapp/prepare.sh
ExecStart=/opt/myapp/bin/server
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Type=** варианты:

| Type | Когда использовать |
|------|-------------------|
| `simple` | Основной процесс — тот, что запустил ExecStart |
| `forking` | Демон делает fork и родитель завершается |
| `oneshot` | Команда выполняется один раз и завершается |
| `notify` | Процесс сообщает готовность через sd_notify |
| `exec` | Как simple, но считается запущенным после exec |

## Зависимости и enable

- **Requires** — жёсткая зависимость (падение зависимости остановит юнит).
- **Wants** — мягкая (желательно, но не обязательно).
- **After/Before** — только **порядок** запуска, не факт наличия сервиса.

```bash
systemctl status nginx.service
systemctl enable nginx.service    # symlink в multi-user.target.wants
systemctl start nginx.service
systemctl is-enabled nginx
```

`WantedBy=multi-user.target` в `[Install]` + `enable` создаёт симлинк для автозапуска.

## Перезапуск и лимиты старта

```ini
Restart=on-failure
RestartSec=10
StartLimitBurst=3
StartLimitIntervalSec=60
```

Если сервис падает 3 раза за минуту — systemd перестанет его перезапускать.

## Drop-in переопределения

Не редактируйте пакетные файлы в `/usr/lib/` — они перезапишутся при обновлении.

```bash
sudo systemctl edit nginx.service
# откроется редактор для /etc/systemd/system/nginx.service.d/override.conf

sudo systemctl daemon-reload
sudo systemctl restart nginx.service
```

## journald

Централизованные логи:

```bash
journalctl -u nginx.service
journalctl -u nginx -p err --since today
journalctl -b                  # текущая загрузка
journalctl -b -1                 # предыдущая загрузка
journalctl -f                    # follow (как tail -f)
```

Персистентность и ротация — `/etc/systemd/journald.conf` (`Storage=persistent`, `SystemMaxUse=`).

## Таймеры vs cron

```bash
systemctl list-timers --all
```

Пример timer-юнита:

```ini
[Timer]
OnCalendar=daily
Persistent=true
```

`Persistent=true` — если сервер был выключен, задача выполнится при следующем включении.

## Ресурсные лимиты (мост к cgroups)

В секции `[Service]`:

```ini
CPUQuota=50%
MemoryMax=512M
TasksMax=100
LimitNOFILE=65535
```

```bash
systemctl show nginx.service -p MemoryMax -p CPUQuotaPerSecUSec
```

## Sandboxing (обзорно)

Ограничение привилегий сервиса:

```ini
User=nginx
ProtectSystem=strict
PrivateTmp=true
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
```

## Диагностика загрузки

```bash
systemd-analyze
systemd-analyze blame
systemd-analyze critical-chain sshd.service
```

## Спутники (обзорно)

- **systemd-resolved** — локальный DNS-резолвер (stub 127.0.0.53).
- **systemd-networkd** — управление сетью на серверах.
- **logind** — сессии пользователей, lid switch, suspend.

## Практика

Напишите простой юнит для скрипта `while true; do date >> /tmp/heartbeat; sleep 60; done`, включите `Restart=always`, проверьте логи через `journalctl -u`.
