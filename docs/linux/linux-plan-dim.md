start

# Linux: список тем для изучения

Дорожная карта от основ к продвинутому. 
К темам добавлены якорные команды и файлы, чтобы было за что зацепиться на практике. 
Пометка *(обзорно)* — достаточно понимать концепцию, без глубокого погружения. 
Разделы 11–13 — фундамент контейнеров и Kubernetes.

---

## 1. Архитектура ОС и загрузка

- [ ] Ядро vs пользовательское пространство; системные вызовы, роль libc
- [ ] Процесс загрузки: BIOS/UEFI → GRUB2 → ядро + initramfs → systemd (PID 1)
- [ ] GRUB: конфигурация, параметры ядра (`/etc/default/grub`, `grub2-mkconfig`, `cat /proc/cmdline`)
- [ ] initramfs: зачем нужен, пересборка (`dracut` в RHEL, `update-initramfs` в Ubuntu)
- [ ] Runlevels → systemd targets: multi-user, graphical, rescue, emergency
- [ ] Семейства дистрибутивов, жизненный цикл релизов (LTS, Stream, EOL)

## 2. Ядро

- [ ] Версии ядра (`uname -r`), обновление, несколько установленных ядер параллельно
- [ ] Модули: загрузка/выгрузка, параметры, автозагрузка, blacklist (`lsmod`, `modprobe`, `modinfo`, `/etc/modprobe.d/`, `/etc/modules-load.d/`)
- [ ] Параметры ядра на лету и персистентно: `sysctl`, `/proc/sys/`, `/etc/sysctl.d/`
- [ ] Сообщения ядра: кольцевой буфер, `dmesg -T`, `journalctl -k`
- [ ] Kernel panic, magic SysRq, kdump *(обзорно)*
- [ ] OOM killer: когда срабатывает, `oom_score`, `oom_score_adj`
- [ ] Виртуальная память в двух словах: страницы, page cache, swap
- [ ] eBPF: что это и почему на нём построены современная observability и сеть *(обзорно)*

## 3. Устройства

- [ ] «Всё — файл»: `/dev`, блочные vs символьные устройства, major/minor номера
- [ ] udev: как появляются устройства, правила, `udevadm info/monitor/trigger`
- [ ] sysfs (`/sys`): устройства, драйверы, классы
- [ ] Инвентаризация железа: `lspci`, `lsusb`, `lsblk`, `lscpu`, `lshw`, `dmidecode`
- [ ] Драйвер = модуль ядра; сопоставление устройства и драйвера (`lspci -k`)
- [ ] Псевдоустройства: `/dev/null`, `/dev/zero`, `/dev/urandom`, loop-устройства (`losetup`)
- [ ] Терминалы: tty vs pts *(обзорно)*

## 4. Файловая система и хранилище

- [ ] FHS: назначение каталогов
- [ ] inode; жёсткие и символические ссылки; atime/mtime/ctime
- [ ] Права rwx, числовая запись, umask; SUID/SGID/sticky
- [ ] Расширенные права: ACL (`getfacl`/`setfacl`), атрибуты `chattr`/`lsattr` (immutable)
- [ ] Типы ФС: ext4, xfs, btrfs; псевдо-ФС: tmpfs, proc, sysfs; **overlayfs** — основа контейнерных образов
- [ ] Разметка: MBR vs GPT, `fdisk`/`gdisk`/`parted`
- [ ] Монтирование: `mount`, `/etc/fstab`, опции (`noatime`, `ro`), bind mounts
- [ ] LVM: PV/VG/LV, расширение томов, снапшоты; thin provisioning *(обзорно)*
- [ ] Программный RAID: `mdadm`, уровни 0/1/5/10 *(обзорно)*
- [ ] Swap: раздел vs файл, `vm.swappiness`
- [ ] Обслуживание: `fsck`, `xfs_repair`; исчерпание inodes (`df -i`)
- [ ] Сетевые ФС: NFS, autofs *(обзорно)*

## 5. Процессы и IPC

- [ ] Жизненный цикл: fork/exec, exit code, wait; зомби и сироты
- [ ] Состояния R/S/D/Z/T; что означает D-state и почему такой процесс не убить
- [ ] Сигналы: основные номера, обработка, чем KILL/STOP отличаются от остальных
- [ ] Приоритеты: nice/renice; планировщик CPU (CFS/EEVDF) *(обзорно)*
- [ ] Потоки vs процессы; как видеть потоки (`ps -eLf`, `/proc/<pid>/task`)
- [ ] Файловые дескрипторы: stdin/stdout/stderr, `/proc/<pid>/fd`, лимит nofile
- [ ] Сессии и группы процессов; демонизация; что делает `nohup`/`setsid`
- [ ] IPC: pipe/FIFO, unix-сокеты, shared memory, семафоры, очереди (`ipcs`)
- [ ] Окружение процесса: env-переменные, `/proc/<pid>/environ`, `/proc/<pid>/cwd`

## 6. systemd

- [ ] Архитектура: PID 1, юниты, дерево зависимостей, параллельный запуск
- [ ] Типы юнитов: service, socket, timer, target, mount/automount, path, slice, scope
- [ ] Анатомия service-юнита: секции [Unit]/[Service]/[Install]; `Type=` simple/exec/forking/oneshot/notify
- [ ] Зависимости и порядок: Requires/Wants vs After/Before; `WantedBy` и механика `enable`
- [ ] Политики перезапуска: `Restart=`, `RestartSec`, `StartLimitBurst/Interval`
- [ ] Переопределения без правки пакетных файлов: drop-in'ы, `systemctl edit`, `daemon-reload`
- [ ] Написать свой юнит с нуля: EnvironmentFile, ExecStartPre, WorkingDirectory
- [ ] journald: фильтры `journalctl -u/-p/--since/-b`, персистентное хранение, лимиты и ротация
- [ ] Таймеры vs cron: `OnCalendar`, `Persistent=`, `systemctl list-timers`
- [ ] Ресурсные лимиты в юнитах: `CPUQuota`, `MemoryMax`, `TasksMax`, `LimitNOFILE` (мост к cgroups)
- [ ] Sandboxing юнитов: `User=`, `ProtectSystem`, `PrivateTmp`, `CapabilityBoundingSet` *(обзорно)*
- [ ] Диагностика загрузки: `systemd-analyze blame`, `critical-chain`
- [ ] Спутники: systemd-resolved, systemd-networkd, logind *(обзорно)*

## 7. Пользователи, доступ, безопасность

- [ ] Пользователи и группы: `/etc/passwd`, `/etc/shadow`, `/etc/group`; UID/GID, системные vs обычные
- [ ] sudo и sudoers (`visudo`, `/etc/sudoers.d/`); su vs sudo
- [ ] PAM: за что отвечает стек аутентификации *(обзорно)*
- [ ] SSH: ключи, `sshd_config` и hardening, agent, ProxyJump
- [ ] Linux capabilities: зачем дробить root (CAP_NET_BIND_SERVICE, CAP_SYS_ADMIN...), `getcap`/`setcap` — критично для контейнеров
- [ ] SELinux (RHEL): режимы, контексты (`ls -Z`), booleans, `restorecon`, разбор audit-логов; AppArmor (Ubuntu)
- [ ] seccomp: фильтрация syscall'ов, роль в контейнерах *(обзорно)*

## 8. Сеть: основы

- [ ] Модель TCP/IP, инкапсуляция; MTU и фрагментация
- [ ] L2: Ethernet, MAC, ARP; VLAN (802.1Q), bridge, bonding
- [ ] L3: адресация и CIDR, таблица маршрутов, default gateway; policy routing (`ip rule`) *(обзорно)*
- [ ] TCP: 3-way handshake, состояния соединения (особенно TIME_WAIT), ретрансмиты; UDP
- [ ] Сокеты: listen backlog, ephemeral-порты
- [ ] NAT и conntrack
- [ ] netfilter: iptables (таблицы и цепочки) и nftables
- [ ] Конфигурация: netplan (Ubuntu), NetworkManager/`nmcli` (RHEL), systemd-networkd
- [ ] Рабочий набор: `ip`, `ss`, `ethtool`, `tcpdump`, `nc`

## 9. DNS

- [ ] Иерархия: root → TLD → авторитативные серверы; делегирование через NS
- [ ] Рекурсивный резолвер vs авторитативный сервер; forwarders
- [ ] Типы записей: A/AAAA, CNAME, NS, SOA, MX, TXT, PTR, SRV
- [ ] TTL, кэширование, негативное кэширование
- [ ] Путь запроса на хосте: `nsswitch.conf` → `/etc/hosts` → `/etc/resolv.conf` → systemd-resolved (stub 127.0.0.53)
- [ ] Отладка: `dig` (`+short`, `+trace`, `@server`), `resolvectl status/query`
- [ ] Обратные зоны (PTR) и где они реально нужны
- [ ] Search-домены и `ndots` — источник классических проблем в Kubernetes
- [ ] Свой резолвер: dnsmasq / unbound / bind *(обзорно)*; DNSSEC, DoT/DoH *(обзорно)*

## 10. DHCP

- [ ] Процесс DORA: Discover → Offer → Request → Ack; почему broadcast
- [ ] Аренда (lease): T1/T2, renew vs rebind, release
- [ ] Опции: 3 (router), 6 (DNS), 51 (lease time), 66/67 (PXE), 43 (vendor-specific)
- [ ] Клиентская сторона: dhclient / NetworkManager / systemd-networkd; где лежат lease-файлы
- [ ] Статические привязки по MAC vs статическая конфигурация интерфейса
- [ ] DHCP relay (ip helper) — зачем в маршрутизируемых сетях
- [ ] Серверы: dnsmasq, ISC dhcpd → Kea *(обзорно)*
- [ ] Отладка: логи клиента/сервера, `tcpdump -i any port 67 or port 68 -nn`
- [ ] IPv6: DHCPv6 vs SLAAC *(обзорно)*

## 11. Namespaces

- [ ] Идея изоляции; типы: pid, net, mnt, uts, ipc, user, cgroup, time
- [ ] Где смотреть: `/proc/<pid>/ns/`, `lsns`
- [ ] Инструменты: `unshare` (создать), `nsenter` (войти — в т.ч. в namespace контейнера)
- [ ] Network namespaces: `ip netns`, veth-пары, связка с bridge — собрать «контейнерную» сеть руками
- [ ] mount namespace и propagation: shared/slave/private
- [ ] user namespace: маппинг UID, rootless-контейнеры
- [ ] Итог: как из namespaces + cgroups + overlayfs складывается контейнер

## 12. cgroups

- [ ] Назначение: учёт и ограничение ресурсов для групп процессов
- [ ] v1 vs v2 (unified hierarchy); как определить версию на хосте (`mount | grep cgroup`)
- [ ] Иерархия `/sys/fs/cgroup`, интерфейсные файлы, перемещение процессов
- [ ] Контроллеры: cpu, memory, io, pids, cpuset
- [ ] Ключевые ручки: `cpu.max`, `cpu.weight`, `memory.max`/`high`/`current`, `pids.max`, `io.max`
- [ ] События и OOM внутри cgroup: `memory.events`
- [ ] systemd поверх cgroups: slices/scopes/services, `systemd-cgls`, `systemd-cgtop`
- [ ] Как это использует Kubernetes: requests/limits → `cpu.weight`/`cpu.max`, QoS-классы, kubepods-слайсы

## 13. Управление ресурсами (resource management)

- [ ] CPU: load average vs утилизация; run queue; привязка к ядрам (`taskset`, cpuset)
- [ ] Память: RSS vs VSZ; page cache и buffers («куда делась память»); `drop_caches`
- [ ] Swap и `vm.swappiness`; overcommit (`vm.overcommit_memory`)
- [ ] OOM: глобальный vs cgroup-OOM; защита процессов через `oom_score_adj`
- [ ] Huge pages / THP *(обзорно)*
- [ ] I/O: планировщики (none / mq-deadline / bfq), `ionice`
- [ ] Лимиты: `ulimit` и `limits.conf` vs systemd `LimitNOFILE`/`TasksMax` — что кого перекрывает
- [ ] PSI (Pressure Stall Information): `/proc/pressure/{cpu,memory,io}` — современная метрика насыщения
- [ ] NUMA: `numactl`, `numastat` *(обзорно)*

## 14. Траблшутинг: методология и утилиты

- [ ] Методология USE (Utilization / Saturation / Errors) и «60-second analysis» Брендана Грегга
- [ ] Первые 60 секунд: `uptime`, `dmesg -T | tail`, `vmstat 1`, `top`/`htop`
- [ ] CPU: `mpstat -P ALL 1`, `pidstat 1`, `perf top` *(обзорно)*
- [ ] Память: `free -h`, `/proc/meminfo`, `pmap -x <pid>`, `smem`
- [ ] Диск и ФС: `iostat -x 1`, `iotop`, `df -h`/`-i`, `du -xsh`, `lsof +D`
- [ ] Сеть: `ss -s`/`-tanp`, `ping`/`mtr`, `tcpdump`, `ethtool -S`, `nstat`, `conntrack -L`
- [ ] Процессы: `strace -f -e trace=%network`, `ltrace`, `lsof -p`, `/proc/<pid>/{status,stack,fd,limits}`
- [ ] «Кто держит файл / порт / точку монтирования»: `lsof`, `fuser -vm`
- [ ] Логи: `journalctl` (`-k`, `-p err`, `--since`), `/var/log/`, logrotate
- [ ] Историческая картина: `sar` (sysstat), `atop` (пишет историю), `dstat`
- [ ] eBPF-инструментарий: bcc-tools (`execsnoop`, `opensnoop`, `biolatency`, `tcplife`), bpftrace
- [ ] Типовые кейсы разобрать руками: df показывает свободно, а места нет (удалённый открытый файл); кончились inodes; процесс в D-state; шторм TIME_WAIT; сработал OOM — найти жертву и причину

## 15. Эксплуатация: пакеты и обслуживание

- [ ] apt/dpkg и dnf/rpm: поиск, установка, откат, фиксация версий (hold / versionlock)
- [ ] Репозитории: sources.list, .repo-файлы, GPG-ключи
- [ ] Автообновления безопасности: unattended-upgrades / dnf-automatic
- [ ] Обновление ядра и планирование перезагрузок; needrestart
- [ ] Время: chrony, `timedatectl`, таймзоны — и почему рассинхрон ломает TLS и кластеры
- [ ] Ротация логов: logrotate, лимиты journald

---

## Как учить

По каждой теме цикл: прочитать → воспроизвести руками на ВМ → сломать → починить. Идеи практики: собрать сеть из network namespace + veth + NAT; написать systemd-юнит с MemoryMax и поймать cgroup-OOM; поднять dnsmasq как DHCP+DNS и посмотреть DORA в tcpdump; отладить «подвисший» процесс через strace/lsof.

Опорные ресурсы: «How Linux Works» (Brian Ward), «Systems Performance» (Brendan Gregg), man7.org, документация Red Hat / Arch Wiki.



end