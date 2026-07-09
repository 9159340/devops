# 12. cgroups

Подробнее по [краткой лекции](../linux-lectures.md) и [плану изучения](../linux-plan-dim.md).

## Назначение

**cgroups** (control groups) — механизм ядра для **учёта** и **ограничения** ресурсов группы процессов: CPU, память, I/O, число процессов.

Без cgroups один контейнер или runaway-скрипт может занять весь сервер.

## v1 vs v2

| Версия | Особенность |
|--------|-------------|
| **cgroup v1** | Отдельная иерархия на каждый контроллер (`cpu`, `memory`, …) |
| **cgroup v2** | Единая иерархия (**unified**), современный стандарт |

```bash
mount | grep cgroup
# cgroup2 on /sys/fs/cgroup type cgroup2 ...  → v2
stat -fc %T /sys/fs/cgroup/   # cgroup2fs = v2
```

Современные дистрибутивы и Kubernetes ожидают **v2**.

## Иерархия и интерфейс

Корень — `/sys/fs/cgroup/`. Каждый каталог — cgroup; процессы перечислены в `cgroup.procs`.

```bash
cat /sys/fs/cgroup/cgroup.controllers
ls /sys/fs/cgroup/system.slice/
cat /sys/fs/cgroup/system.slice/ssh.service/cgroup.procs
```

Добавить процесс в cgroup (v2):

```bash
echo $$ | sudo tee /sys/fs/cgroup/mygroup/cgroup.procs
```

## Контроллеры

| Контроллер | Ограничивает |
|------------|--------------|
| **cpu** | Долю CPU (`cpu.max`, `cpu.weight`) |
| **memory** | RAM (`memory.max`, `memory.high`) |
| **io** | Дисковый I/O |
| **pids** | Количество процессов |
| **cpuset** | Привязка к конкретным ядрам/NUMA-узлам |

## Ключевые ручки v2

```bash
# Лимит CPU: 50% одного ядра = 50000 из 100000
echo "50000 100000" | sudo tee /sys/fs/cgroup/demo/cpu.max

# Вес CPU (аналог shares)
echo 200 | sudo tee /sys/fs/cgroup/demo/cpu.weight

# Лимит памяти 256 МБ
echo $((256*1024*1024)) | sudo tee /sys/fs/cgroup/demo/memory.max

# Текущее потребление
cat /sys/fs/cgroup/demo/memory.current

# Лимит процессов
echo 50 | sudo tee /sys/fs/cgroup/demo/pids.max
```

**memory.high** — мягкий порог (throttling), **memory.max** — жёсткий (OOM внутри cgroup).

## memory.events и OOM в cgroup

```bash
cat /sys/fs/cgroup/demo/memory.events
# low, high, max, oom, oom_kill ...
```

Если процесс превысил `memory.max`, срабатывает **cgroup OOM** — убивается процесс внутри группы, не обязательно весь хост.

## systemd и cgroups

systemd автоматически помещает сервисы в cgroups:

| Юнит | Назначение |
|------|------------|
| **slice** | Крупные группы (`system.slice`, `user.slice`) |
| **scope** | Процессы вне unit-файла (user session) |
| **service** | Один сервис = одна cgroup |

```bash
systemd-cgls
systemd-cgtop
systemctl show nginx.service -p ControlGroup
```

## Kubernetes

Pod получает cgroup с лимитами из **requests/limits**:

| K8s | cgroup v2 (упрощённо) |
|-----|----------------------|
| CPU request | `cpu.weight` |
| CPU limit | `cpu.max` |
| Memory limit | `memory.max` |

**QoS-классы**:

- **Guaranteed** — requests = limits;
- **Burstable** — limits &gt; requests;
- **BestEffort** — без requests/limits.

Cgroups подов обычно под `kubepods.slice` (или `kubepods/` в v2).

```bash
# На worker-ноде
find /sys/fs/cgroup -name 'cgroup.procs' -path '*kubepods*' 2>/dev/null | head
```

## Практика

Создайте systemd-юнит с `MemoryMax=64M`, запустите `stress-ng --vm 1 --vm-bytes 128M` и поймайте cgroup-OOM в `journalctl`.
