# PoC Offline Semgrep PRO engine docker image
Этот проект предоставляет **офлайн-решение для запуска Semgrep pro engine** без подключения к облаку Semgrep (semgrep.dev).  
Используется мок-сервер локальный мок сервер.
Author: https://t.me/hatn9g

## 📦 О чём это?

Обычно Semgrep pro engine требует подключения к интернету для получения настроек и правил, без логина в облако нельзя использовать pro engine, с логином нельзя использовать локальные правила.
Этот образ является результатом эксперимента и просто примером\доказательством, как можно такое провернуть

Этот PoC образ решает две задачи:
 - Использовать pro engine без обязательного доступа к semgrep.dev
 - Иметь возможность запускать свои локальные правила (через добавление\удаление правил в мокнутый запрос /mock_server/responses/cli_scans.json)


В образ включены:

 - Semgrep (образ на базе `semgrep/semgrep:1.122.0`)
 - Локальный мок-сервер (`mock_server/`)
 - Тестовый репозиторий (`test_file`)
 - Хак `sitecustomize.py`, чтобы игнорировать ошибки TLS и не возиться с добавлением сертификатов
 - `entrypoint.sh`, который:
   - обновляет `/etc/hosts` для редиректа на `localhost`
   - запускает мок-сервер
   - делает Semgrep login через mock server


## 🧪 Тестовая уязвимость

Директория `test_file` содержит код с уязвимостью, которую определяет только pro engine.

Репозиторий инициализируется во время сборки:

```Dockerfile
RUN cd /test_repo; \
    git init; \
    git add *; \
    git config --global user.email johndoe@example.com; \
    git remote add origin https://fake_repo.com; \
    git commit -m 'Initial project version';
```


## Использование
```
    docker build -t semgrep-pro-offline .
    docker run --rm -it semgrep-pro-offline bash -c "source ./entrypoint.sh && cd /test_repo && semgrep ci --pro --sarif --sarif-output=out.sarif"
```

Команда запустит энтрипоинт, который настроит локальный сервер и семгреп, затем перейдет в тестовый репозиторий и запустить сканирование тестового репозитория и создаст файл с отчетом.

# ⚠️ Заметки

Это грязный хак, используемый только для демонстрации.

Этот образ предназначен для исследовательских и образовательных целей, не для продакшена.

Вы нарушаете EULA Semgrep при коммерческом использовании PRO-движка вне их облака.	

