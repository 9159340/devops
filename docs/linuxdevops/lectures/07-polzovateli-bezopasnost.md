# 7. Пользователи, доступ, безопасность

Подробнее по [краткой лекции](../linux-lectures.md) и [плану изучения](../linux-plan-dim.md).

## Учётные записи

| Файл | Содержимое |
|------|------------|
| `/etc/passwd` | Имя, UID, GID, домашний каталог, shell (пароль здесь не хранится) |
| `/etc/shadow` | Хеш пароля (только root) |
| `/etc/group` | Группы и их члены |

**UID** (User ID) / **GID** (Group ID) — числовые идентификаторы.

- UID &lt; 1000 (или 999) — системные учётки (`root`=0, `nginx`, `sshd`).
- UID ≥ 1000 — обычные пользователи.

```bash
id
id alice
getent passwd alice
getent group docker
```

```bash
# Создание пользователя
sudo useradd -m -s /bin/bash alice
sudo passwd alice
sudo usermod -aG docker alice    # добавить в группу
```

## sudo и su

**sudo** (superuser do) — выполнить команду от другого пользователя (обычно root) с записью в аудит.

**su** (switch user) — сменить пользователя; нужен пароль целевого пользователя.

```bash
sudo whoami
sudo -u postgres psql
su - alice                # login shell целевого пользователя
```

Настройка sudo — только через `visudo` (проверяет синтаксис):

```bash
sudo visudo
# или отдельные файлы:
sudo visudo -f /etc/sudoers.d/alice
```

Пример правила:

```
alice ALL=(ALL) NOPASSWD: /bin/systemctl restart nginx
```

## PAM (обзорно)

**PAM** (Pluggable Authentication Modules) — стек проверки аутентификации: пароль, LDAP, 2FA, политики смены пароля. Конфиги в `/etc/pam.d/` (отдельный файл на сервис: `login`, `sshd`, `sudo`).

Для DevOps достаточно знать: если «не пускает» при правильном пароле — смотреть `/etc/pam.d/` и логи.

## SSH

**SSH** (Secure Shell) — удалённый защищённый доступ.

```bash
# Генерация ключа
ssh-keygen -t ed25519 -C "alice@laptop"

# Копирование на сервер
ssh-copy-id alice@server.example.com

# Подключение
ssh alice@server.example.com
```

Файлы:

- `~/.ssh/id_ed25519` — приватный ключ (права 600);
- `~/.ssh/authorized_keys` на сервере — разрешённые публичные ключи.

Hardening в `/etc/ssh/sshd_config`:

```
PermitRootLogin no
PasswordAuthentication no
Port 2222
```

```bash
sudo sshd -t               # проверка конфига
sudo systemctl reload sshd
```

**ProxyJump** — подключение через бастион:

```bash
ssh -J bastion.example.com target.internal
```

**SSH agent** — хранит расшифрованный ключ в памяти сессии (`ssh-add -l`).

## Linux capabilities

Вместо полного **root** процессу можно выдать отдельные **capabilities** (возможности):

| Capability | Зачем |
|------------|-------|
| CAP_NET_BIND_SERVICE | Слушать порт &lt; 1024 без root |
| CAP_SYS_ADMIN | Администрирование (опасно) |
| CAP_NET_RAW | raw-сокеты (ping без root) |

```bash
getcap /usr/bin/ping
sudo setcap cap_net_bind_service=+ep /opt/myapp/server
```

Критично для контейнеров: Docker по умолчанию отбрасывает большинство capabilities.

## SELinux и AppArmor

**SELinux** (Security-Enhanced Linux) — на RHEL/CentOS/Fedora. Режимы:

- **Enforcing** — блокирует нарушения;
- **Permissive** — только логирует;
- **Disabled** — выключен.

```bash
getenforce
sestatus
ls -Z /var/www/html/       # контекст безопасности
sudo restorecon -Rv /var/www/html/
getsebool -a | grep httpd
```

**AppArmor** — профили для приложений на Ubuntu/Debian (`aa-status`).

## seccomp (обзорно)

**seccomp** (secure computing mode) — фильтр **syscall'ов**: процессу разрешён только белый список системных вызовов. Docker и Kubernetes используют для уменьшения поверхности атаки контейнера.

## Практика

1. Создать пользователя, выдать sudo только на один systemctl restart.
2. Настроить вход по ключу, отключить PasswordAuthentication.
3. `getcap` на `/usr/bin/ping` — увидеть CAP_NET_RAW.
