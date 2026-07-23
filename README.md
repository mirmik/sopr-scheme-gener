# sopr-scheme-gener

Редактор схем типовых задач по сопротивлению материалов.

## Запуск из исходного дерева

```bash
python -m sopr_scheme_gener
```

Для установки команд приложения и зависимостей в виртуальное окружение:

```bash
python -m pip install -e .
sopr-scheme-gener
```

Исторический запуск `python sopr-sheme-gener.py` пока также поддерживается.

## Application boundary

Новый application shell использует явный `AppContext`. Выбор текущего типа и
координация его UI принадлежат `DocumentController`. Старые глобалы
`common.APP`, `CONFVIEW`, `SCHEMETYPE`, `HSPLITTER` и `PAINT_CONTAINER`
публикуются только через `LegacyAdapter` в `sopr_scheme_gener/legacy.py`.

Новый package-код не должен обращаться к этим глобалам напрямую. Это правило
закреплено архитектурным тестом и позволяет постепенно переносить legacy-задачи
без изменения их текущего рендера.

## Development API

Приложение может открыть локальный TCP API для автоматизации и живой
диагностики:

```bash
sopr-scheme-gener --dev-api
soprctl info
soprctl tasks
soprctl select beams
soprctl screenshot /tmp/beams.png
```

По умолчанию сервер слушает только `127.0.0.1:8765` и создаёт защищённый
токеном discovery-файл во временном каталоге системы. Для подключения с другой
машины явно задайте `--dev-host`, `--dev-port` и `--dev-token`, а клиенту
передайте соответствующие параметры. Протокол не шифрует трафик, поэтому
удалённое подключение следует пропускать только через доверенную сеть, VPN или
SSH-туннель.

Доверенные Python-сценарии включаются отдельно:

```bash
sopr-scheme-gener --dev-api --unsafe-dev-exec
soprctl exec --code "ctx.select_task('stress-cube'); result = ctx.canvas.size()"
```

Этот режим даёт выполняемому коду полный доступ к процессу приложения и не
должен включаться для недоверенных подключений.

## Render baseline

Текущий визуальный результат Qt5/Linux зафиксирован для default-состояния всех
11 типов задач и для 11 доверенных legacy-файлов из репозитория:

```bash
sopr-baseline verify
```

Команда запускает каждый сценарий в отдельном offscreen-процессе и проверяет
размер, SHA-256 и число непустых пикселей PNG. После намеренного изменения
визуального результата эталоны обновляются только после просмотра новых
изображений:

```bash
sopr-baseline capture
```

Эталоны из `tests/baselines/linux-qt5` платформенные. Для Windows потребуется
отдельный профиль, поскольку шрифты и растеризация Qt могут отличаться.
