# 15. Эксплуатация: пакеты и обслуживание

Подробнее по [краткой лекции](../linux-lectures.md) и [плану изучения](../linux-plan-dim.md).

## Менеджеры пакетов

### Debian / Ubuntu: apt и dpkg

**dpkg** — низкоуровневая работа с `.deb`.  
**apt** — удобный фронтенд с зависимостями и репозиториями.

```bash
apt search nginx
apt show nginx
sudo apt update
sudo apt install nginx
sudo apt remove nginx
sudo apt purge nginx          # + конфиги

dpkg -l | grep nginx
dpkg -L nginx                 # файлы пакета
```

Откат (если старая версия в кэше):

```bash
apt-cache policy nginx
sudo apt install nginx=1.18.0-6ubuntu14
```

Фиксация версии:

```bash
sudo apt-mark hold nginx
apt-mark showhold
sudo apt-mark unhold nginx
```

### RHEL / Fedora: dnf и rpm

**rpm** — формат `.rpm`. **dnf** — менеджер зависимостей (замена yum).

```bash
dnf search nginx
dnf info nginx
sudo dnf install nginx
sudo dnf remove nginx

rpm -qa | grep nginx
rpm -ql nginx
```

Фиксация версии (**versionlock**):

```bash
sudo dnf install python3-dnf-plugin-versionlock
sudo dnf versionlock add nginx-*
dnf versionlock list
```

## Репозитории

| Дистрибутив | Конфигурация |
|-------------|--------------|
| Debian/Ubuntu | `/etc/apt/sources.list`, `/etc/apt/sources.list.d/` |
| RHEL/Fedora | `/etc/yum.repos.d/*.repo` |

```bash
# Ubuntu
cat /etc/apt/sources.list.d/*.list

# RHEL
dnf repolist
cat /etc/yum.repos.d/epel.repo
```

**GPG-ключи** проверяют подлинность пакетов:

```bash
apt-key list                  # устаревающий интерфейс
ls /etc/apt/trusted.gpg.d/
rpm -qa gpg-pubkey*
```

## Автообновления безопасности

| Дистрибутив | Инструмент |
|-------------|------------|
| Debian/Ubuntu | `unattended-upgrades` |
| RHEL | `dnf-automatic` |

```bash
# Ubuntu
cat /etc/apt/apt.conf.d/50unattended-upgrades | head -30
systemctl status unattended-upgrades
```

На продакшене автообновления ядра планируют с окном перезагрузки.

## Обновление ядра и needrestart

После обновления библиотек запущенные процессы могут использовать старые версии в памяти.

```bash
sudo apt upgrade
sudo needrestart -r l         # что требует рестарта (Debian)
# или проверка вручную
uname -r
rpm -q kernel --last
```

Перезагрузка после нового ядра обязательна.

## Время: chrony и timedatectl

**NTP** (Network Time Protocol) синхронизирует часы. Рассинхрон ломает:

- TLS-сертификаты (кажется «ещё не действителен»);
- распределённые системы (etcd, Kafka, кластеры БД).

```bash
timedatectl status
timedatectl list-timezones
sudo timedatectl set-timezone Europe/Moscow

systemctl status chronyd       # RHEL
systemctl status systemd-timesyncd   # Ubuntu
chronyc tracking
```

**chrony** — популярный NTP-клиент/сервер; быстрее подстраивается после дрейфа, чем классический ntpd.

## Ротация логов

### logrotate

Конфиги в `/etc/logrotate.d/`:

```bash
cat /etc/logrotate.d/nginx
sudo logrotate -d /etc/logrotate.conf   # dry-run
```

Типичные директивы: `daily`, `rotate 14`, `compress`, `postrotate`.

### journald

```bash
cat /etc/systemd/journald.conf | grep -E '^[^#]'
# SystemMaxUse=500M
# MaxRetentionSec=1month
```

```bash
journalctl --disk-usage
sudo journalctl --vacuum-size=500M
```

## Практика

1. Установить пакет, найти его файлы через `dpkg -L` / `rpm -ql`.
2. `timedatectl` и `chronyc sources` — убедиться в синхронизации.
3. `journalctl --disk-usage` — оценить размер логов.
