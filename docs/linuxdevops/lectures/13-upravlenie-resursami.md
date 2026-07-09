# 13. Управление ресурсами

Подробнее по [краткой лекции](../linux-lectures.md) и [плану изучения](../linux-plan-dim.md).

## CPU: load average и утилизация

**Load average** — средняя длина очереди задач (running + waiting), показанная в `uptime`.  
Load 4.0 на 4-ядерной машине ≈ полная загрузка; на 16 ядрах — это ~25% capacity.

**Утилизация** — доля времени, когда CPU занят (%user, %system в `mpstat`).

```bash
uptime
mpstat -P ALL 1 3
top -bn1 | head -5
```

**Run queue** — процессы, готовые к выполнению, но ждущие свободное ядро.

Привязка к ядрам:

```bash
taskset -c 0,1 ./cpu-heavy.sh
taskset -pc 0,1 1234              # изменить affinity работающего процесса
```

**cpuset** cgroup — жёстче: процесс не может выйти за указанные CPU.

## Память: RSS, VSZ, page cache

| Метрика | Значение |
|---------|----------|
| **VSZ** (Virtual Size) | Весь виртуальный адресный простор |
| **RSS** (Resident Set Size) | Страницы, реально в RAM |

```bash
ps aux --sort=-%mem | head
free -h
cat /proc/meminfo | head -20
```

**Page cache** и **buffers** — кэш файлов в RAM. Строка «available» в `free -h` — сколько памяти реально доступно приложениям.

```bash
# Сброс кэша (только диагностика, не лечение!)
sudo sync
echo 3 | sudo tee /proc/sys/vm/drop_caches
```

## Swap и overcommit

**Swap** — выгрузка редко используемых страниц на диск.

```bash
swapon --show
sysctl vm.swappiness
```

**vm.overcommit_memory** — политика выделения памяти:

| Значение | Поведение |
|----------|-----------|
| 0 | Эвристика (по умолчанию) |
| 1 | Всегда разрешать overcommit |
| 2 | Строгий лимит |

```bash
sysctl vm.overcommit_memory vm.overcommit_ratio
```

## OOM: глобальный и cgroup

- **Глобальный OOM** — ядро убивает процесс на всём хосте.
- **cgroup OOM** — убивает процесс внутри лимитированной группы.

Защита критичного процесса:

```bash
echo -500 | sudo tee /proc/1234/oom_score_adj
```

## Huge pages (обзорно)

**Huge pages** — страницы 2 МБ / 1 ГБ вместо 4 КБ; меньше нагрузка на **TLB** (Translation Lookaside Buffer).  
**THP** (Transparent Huge Pages) — ядро объединяет страницы автоматически (иногда спорно для БД).

```bash
grep -i huge /proc/meminfo
```

## I/O: планировщики и ionice

Планировщик очереди диска (для каждого устройства):

```bash
cat /sys/block/sda/queue/scheduler
# none mq-deadline bfq
```

- **none** — без reordering (типично NVMe);
- **mq-deadline** — deadline для multi-queue;
- **bfq** — fair queuing, лучше для desktop.

**ionice** — приоритет I/O процесса:

```bash
ionice -c 2 -n 7 ./backup.sh    # idle/low priority
ionice -p 1234
```

## ulimit vs systemd

| Источник | Где |
|----------|-----|
| `ulimit` | Текущая shell-сессия |
| `/etc/security/limits.conf` | PAM при логине |
| systemd `LimitNOFILE=` | Процессы под systemd |

Для сервисов **systemd перекрывает** limits.conf.

```bash
ulimit -a
cat /proc/$$/limits
systemctl show sshd -p LimitNOFILE
```

## PSI — Pressure Stall Information

Современная метрика **насыщения** ресурса: как долго задачи ждут CPU/память/I/O.

```bash
cat /proc/pressure/cpu
cat /proc/pressure/memory
cat /proc/pressure/io
```

Высокое `some`/`full` — признак нехватки ресурса, даже если «средняя утилизация» выглядит нормально.

## NUMA (обзорно)

**NUMA** (Non-Uniform Memory Access) — на многопроцессорных серверах доступ к «чужой» памяти медленнее.

```bash
numactl --hardware
numastat
numactl --cpunodebind=0 --membind=0 ./app
```

## Практика

1. `free -h` и `/proc/meminfo` — объяснить, куда делась память.
2. Сравнить RSS и VSZ у `java` или `chrome` процесса.
3. Прочитать `/proc/pressure/memory` под нагрузкой `stress-ng`.
