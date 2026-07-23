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
