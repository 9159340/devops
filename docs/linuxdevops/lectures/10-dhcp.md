# 10. DHCP

Подробнее по [краткой лекции](../linux-lectures.md) и [плану изучения](../linux-plan-dim.md).

## Зачем нужен DHCP

**DHCP** (Dynamic Host Configuration Protocol) — автоматическая выдача сетевых параметров клиенту: IP-адрес, маска, шлюз, DNS и др.

Клиент при старте ещё не знает свой IP — поэтому первые сообщения идут **broadcast** (на всю подсеть).

## Процесс DORA

| Шаг | Сообщение | Кто | Смысл |
|-----|-----------|-----|-------|
| 1 | **D**iscover | Клиент → broadcast | «Есть DHCP-сервер?» |
| 2 | **O**ffer | Сервер → клиент | «Вот тебе IP 10.0.0.50» |
| 3 | **R**equest | Клиент → broadcast | «Беру этот IP» |
| 4 | **A**ck | Сервер → клиент | «Подтверждаю, вот опции» |

Порты: сервер **67/udp**, клиент **68/udp**.

```bash
sudo tcpdump -i any port 67 or port 68 -nn -v
```

## Аренда (lease)

**Lease** — срок, на который выдан IP.

- **T1** (~50% lease) — клиент пытается **renew** у того же сервера (unicast).
- **T2** (~87.5%) — **rebind**: спрашивает любой сервер в сети.
- **Release** — клиент явно освобождает адрес при shutdown.

```bash
# Lease-файлы (пути зависят от дистрибутива)
ls /var/lib/dhcp/
ls /var/lib/NetworkManager/
cat /var/lib/dhcp/dhclient*.lease 2>/dev/null | head -50
```

## Важные опции DHCP

| Код | Название | Содержимое |
|-----|----------|------------|
| 3 | Router | Default gateway |
| 6 | DNS | Список DNS-серверов |
| 51 | Lease Time | Время аренды в секундах |
| 66/67 | PXE | Сервер и файл для сетевой загрузки |
| 43 | Vendor Specific | Произвольные данные вендора |

## Клиентская сторона

Кто запрашивает DHCP на Linux:

- **dhclient** (классика);
- **NetworkManager**;
- **systemd-networkd**.

```bash
nmcli device show eth0 | grep -E 'IP4.ADDRESS|IP4.GATEWAY|IP4.DNS'
networkctl status eth0
journalctl -u NetworkManager --since "10 min ago" | grep -i dhcp
```

## Статика: MAC vs интерфейс

| Подход | Где настраивается | Когда |
|--------|-------------------|-------|
| Резервация по **MAC** | На DHCP-сервере | Централизованно, IP «прилипает» к железу |
| Статический IP на интерфейсе | netplan, nmcli | Серверы, когда DHCP не нужен |

```bash
# Статика через nmcli (пример)
sudo nmcli con mod "Wired" ipv4.method manual ipv4.addresses 10.0.0.10/24 ipv4.gateway 10.0.0.1
```

## DHCP relay

Если DHCP-сервер в **другой подсети**, broadcast не дойдёт. **DHCP relay** (ip helper на Cisco) пересылает запросы на известный адрес сервера.

```
[Клиент 192.168.1.0/24] --broadcast--> [Router + relay] --unicast--> [DHCP 10.0.0.5]
```

## Серверы (обзорно)

- **dnsmasq** — DHCP + DNS для лаборатории;
- **ISC dhcpd** — классика (устаревает);
- **Kea** — современная замена от ISC.

## IPv6: DHCPv6 и SLAAC (обзорно)

- **SLAAC** (Stateless Address Autoconfiguration) — адрес из префикса роутера через Router Advertisement.
- **DHCPv6** — stateful выдача адресов и опций (аналог DHCP для v6).

```bash
ip -6 addr show
```

## Практика

1. Захватить DORA в `tcpdump` при `sudo dhclient -v eth0` (осторожно — сбросит IP).
2. Найти lease-файл и прочитать выданные DNS и gateway.
3. Объяснить, зачем нужен relay, если сервер в VLAN 10, а клиенты в VLAN 20.
