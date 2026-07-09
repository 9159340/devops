# 14. Траблшутинг: методология и утилиты

Подробнее по [краткой лекции](../linux-lectures.md) и [плану изучения](../linux-plan-dim.md).

## Методология USE

**USE** (Brendan Gregg) — для каждого ресурса задайте три вопроса:

| Буква | Вопрос |
|-------|--------|
| **U**tilization | Насколько занят ресурс? |
| **S**aturation | Есть ли очередь ожидания? |
| **E**rrors | Есть ли ошибки? |

Ресурсы: CPU, память, диск, сеть, шина.

## Первые 60 секунд

Чеклист «быстрого осмотра»:

```bash
uptime
dmesg -T | tail -30
vmstat 1 5
top -bn1 | head -20
# или htop — интерактивно
```

`vmstat` — сводка: r (run queue), b (blocked), swap in/out, bi/bo (disk I/O).

## CPU

```bash
mpstat -P ALL 1 3
pidstat 1 5
pidstat -u 1              # по процессам
sudo perf top             # обзорно: горячие функции ядра/приложений
```

## Память

```bash
free -h
cat /proc/meminfo
pmap -x $(pgrep nginx | head -1) | tail -1
smem -rkt                 # если установлен smem
```

## Диск и ФС

```bash
iostat -x 1 3
sudo iotop -o             # кто пишет на диск
df -h
df -i
du -xsh /var/* | sort -h | tail
sudo lsof +D /var/log
```

Колонки `iostat -x`: **await** (среднее время I/O), **%util** (занятость устройства).

## Сеть

```bash
ss -s
ss -tanp | head
ping -c 5 8.8.8.8
mtr -rwzbc 100 8.8.8.8
sudo tcpdump -i eth0 -nn -c 20
ethtool -S eth0 | grep -i error
nstat -az | head
sudo conntrack -L 2>/dev/null | wc -l
```

## Процессы: strace и /proc

```bash
sudo strace -f -p 1234 -e trace=network
sudo strace -f -e trace=file ./myapp 2>&1 | head

cat /proc/1234/status
cat /proc/1234/limits
ls -l /proc/1234/fd/
sudo cat /proc/1234/stack
```

## Кто держит файл, порт, mount

```bash
sudo lsof /var/log/app.log
sudo lsof -i :8080
sudo fuser -vm /mnt/data
```

## Логи

```bash
journalctl -k -p err --since "1 hour ago"
journalctl -u nginx -p warning --since today
ls -la /var/log/
```

**logrotate** — ротация файлов в `/etc/logrotate.d/`.

## Исторические данные

```bash
sar -u 1 3                # CPU (пакет sysstat)
sar -r 1 3                # память
atop                        # интерактивный, пишет историю
dstat -cdngy 1 5
```

## eBPF-инструменты

**bcc-tools** (обзорно):

```bash
sudo execsnoop              # новые процессы
sudo opensnoop              # открытия файлов
sudo biolatency             # латентность диска
sudo tcplife                # жизненный цикл TCP-соединений
```

**bpftrace** — скриптовый язык для eBPF.

## Типовые кейсы

### df показывает место, записать нельзя

Часто — удалённый файл, но процесс держит дескриптор открытым:

```bash
sudo lsof | grep deleted
# перезапустить процесс или truncate через /proc/<pid>/fd/<n>
```

### Кончились inodes

```bash
df -i
find /var -xdev -type f | wc -l   # много мелких файлов?
```

### Процесс в D-state

Ждёт I/O (диск, NFS). `kill -9` не поможет — чинить хранилище/сеть.

```bash
ps aux | awk '$8 ~ /D/'
dmesg -T | tail
```

### Шторм TIME_WAIT

```bash
ss -tan state time-wait | wc -l
sysctl net.ipv4.ip_local_port_range
```

### OOM — найти жертву

```bash
dmesg -T | grep -i 'killed process'
journalctl -k | grep -i oom
```

## Практика

Разберите один реальный инцидент по USE: для CPU — `mpstat`, для диска — `iostat`, для сети — `ss` + `tcpdump`.
