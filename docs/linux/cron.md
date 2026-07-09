
# Посмотреть, что делает крон

~$ grep cron /var/log/syslog | tail


# Cron на Windows (WSL) — автозапуск git-upd

Настроен cron в WSL Ubuntu для запуска `git-upd.cmd` каждые 5 минут.

Репо Git: c:\Z_PROJECTS2026\devops\
Там создан CMD-файл git-upd.cmd с командой
    git add . && git commit -m "upd" && git push

Автозапуск каждые 5 минут будет обеспечивать Cron.

### Что сделано

- **Wrapper** — `cron/run-git-upd.sh` запускает `git-upd.cmd` и пишет лог
- **Crontab** — `*/5 * * * * /mnt/c/work/projects2026/devops/cron/run-git-upd.sh`
- **Логи скрипта** — `~/logs/git-upd.log` в WSL
- **`.gitattributes`** — `cron/*.sh` с LF, чтобы WSL не ломался на CRLF

### Задача планировщика Windows

Создана задача **WSL Cron Start** (триггер: вход в систему):

```
wsl.exe -d Ubuntu -u root service cron start
```

Запуск от администратора (если ещё не создана):

```powershell
schtasks /create /tn "WSL Cron Start" /sc onlogon /tr "wsl.exe -d Ubuntu -u root service cron start" /f
```

**Важно:** задача срабатывает при **логине**, а не при загрузке Windows. Пока не вошёл в систему — WSL и cron не работают. В `/etc/wsl.conf` включён `systemd=true`, cron обычно поднимается сам при старте WSL.

### Логи

```bash
# результат git-upd (удобнее всего)
wsl tail -f ~/logs/git-upd.log

# запуски cron-задач в syslog
wsl grep 'CRON.*CMD' /var/log/syslog | tail -20

# только наша задача
wsl grep 'run-git-upd' /var/log/syslog

# статус и crontab
wsl service cron status
wsl crontab -l
```

В syslog два типа записей:

- **Старт демона** — `(CRON) INFO (pidfile fd = 3)` — появляется при каждом перезапуске WSL
- **Запуск задачи** — `CRON[n]: (nikolai) CMD (/mnt/c/.../run-git-upd.sh)`

### Нюансы

- Пока WSL выключен (простой), тики cron пропускаются
- `git-upd.cmd` коммитит всегда; если изменений нет — в лог попадёт ошибка `nothing to commit`
- `/mnt/c` смонтирован `rw` без `noexec` — скрипты с диска C: запускаются нормально


end