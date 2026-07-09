# 4. Файловая система и хранилище

Подробнее по [краткой лекции](../linux-lectures.md) и [плану изучения](../linux-plan-dim.md).

## FHS — иерархия каталогов

**FHS** (Filesystem Hierarchy Standard) описывает назначение основных каталогов:

| Каталог | Назначение |
|---------|------------|
| `/` | Корень всей иерархии |
| `/bin`, `/sbin` | Базовые команды (часто симлинк на `/usr`) |
| `/etc` | Конфигурация |
| `/home` | Домашние каталоги пользователей |
| `/var` | Изменяемые данные: логи, кэш, spool |
| `/tmp` | Временные файлы |
| `/usr` | Программы и библиотеки |
| `/dev` | Устройства |
| `/proc`, `/sys` | Виртуальные ФС ядра |

## inode и ссылки

**inode** (index node) — структура с метаданными файла: права, владелец, размер, указатели на блоки данных. Имя файла хранится в каталоге, а не в inode.

```bash
ls -li /etc/passwd        # номер inode слева
stat /etc/passwd          # atime, mtime, ctime, inode
df -i                     # свободные inodes (важно на мелких ФС!)
```

- **Жёсткая ссылка** — второе имя того же inode (`ln file hardlink`).
- **Символическая ссылка** — отдельный файл-указатель на путь (`ln -s target symlink`).

Временные метки:

- **atime** — последний доступ;
- **mtime** — изменение содержимого;
- **ctime** — изменение метаданных inode.

## Права доступа

Формат `rwx` для трёх категорий: **owner** (владелец), **group** (группа), **others** (остальные).

```bash
chmod 755 script.sh       # rwxr-xr-x
chmod u+x script.sh       # добавить execute владельцу
umask                     # маска вычитания при создании файлов (обычно 0022)
```

Специальные биты:

| Бит | Эффект |
|-----|--------|
| **SUID** (4) | Программа выполняется от UID владельца файла (`chmod u+s`) |
| **SGID** (2) | Выполнение от GID группы; в каталоге — новые файлы наследуют группу |
| **sticky** (1) | В каталоге (например `/tmp`) удалить файл может только владелец |

```bash
ls -l /usr/bin/passwd     # часто -rwsr-xr-x (SUID)
ls -ld /tmp               # drwxrwxrwt (sticky)
```

## ACL и атрибуты

**ACL** (Access Control List) — права для конкретных пользователей/групп поверх классических rwx.

```bash
getfacl /shared/data
setfacl -m u:alice:rwx /shared/data
setfacl -m g:developers:rx /shared/data
```

**Атрибуты** ext4/xfs через `chattr`/`lsattr`:

```bash
sudo chattr +i /etc/resolv.conf   # immutable — нельзя менять даже root
lsattr /etc/resolv.conf
sudo chattr -i /etc/resolv.conf   # снять
```

## Типы файловых систем

| ФС | Особенности |
|----|-------------|
| **ext4** | Классика Linux, журналирование |
| **xfs** | Хороша на больших томах, RHEL по умолчанию |
| **btrfs** | Снапшоты, сжатие, подтома |
| **tmpfs** | В RAM (`/dev/shm`, `/run`) |
| **proc**, **sysfs** | Виртуальные |
| **overlayfs** | Слои поверх друг друга — основа Docker-образов |

```bash
findmnt                   # что смонтировано
df -hT                    # тип ФС и занятость
```

## Разметка диска

- **MBR** (Master Boot Record) — устаревающая схема, максимум 2 ТБ на раздел.
- **GPT** (GUID Partition Table) — современный стандарт, нужен для UEFI.

```bash
sudo fdisk -l             # или lsblk
sudo parted /dev/sdb print
```

## Монтирование

```bash
# Временно
sudo mount /dev/sdb1 /mnt/data
sudo mount -o ro,noatime /dev/sdb1 /mnt/data

# Постоянно — /etc/fstab
# <устройство>  <точка>  <тип>  <опции>  <dump>  <fsck>
# UUID=...        /data    xfs    defaults 0       0

sudo mount -a             # применить fstab (проверка синтаксиса)

# Bind mount — тот же каталог в другом месте
sudo mount --bind /var/log /mnt/logs
```

Опции: `ro` (только чтение), `noatime` (не обновлять atime — меньше записей на диск).

## LVM (обзор основ)

**LVM** (Logical Volume Manager) — гибкое управление томами:

```
PV (Physical Volume) → VG (Volume Group) → LV (Logical Volume)
```

```bash
sudo pvs && sudo vgs && sudo lvs
sudo lvextend -L +10G /dev/mapper/vg0-data
sudo xfs_growfs /data     # расширить ФС (xfs)
# или resize2fs для ext4
```

## RAID и swap (кратко)

**mdadm** — программный **RAID** (Redundant Array of Independent Disks): уровни 0 (striping), 1 (mirror), 5, 10.

**Swap** — раздел или файл подкачки:

```bash
swapon --show
free -h
sysctl vm.swappiness
```

## Обслуживание

```bash
sudo fsck /dev/sdb1       # проверка (раздел должен быть unmounted)
sudo xfs_repair /dev/...  # для xfs при проблемах
df -h && df -i            # место и inodes
du -xsh /var/*            # размер каталогов
```

## Типичная проблема

`df` показывает свободное место, но записать нельзя — проверьте `df -i` (закончились inodes) или удалённый, но ещё открытый файл (`lsof | grep deleted`).
