# 1. Архитектура ОС и загрузка

Подробнее по [краткой лекции](../linux-lectures.md) и [плану изучения](../linux-plan-dim.md).

## Ядро и пользовательское пространство

**ОС (Operating System)** делит работу на два уровня:

| Уровень | Название | Что делает |
|---------|----------|------------|
| Привилегированный | **kernel space** (пространство ядра) | Управляет CPU, памятью, устройствами, сетью |
| Обычный | **user space** (пользовательское пространство) | Здесь работают ваши программы и демоны |

Программа не пишет напрямую на диск и не выделяет память сама — она обращается к **ядру** через **системные вызовы** (syscalls): `read`, `write`, `fork`, `execve` и сотни других.

**libc** (C library) — стандартная библиотека (чаще всего **glibc** в Debian/RHEL, **musl** в Alpine). Она даёт привычные функции `open()`, `printf()` и внутри вызывает syscalls. Без libc пришлось бы писать ассемблерные инструкции `syscall` вручную.

```bash
# Версия ядра
uname -r

# Какая libc установлена (Debian/Ubuntu)
ldd --version

# Список системных вызовов, которые использует команда
strace -c ls /tmp
```

## Цепочка загрузки

При включении сервера происходит последовательность:

```
BIOS/UEFI → GRUB2 → ядро Linux + initramfs → systemd (PID 1)
```

- **BIOS** (Basic Input/Output System) / **UEFI** (Unified Extensible Firmware Interface) — прошивка материнской платы; ищет загрузчик на диске.
- **GRUB2** (GRand Unified Bootloader) — загрузчик; показывает меню ядер, передаёт управление выбранному ядру.
- **initramfs** (initial RAM filesystem) — временная файловая система в RAM с модулями и скриптами, чтобы смонтировать корневой раздел.
- **systemd** — первый процесс (**PID 1**), запускает остальную систему.

```bash
# Текущие параметры, с которыми загружено ядро
cat /proc/cmdline

# Кто является PID 1
ps -p 1 -o pid,comm,args

# Время загрузки по этапам
systemd-analyze
systemd-analyze blame | head -20
```

## GRUB: настройка

Основной файл — `/etc/default/grub`. После правок конфиг нужно пересобрать:

```bash
# RHEL / Fedora / CentOS
sudo grub2-mkconfig -o /boot/grub2/grub.cfg

# Debian / Ubuntu
sudo update-grub
```

Пример строки в `/etc/default/grub`:

```
GRUB_CMDLINE_LINUX="console=ttyS0,115200n8 quiet"
```

Параметры из этой строки попадают в `/proc/cmdline` и влияют на поведение ядра (консоль, отладка, отключение IPv6 и т.д.).

## initramfs

**initramfs** нужен, когда драйвер диска, **LVM** (Logical Volume Manager) или **RAID** не встроены в само ядро. Без него система не увидит корневой раздел.

```bash
# Список initramfs-образов (Debian/Ubuntu)
ls -lh /boot/initrd* /boot/initramfs*

# Пересборка
sudo update-initramfs -u          # Ubuntu/Debian
sudo dracut -f                    # RHEL/Fedora
```

## Runlevels и systemd targets

Раньше использовались **runlevels** (уровни запуска 0–6). В systemd им соответствуют **targets** (цели):

| Runlevel | Target | Назначение |
|----------|--------|------------|
| 0 | `poweroff.target` | Выключение |
| 1 | `rescue.target` | Однопользовательский режим |
| 3 | `multi-user.target` | Многопользовательский, без GUI |
| 5 | `graphical.target` | С графической оболочкой |
| 6 | `reboot.target` | Перезагрузка |

```bash
# Текущая цель (аналог runlevel)
systemctl get-default

# Переключиться в rescue-режим (осторожно на проде)
sudo systemctl isolate rescue.target

# Вернуться к обычному режиму
sudo systemctl isolate multi-user.target
```

## Дистрибутивы и жизненный цикл

**Дистрибутив** — ядро Linux + набор пакетов + политика обновлений. Основные семейства:

- **Debian/Ubuntu** — `apt`, LTS-релизы Ubuntu (~5 лет поддержки).
- **RHEL/Fedora** — `dnf`/`yum`, RHEL с долгой поддержкой, Fedora — «лаборатория».
- **Arch** — rolling release (постоянные обновления).
- **SUSE** — openSUSE / SLES.

**LTS** (Long Term Support) — релиз с длительной поддержкой патчей безопасности.  
**EOL** (End of Life) — дата, после которой обновления безопасности прекращаются; на EOL-системах работать опасно.

```bash
# Информация о дистрибутиве
cat /etc/os-release

# Версия пакетов (пример Ubuntu)
lsb_release -a
```

## Что попробовать на практике

1. Посмотреть `/proc/cmdline` и сопоставить с `/etc/default/grub`.
2. Запустить `systemd-analyze blame` и найти самый медленный юнит при загрузке.
3. Узнать EOL вашего дистрибутива на сайте вендора.
