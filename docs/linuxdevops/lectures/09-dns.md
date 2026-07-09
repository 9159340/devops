# 9. DNS

Подробнее по [краткой лекции](../linux-lectures.md) и [плану изучения](../linux-plan-dim.md).

## Иерархия DNS

**DNS** (Domain Name System) — распределённая база «имя → IP и другие записи».

Иерархия сверху вниз:

```
. (root) → TLD (.com, .ru, .org) → зона example.com → подзона api.example.com
```

**TLD** (Top-Level Domain) — домены верхнего уровня.

**Авторитативный сервер** — хранит «истину» для зоны. **Делегирование** — NS-записи указывают, какие серверы отвечают за подзону.

## Рекурсивный vs авторитативный

| Тип | Роль |
|-----|------|
| **Рекурсивный резолвер** | Идёт по иерархии за клиентом (8.8.8.8, корпоративный DNS) |
| **Авторитативный** | Отвечает только за свои зоны |

**Forwarder** — рекурсивный сервер, который пересылает запросы «вверх» на другой резолвер.

## Типы записей

| Запись | Назначение |
|--------|------------|
| **A** | IPv4-адрес |
| **AAAA** | IPv6-адрес |
| **CNAME** | Алиас на другое имя |
| **NS** | Серверы зоны |
| **SOA** | Start of Authority — метаданные зоны |
| **MX** | Почтовые серверы |
| **TXT** | Произвольный текст (SPF, верификация) |
| **PTR** | Обратное имя по IP |
| **SRV** | Сервис + порт + приоритет |

```bash
dig example.com A +short
dig example.com MX
dig example.com TXT
```

## TTL и кэширование

**TTL** (Time To Live) — сколько секунд резолвер может хранить ответ в кэше.

**Негативное кэширование** — запоминание «записи нет» (NXDOMAIN), чтобы не спамить авторитативные серверы.

```bash
dig example.com | grep -E '^example|IN'
```

## Путь запроса на Linux-хосте

Порядок определяется `/etc/nsswitch.conf` (строка `hosts:`):

```
files dns
```

Типичный путь:

1. `/etc/hosts` — статические записи;
2. `/etc/resolv.conf` — адреса DNS-серверов;
3. **systemd-resolved** — на Ubuntu stub `127.0.0.53`.

```bash
cat /etc/nsswitch.conf | grep hosts
cat /etc/hosts
cat /etc/resolv.conf
resolvectl status           # если systemd-resolved
```

## Отладка: dig и resolvectl

```bash
dig example.com
dig example.com +short
dig example.com @8.8.8.8          # явный сервер
dig example.com +trace              # полный путь от root

dig -x 8.8.8.8                      # обратный PTR

resolvectl query example.com
resolvectl status
```

## PTR и обратные зоны

**PTR** — запись «IP → имя». Нужна для почты (проверка rDNS), некоторых API и логов.

Обратные зоны делегируются владельцу блока IP (провайдер, облако).

## Search-домены и ndots

В `/etc/resolv.conf`:

```
search corp.example.com
options ndots:5
```

Если имя содержит меньше `ndots` точек, резолвер сначала пробует с **search-доменами**. В **Kubernetes** это часто даёт лишние запросы (`myservice.ns.svc.cluster.local` vs `myservice`).

```bash
# В поде Kubernetes
cat /etc/resolv.conf
```

## Свой резолвер (обзорно)

- **dnsmasq** — лёгкий DNS/DHCP для LAN и лабораторий;
- **unbound** — рекурсивный резолвер;
- **BIND** — полноценный авторитативный/рекурсивный сервер.

**DNSSEC** — криптографическая проверка подлинности ответов.  
**DoT/DoH** (DNS over TLS/HTTPS) — шифрование DNS-трафика.

## Практика

1. `dig +trace google.com` — проследить цепочку делегирования.
2. Сравнить `dig @127.0.0.53` и `dig @8.8.8.8` на Ubuntu с resolved.
3. Добавить запись в `/etc/hosts` и проверить, что она имеет приоритет над DNS (при `hosts: files dns`).
