# Linux: краткие лекции

Краткий обзор по темам из [плана изучения](linux-plan-dim.md). Каждый раздел помечен тегами `TOPIC_START` / `TOPIC_END` — по ним можно разделить файл на отдельные страницы и дополнить подробностями.


---


Подробные материалы — в [детальных лекциях](index.md#детальные-лекции).

---

<!-- TOPIC_START id="01-architektura-os-zagruzka" title="Архитектура ОС и загрузка" -->

## 1. Архитектура ОС и загрузка

Linux делится на **ядро** (kernel space) и **пользовательское пространство** (user space). Программы не обращаются к железу напрямую — они вызывают **системные вызовы** (syscalls), а библиотека **libc** (glibc, musl) предоставляет удобную обёртку: `open()`, `read()`, `fork()` и т.д.

**Загрузка системы** идёт цепочкой: прошивка (BIOS/UEFI) → загрузчик **GRUB2** → ядро Linux + **initramfs** (временная ФС с драйверами для диска) → **systemd** как процесс PID 1. GRUB настраивается в `/etc/default/grub`, после правок — `grub2-mkconfig` (RHEL) или `update-grub` (Debian/Ubuntu). Текущие параметры ядра: `cat /proc/cmdline`.

**initramfs** нужен, чтобы смонтировать корневую ФС, если драйвер диска или LVM/RAID не встроены в ядро. Пересборка: `dracut` (RHEL) или `update-initramfs -u` (Ubuntu).

Классические **runlevels** (0–6) в systemd заменены **targets**: `multi-user.target`, `graphical.target`, `rescue.target`, `emergency.target`. Переключение: `systemctl isolate rescue.target`.

Дистрибутивы делятся на семейства (Debian/Ubuntu, RHEL/Fedora, Arch, SUSE) с разным жизненным циклом: LTS-релизы (5 лет поддержки), rolling (Arch), Stream (RHEL). Следить за EOL важно для безопасности.

<!-- TOPIC_END id="01-architektura-os-zagruzka" -->

---

<!-- TOPIC_START id="02-yadro" title="Ядро" -->

## 2. Ядро

Версия ядра: `uname -r`. На сервере часто установлено несколько ядер — старое остаётся на случай отката. Обновление ядра требует перезагрузки.

**Модули ядра** — подгружаемые драйверы. `lsmod` — загруженные, `modprobe <имя>` — загрузить, `modinfo` — информация. Автозагрузка: `/etc/modules-load.d/`. Blacklist: `/etc/modprobe.d/`.

**Параметры ядра** меняются на лету через `sysctl` или `/proc/sys/`, персистентно — в `/etc/sysctl.d/*.conf`. Пример: `sysctl -w vm.swappiness=10`.

Сообщения ядра хранятся в **кольцевом буфере**: `dmesg -T` (с метками времени), `journalctl -k` (только kernel). При **kernel panic** система останавливается; **magic SysRq** (Alt+SysRq) — аварийные команды; **kdump** сохраняет дамп памяти для анализа.

**OOM killer** убивает процесс при нехватке памяти. Приоритет жертвы: `oom_score` (чем выше — тем вероятнее убийство), `oom_score_adj` (-1000…1000) позволяет защитить критичный процесс.

**Виртуальная память**: данные разбиты на страницы (обычно 4 КБ). Неиспользуемые страницы уходят в **swap**. **Page cache** — кэш файлов в RAM (отсюда «занятая» память в `free`).

**eBPF** — механизм запуска sandboxed-программ в ядре без модулей. На нём построены современные инструменты observability (bcc, bpftrace) и сетевая фильтрация (Cilium).

<!-- TOPIC_END id="02-yadro" -->

---

<!-- TOPIC_START id="03-ustrojstva" title="Устройства" -->

## 3. Устройства

В Linux **всё — файл**. Устройства живут в `/dev/`: **блочные** (диски — чтение блоками) и **символьные** (терминалы, случайные числа). Идентификация: **major/minor** номера.

**udev** — демон, создающий узлы `/dev` при появлении устройств. Правила в `/etc/udev/rules.d/`. Диагностика: `udevadm info`, `udevadm monitor`, `udevadm trigger`.

**sysfs** (`/sys`) — дерево устройств, драйверов и классов в виде файлов. Дополняет `/proc` (процессы) информацией об оборудовании.

**Инвентаризация**: `lspci` (PCI), `lsusb` (USB), `lsblk` (блочные устройства), `lscpu`, `lshw`, `dmidecode` (DMI/SMBIOS). Драйвер устройства — модуль ядра: `lspci -k` показывает, какой драйвер привязан.

**Псевдоустройства**: `/dev/null` (поглощает данные), `/dev/zero` (нули), `/dev/urandom` (случайные байты), **loop**-устройства (`losetup`) — файл как блочное устройство (образы ISO, контейнеры).

**Терминалы**: **tty** — физические/виртуальные консоли, **pts** — псевдотерминалы (SSH, терминальные эмуляторы).

<!-- TOPIC_END id="03-ustrojstva" -->

---

<!-- TOPIC_START id="04-fajlovaya-sistema" title="Файловая система и хранилище" -->

## 4. Файловая система и хранилище

**FHS** (Filesystem Hierarchy Standard) определяет назначение каталогов: `/bin`, `/etc`, `/var`, `/usr`, `/tmp`, `/home` и т.д.

Каждый файл описывается **inode** (метаданные: права, размер, указатели на блоки). **Жёсткая ссылка** — ещё одно имя того же inode; **символическая** — указатель на путь. Временные метки: atime (доступ), mtime (изменение), ctime (изменение inode).

**Права rwx** для owner/group/others; числовая запись (755 = rwxr-xr-x). **umask** вычитает права при создании. Специальные биты: **SUID** (выполнение от имени владельца), **SGID**, **sticky** (только владелец удаляет в `/tmp`).

**ACL** (`getfacl`/`setfacl`) — права для конкретных пользователей. **Атрибуты** (`chattr`/`lsattr`): `immutable` защищает от изменений даже root.

Типы ФС: **ext4**, **xfs**, **btrfs**. Псевдо-ФС: **tmpfs** (в RAM), **proc**, **sysfs**. **overlayfs** — слои поверх друг друга, основа контейнерных образов.

**Разметка диска**: MBR (устаревает) vs **GPT**. Инструменты: `fdisk`, `gdisk`, `parted`.

**Монтирование**: `mount`, постоянное — `/etc/fstab`. Опции: `noatime`, `ro`. **Bind mount** — один каталог в другом месте.

**LVM**: Physical Volume → Volume Group → Logical Volume. Гибкое расширение, снапшоты. **mdadm** — программный RAID (0/1/5/10).

**Swap**: раздел или файл. Агрессивность: `vm.swappiness`. Обслуживание: `fsck`, `xfs_repair`; следить за inodes: `df -i`.

<!-- TOPIC_END id="04-fajlovaya-sistema" -->

---

<!-- TOPIC_START id="05-processy-ipc" title="Процессы и IPC" -->

## 5. Процессы и IPC

Процесс рождается через **fork** (копия) и **exec** (замена образа программой). **Exit code** — результат завершения (0 = успех). Родитель ждёт через `wait()`. **Зомби** — завершившийся процесс, чей exit code не прочитан. **Сироты** — родитель умер, усыновляет init/systemd.

**Состояния**: R (running), S (sleeping), D (uninterruptible sleep — ждёт I/O, не убивается), Z (zombie), T (stopped). Процесс в **D-state** — признак зависшего диска/NFS.

**Сигналы**: SIGTERM (15) — вежливое завершение, SIGKILL (9) — немедленное (нельзя перехватить), SIGSTOP/SIGCONT — пауза/продолжение. `kill -l` — список.

**Приоритет**: nice (-20…19, меньше = выше). `nice`, `renice`. Планировщик **CFS/EEVDF** распределяет CPU-время.

**Потоки** — легковесные единицы внутри процесса с общей памятью. `ps -eLf`, `/proc/<pid>/task/`.

**Файловые дескрипторы**: 0=stdin, 1=stdout, 2=stderr. `/proc/<pid>/fd/`. Лимит: `ulimit -n` (nofile).

**Сессии и группы**: `setsid`, `nohup` — процесс переживает закрытие терминала.

**IPC**: pipe/FIFO, unix-сокеты, shared memory, семафоры, очереди сообщений (`ipcs`).

Окружение: `env`, `/proc/<pid>/environ`, рабочий каталог: `/proc/<pid>/cwd`.

<!-- TOPIC_END id="05-processy-ipc" -->

---

<!-- TOPIC_START id="06-systemd" title="systemd" -->

## 6. systemd

**systemd** — PID 1, управляет загрузкой и жизненным циклом системы. Основа — **юниты** (unit files) с деревом зависимостей и параллельным запуском.

**Типы юнитов**: service, socket, timer, target, mount, automount, path, slice, scope.

**Service-юнит** имеет секции `[Unit]` (зависимости), `[Service]` (команды, тип), `[Install]` (enable). `Type=simple` — основной процесс, `forking` — демон с fork, `oneshot` — одноразовый, `notify` — sd_notify.

**Зависимости**: `Requires`/`Wants` (что нужно) vs `After`/`Before` (порядок). `WantedBy=multi-user.target` + `systemctl enable` создаёт symlink.

**Перезапуск**: `Restart=on-failure`, `RestartSec=`, `StartLimitBurst/Interval`.

**Drop-in'ы**: `systemctl edit myservice` — переопределение без правки пакетного файла. После изменений: `daemon-reload`.

Свой юнит: `EnvironmentFile=`, `ExecStartPre=`, `WorkingDirectory=`.

**journald**: `journalctl -u unit -p err --since today -b` (текущая загрузка). Персистентность и ротация — `/etc/systemd/journald.conf`.

**Таймеры** — альтернатива cron: `OnCalendar=`, `Persistent=true`, `systemctl list-timers`.

**Ресурсные лимиты** в юните: `CPUQuota=`, `MemoryMax=`, `TasksMax=`, `LimitNOFILE=` — мост к cgroups.

**Sandboxing**: `User=`, `ProtectSystem=strict`, `PrivateTmp=true`, `CapabilityBoundingSet=`.

Диагностика загрузки: `systemd-analyze blame`, `systemd-analyze critical-chain`.

<!-- TOPIC_END id="06-systemd" -->

---

<!-- TOPIC_START id="07-polzovateli-bezopasnost" title="Пользователи, доступ, безопасность" -->

## 7. Пользователи, доступ, безопасность

Учётные записи: `/etc/passwd` (имя, UID, shell), `/etc/shadow` (хеш пароля), `/etc/group`. UID < 1000 — системные, ≥ 1000 — обычные пользователи.

**sudo** — выполнение от root с аудитом. Настройка: `visudo`, файлы в `/etc/sudoers.d/`. `su` — смена пользователя (нужен пароль цели).

**PAM** (Pluggable Authentication Modules) — стек аутентификации: пароль, LDAP, 2FA. Конфиги в `/etc/pam.d/`.

**SSH**: ключи (`ssh-keygen`, `~/.ssh/authorized_keys`), hardening в `sshd_config` (отключить root login, сменить порт), **agent forwarding**, **ProxyJump** для bastion.

**Linux capabilities** — дробление привилегий root: CAP_NET_BIND_SERVICE (порт < 1024), CAP_SYS_ADMIN и др. `getcap`/`setcap` — критично для контейнеров без полного root.

**SELinux** (RHEL): режимы Enforcing/Permissive/Disabled. Контексты (`ls -Z`), booleans (`getsebool`), `restorecon`. **AppArmor** (Ubuntu) — профили для приложений.

**seccomp** — фильтрация syscall'ов. Docker/Kubernetes используют для ограничения контейнеров.

<!-- TOPIC_END id="07-polzovateli-bezopasnost" -->

---

<!-- TOPIC_START id="08-set-osnovy" title="Сеть: основы" -->

## 8. Сеть: основы

**Модель TCP/IP**: приложение → TCP/UDP → IP → Ethernet. **MTU** — максимальный размер кадра (обычно 1500); при превышении — фрагментация.

**L2**: MAC-адреса, **ARP** (IP → MAC). **VLAN** (802.1Q) — логические сети на одном физическом интерфейсе. **Bridge** — коммутатор в software. **Bonding** — агрегация интерфейсов.

**L3**: адресация **CIDR** (10.0.0.0/8), таблица маршрутов (`ip route`), default gateway. **Policy routing**: `ip rule` — маршрутизация по источнику/метке.

**TCP**: трёхстороннее рукопожатие (SYN → SYN-ACK → ACK). Состояния: LISTEN, ESTABLISHED, **TIME_WAIT** (закрывающая сторона ждёт 2×MSL). **UDP** — без установки соединения.

**Сокеты**: listen backlog, ephemeral-порты (обычно 32768–60999).

**NAT** + **conntrack** — отслеживание соединений для трансляции адресов.

**netfilter**: **iptables** (таблицы filter/nat/mangle, цепочки INPUT/OUTPUT/FORWARD) и **nftables** (современная замена).

Конфигурация: **netplan** (Ubuntu), **NetworkManager**/`nmcli` (RHEL desktop), **systemd-networkd**.

Рабочий набор: `ip`, `ss`, `ethtool`, `tcpdump`, `nc`.

<!-- TOPIC_END id="08-set-osnovy" -->

---

<!-- TOPIC_START id="09-dns" title="DNS" -->

## 9. DNS

**Иерархия**: root (.) → TLD (.com, .ru) → авторитативные серверы зоны. Делегирование — NS-записи.

**Рекурсивный резолвер** (8.8.8.8, корпоративный DNS) ищет ответ, обходя иерархию. **Авторитативный сервер** — источник правды для зоны.

**Типы записей**: A/AAAA (адрес), CNAME (алиас), NS, SOA, MX (почта), TXT, PTR (обратный), SRV.

**TTL** — время жизни в кэше. **Негативное кэширование** — запоминание «записи нет».

Путь на хосте: `nsswitch.conf` → `/etc/hosts` → `/etc/resolv.conf` → **systemd-resolved** (stub 127.0.0.53 на Ubuntu).

Отладка: `dig example.com +short`, `dig +trace`, `dig @8.8.8.8`, `resolvectl status`, `resolvectl query`.

**PTR** — обратные зоны (IP → имя), нужны для почты и некоторых сервисов.

**Search-домены** и `ndots` в resolv.conf — частый источник проблем в Kubernetes (лишние DNS-запросы).

Свой резолвер: dnsmasq, unbound, bind. DNSSEC, DoT/DoH — шифрование DNS.

<!-- TOPIC_END id="09-dns" -->

---

<!-- TOPIC_START id="10-dhcp" title="DHCP" -->

## 10. DHCP

**DORA**: Discover (broadcast) → Offer → Request → Ack. Broadcast нужен, потому что клиент ещё не знает свой IP.

**Lease (аренда)**: T1 (renew — тот же сервер), T2 (rebind — любой сервер), release — освобождение.

**Опции**: 3 (router/gateway), 6 (DNS), 51 (lease time), 66/67 (PXE boot), 43 (vendor-specific).

Клиент: **dhclient**, NetworkManager, systemd-networkd. Lease-файлы: `/var/lib/dhcp/`, `/var/lib/NetworkManager/`.

**Статическая привязка по MAC** на сервере vs статический IP на интерфейсе.

**DHCP relay** (ip helper) — пересылка запросов через маршрутизируемые сети, когда сервер в другой подсети.

Серверы: dnsmasq, ISC dhcpd, Kea. Отладка: `tcpdump -i any port 67 or port 68 -nn`.

**IPv6**: DHCPv6 или **SLAAC** (автоконфигурация через router advertisements).

<!-- TOPIC_END id="10-dhcp" -->

---

<!-- TOPIC_START id="11-namespaces" title="Namespaces" -->

## 11. Namespaces

**Namespaces** — изоляция ресурсов для группы процессов. Типы: **pid**, **net**, **mnt**, **uts** (hostname), **ipc**, **user**, **cgroup**, **time**.

Где смотреть: `/proc/<pid>/ns/`, `lsns`.

**unshare** — создать новый namespace. **nsenter** — войти в namespace другого процесса (в т.ч. контейнера).

**Network namespace**: `ip netns add`, veth-пара (один конец в namespace, другой в bridge) — собрать «контейнерную» сеть вручную.

**Mount namespace** + propagation (shared/slave/private) — как монтирования видны между namespace.

**User namespace** — маппинг UID (root в namespace ≠ root на хосте). Основа **rootless**-контейнеров.

**Итог**: namespaces (изоляция) + cgroups (лимиты) + overlayfs (ФС) = контейнер.

<!-- TOPIC_END id="11-namespaces" -->

---

<!-- TOPIC_START id="12-cgroups" title="cgroups" -->

## 12. cgroups

**cgroups** (control groups) — учёт и ограничение ресурсов для групп процессов.

**v1** — отдельные иерархии на контроллер. **v2** — единая иерархия (unified). Проверка: `mount | grep cgroup`.

Интерфейс: `/sys/fs/cgroup/`. Процесс попадает в cgroup через запись PID в `cgroup.procs`.

**Контроллеры**: cpu, memory, io, pids, cpuset.

Ключевые ручки v2: `cpu.max`, `cpu.weight`, `memory.max`/`memory.high`/`memory.current`, `pids.max`, `io.max`.

**memory.events** — счётчики (в т.ч. oom_kill внутри cgroup).

**systemd** управляет cgroups: slices (system.slice, user.slice), scopes, services. `systemd-cgls`, `systemd-cgtop`.

**Kubernetes**: requests/limits → `cpu.weight`/`cpu.max`, QoS-классы (Guaranteed/Burstable/BestEffort), kubepods-слайсы.

<!-- TOPIC_END id="12-cgroups" -->

---

<!-- TOPIC_START id="13-upravlenie-resursami" title="Управление ресурсами" -->

## 13. Управление ресурсами

**CPU**: load average — средняя длина очереди (не = утилизация). **Run queue** — процессы, ждущие CPU. Привязка к ядрам: `taskset`, **cpuset** cgroup.

**Память**: **RSS** (реально в RAM) vs **VSZ** (виртуальный размер). **Page cache** и buffers — «куда делась память» в `free`. `drop_caches` — сброс кэша (диагностика, не решение).

**Swap** + `vm.swappiness`. **Overcommit**: `vm.overcommit_memory`.

**OOM**: глобальный (ядро) vs cgroup-OOM. Защита: `oom_score_adj`.

**Huge pages / THP** — крупные страницы для снижения TLB-miss.

**I/O**: планировщики (none, mq-deadline, bfq). `ionice` — приоритет I/O.

**Лимиты**: `ulimit` / `/etc/security/limits.conf` vs systemd `LimitNOFILE`/`TasksMax` — systemd перекрывает для управляемых процессов.

**PSI** (Pressure Stall Information): `/proc/pressure/{cpu,memory,io}` — метрика насыщения ресурса.

**NUMA**: неоднородный доступ к памяти. `numactl`, `numastat`.

<!-- TOPIC_END id="13-upravlenie-resursami" -->

---

<!-- TOPIC_START id="14-trablshuting" title="Траблшутинг" -->

## 14. Траблшутинг: методология и утилиты

**Методология USE** (Brendan Gregg): для каждого ресурса — Utilization (занятость), Saturation (очередь), Errors (ошибки).

**Первые 60 секунд**: `uptime`, `dmesg -T | tail`, `vmstat 1`, `top`/`htop`.

**CPU**: `mpstat -P ALL 1`, `pidstat 1`, `perf top`.

**Память**: `free -h`, `/proc/meminfo`, `pmap -x <pid>`, `smem`.

**Диск**: `iostat -x 1`, `iotop`, `df -h`/`-i`, `du -xsh`, `lsof +D /path`.

**Сеть**: `ss -s`/`-tanp`, `ping`/`mtr`, `tcpdump`, `ethtool -S`, `nstat`, `conntrack -L`.

**Процессы**: `strace -f -e trace=network`, `lsof -p`, `/proc/<pid>/{status,stack,fd,limits}`.

**Кто держит**: `lsof`, `fuser -vm`.

**Логи**: `journalctl -k -p err --since "1 hour ago"`, `/var/log/`, logrotate.

**История**: `sar` (sysstat), `atop`, `dstat`.

**eBPF**: bcc-tools (`execsnoop`, `opensnoop`, `biolatency`, `tcplife`), bpftrace.

**Типовые кейсы**: df показывает место, а записать нельзя (удалённый открытый файл — `lsof | grep deleted`); кончились inodes; процесс в D-state; шторм TIME_WAIT; OOM — найти жертву в `dmesg`/`journalctl`.

<!-- TOPIC_END id="14-trablshuting" -->

---

<!-- TOPIC_START id="15-ekspluataciya" title="Эксплуатация: пакеты и обслуживание" -->

## 15. Эксплуатация: пакеты и обслуживание

**apt/dpkg** (Debian/Ubuntu) и **dnf/rpm** (RHEL/Fedora): поиск, установка, удаление, откат. Фиксация версий: `apt-mark hold` / `dnf versionlock`.

**Репозитории**: `/etc/apt/sources.list`, `/etc/yum.repos.d/*.repo`, GPG-ключи.

**Автообновления**: unattended-upgrades (Debian), dnf-automatic (RHEL).

Обновление ядра → планирование перезагрузки. **needrestart** — какие сервисы требуют рестарта.

**Время**: **chrony** (NTP), `timedatectl`, таймзоны. Рассинхрон ломает TLS-сертификаты и кластеры (etcd, Kafka).

**Ротация логов**: logrotate (`/etc/logrotate.d/`), лимиты journald (`SystemMaxUse=`).

<!-- TOPIC_END id="15-ekspluataciya" -->
