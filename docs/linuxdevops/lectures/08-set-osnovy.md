# 8. Сеть: основы

Подробнее по [краткой лекции](../linux-lectures.md) и [плану изучения](../linux-plan-dim.md).

## Модель TCP/IP

Данные проходят слои (инкапсуляция):

```
Приложение → TCP/UDP (L4) → IP (L3) → Ethernet (L2) → физика (L1)
```

**MTU** (Maximum Transmission Unit) — максимальный размер кадра L2, обычно **1500** байт. Если пакет больше — **фрагментация** на уровне IP (нежелательна для UDP и производительности).

```bash
ip link show eth0 | grep mtu
ping -M do -s 1472 8.8.8.8    # проверка MTU (1472 + 28 заголовков ≈ 1500)
```

## Уровень L2: Ethernet

- **MAC** (Media Access Control) — аппаратный адрес интерфейса (48 бит).
- **ARP** (Address Resolution Protocol) — узнать MAC по IP в локальной сети.

```bash
ip link show
ip neigh show                 # ARP-таблица
arp -n
```

**VLAN** (Virtual LAN, 802.1Q) — логические сети поверх одного физического порта.

**Bridge** — программный коммутатор (используется в Docker, KVM).

**Bonding** — объединение нескольких NIC в один (отказоустойчивость/агрегация).

```bash
bridge link show
cat /proc/net/bonding/bond0 2>/dev/null
```

## Уровень L3: IP и маршрутизация

**CIDR** (Classless Inter-Domain Routing) — запись сети: `10.0.0.0/8` означает маску /8.

```bash
ip addr show
ip -4 addr show dev eth0
ip route show
ip route get 8.8.8.8          # какой маршрут выберется
```

**Default gateway** — маршрут по умолчанию для трафика вне локальных сетей.

**Policy routing** (обзорно) — маршрутизация по источнику, метке, таблице:

```bash
ip rule list
ip route show table all
```

## TCP и UDP

**TCP** (Transmission Control Protocol) — с установкой соединения, гарантия доставки.

Трёхстороннее рукопожатие: **SYN** → **SYN-ACK** → **ACK**.

**UDP** (User Datagram Protocol) — без соединения, без гарантий (DNS, VoIP, QUIC поверх UDP).

Состояния TCP (важные):

| Состояние | Значение |
|-----------|----------|
| LISTEN | Сервер ждёт подключений |
| ESTABLISHED | Соединение активно |
| TIME_WAIT | Сторона, закрывшая соединение, ждёт 2×MSL (~60 с) |

Много **TIME_WAIT** — нормально при частых коротких соединениях, но может исчерпать ephemeral-порты.

```bash
ss -tan state time-wait | wc -l
ss -tan state established
```

**Ephemeral ports** — временные порты клиента (диапазон в `/proc/sys/net/ipv4/ip_local_port_range`).

## NAT и conntrack

**NAT** (Network Address Translation) — подмена IP/порта (типично SNAT/DNAT в Kubernetes и домашних роутерах).

**conntrack** (connection tracking) — ядро отслеживает состояние соединений для NAT и firewall.

```bash
cat /proc/sys/net/netfilter/nf_conntrack_count
sudo conntrack -L 2>/dev/null | head
```

## netfilter: iptables и nftables

**netfilter** — подсистема ядра для фильтрации и NAT.

**iptables** — классический интерфейс. Таблицы: `filter`, `nat`, `mangle`. Цепочки: `INPUT`, `OUTPUT`, `FORWARD`.

```bash
sudo iptables -L -n -v
sudo iptables -t nat -L -n -v
```

**nftables** — современная замена с единым синтаксисом:

```bash
sudo nft list ruleset
```

## Конфигурация сети

| Инструмент | Где |
|------------|-----|
| **netplan** | Ubuntu Server |
| **NetworkManager** / `nmcli` | Desktop, RHEL |
| **systemd-networkd** | Минимальные образы, контейнеры |

```bash
# NetworkManager
nmcli device status
nmcli connection show

# netplan (Ubuntu)
sudo netplan apply
cat /etc/netplan/*.yaml
```

## Рабочий набор команд

```bash
# ip — замена ifconfig/route
ip addr
ip link set eth0 up
ip route add 10.20.0.0/16 via 10.0.0.1

# ss — замена netstat
ss -tlnp                     # слушающие TCP-порты
ss -tanp | grep :443

# ethtool — параметры NIC
ethtool eth0
ethtool -S eth0               # счётчики

# tcpdump — захват пакетов
sudo tcpdump -i eth0 port 443 -nn -c 10

# nc (netcat) — проверка порта
nc -zv example.com 443
```

## Практика

1. `ip route get` до внешнего IP — понять gateway и интерфейс.
2. `ss -tlnp` — какие сервисы слушают порты.
3. `tcpdump` на DNS-запросе: `sudo tcpdump -i any port 53 -nn`.
