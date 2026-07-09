# 11. Namespaces

Подробнее по [краткой лекции](../linux-lectures.md) и [плану изучения](../linux-plan-dim.md).

## Идея изоляции

**Namespace** (пространство имён) — механизм ядра Linux, при котором группа процессов видит **свою** копию глобального ресурса. Это фундамент **контейнеров**: процесс «думает», что он один на машине.

## Типы namespaces

| Namespace | Изолирует |
|-----------|-----------|
| **pid** | Дерево процессов (PID 1 внутри ≠ systemd на хосте) |
| **net** | Сетевые интерфейсы, маршруты, порты |
| **mnt** | Точки монтирования |
| **uts** | Hostname и domainname |
| **ipc** | IPC: очереди, семафоры, shared memory |
| **user** | UID/GID (root внутри ≠ root снаружи) |
| **cgroup** | Вид корневого cgroup |
| **time** | Системные часы (редко) |

```bash
ls -l /proc/self/ns/
lsns                       # список всех namespaces
lsns -p 1                  # namespaces init/systemd
```

## unshare и nsenter

**unshare** — создать новые namespaces и запустить в них процесс:

```bash
# Новый UTS namespace с другим hostname
sudo unshare -u hostname isolated-host bash
hostname    # isolated-host

# Новый network namespace
sudo ip netns add testns
sudo ip netns exec testns bash
ip link    # только loopback
```

**nsenter** — войти в namespaces существующего процесса (удобно для отладки контейнеров):

```bash
# PID контейнера на хосте
sudo nsenter -t 12345 -n ip addr
sudo nsenter -t 12345 -m ls /
```

## Network namespace вручную

Схема «мини-контейнерной» сети:

```
[netns A: veth0] <---> [veth1 на хосте] <---> [bridge br0] <---> eth0 + NAT
```

```bash
sudo ip netns add ns1
sudo ip link add veth-host type veth peer name veth-ns1
sudo ip link set veth-ns1 netns ns1
sudo ip addr add 10.200.0.1/24 dev veth-host
sudo ip link set veth-host up
sudo ip netns exec ns1 ip addr add 10.200.0.2/24 dev veth-ns1
sudo ip netns exec ns1 ip link set veth-ns1 up
sudo ip netns exec ns1 ip link set lo up
sudo ip netns exec ns1 ip route add default via 10.200.0.1
```

**veth** (virtual ethernet) — пара виртуальных интерфейсов, соединённых «кабелем».

## Mount namespace и propagation

В **mount namespace** свои точки монтирования. **Propagation** определяет, как монтирования распространяются между namespace:

| Режим | Поведение |
|-------|-----------|
| **shared** | Монтирование видно в парных namespace |
| **slave** | Получает, но не отдаёт обратно |
| **private** | Изолировано |
| **unbindable** | Нельзя bind-mount |

```bash
findmnt -o TARGET,PROPAGATION /
```

Docker использует private mount propagation для изоляции.

## User namespace

**User namespace** — маппинг UID/GID: UID 0 внутри может быть 100000 снаружи. Основа **rootless**-контейнеров (Podman, Docker rootless).

```bash
cat /proc/self/uid_map
cat /proc/self/gid_map
```

## Как складывается контейнер

```
namespaces (изоляция) + cgroups (лимиты) + overlayfs (слои ФС) = контейнер
```

| Компонент | Роль |
|-----------|------|
| namespaces | «Не вижу чужие процессы, сеть, ФС» |
| cgroups | «Не могу съесть весь CPU/RAM» |
| overlayfs | «Мой корень — слои образа + writable layer» |

## Практика

Соберите `ip netns` + veth + ping между namespace и хостом. Затем `lsns` для процесса Docker/Podman и сравните с обычным bash.
