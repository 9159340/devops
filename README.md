# devops

Документация на [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).

Сайт: https://9159340.github.io/devops/

## Публикация

При `git push` в ветку `main` GitHub Actions собирает сайт и выкладывает его на GitHub Pages:

https://9159340.github.io/devops/

Деплой идёт автоматически через workflow `.github/workflows/ci.yml` (`mkdocs gh-deploy`).

## Требования

- Python 3.x
- pip

```bash
pip install mkdocs-material
```

## Локальный сервер

Запуск с live-reload (удобно для чтения и правок):

```bash
mkdocs serve
```

Откройте в браузере: http://127.0.0.1:8000/

## Сборка сайта

Статическая сборка в каталог `site/`:

```bash
mkdocs build
```

Проверка сборки без вывода в `site/`:

```bash
mkdocs build --strict
```
