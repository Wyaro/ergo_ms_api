# ERGO MS API

## РУКОВОДСТВО ПО УСТАНОВКЕ ПРОЕКТА

### Установка проекта на Windows

Следуйте приведённым ниже шагам для корректной установки и настройки проекта:

#### 1. Создание виртуального окружения
```bash
py -3.12 -m venv .venv
```

#### 2. Активация виртуального окружения
```bash - CMD
call .venv\Scripts\activate
```

```bash - IDE Visual Studio Code
.venv\Scripts\activate
```

#### 3. Установка Poetry
```bash
pip install poetry
```

#### 4. Настройка Poetry для использования виртуального окружения внутри проекта
```bash
poetry config virtualenvs.in-project true
```

#### 5. Установка зависимостей проекта
```bash
poetry install
```

#### 6. Сборка статических файлов
```bash
poetry run cmd collectstatic
```

---

### Установка проекта на Linux

Следуйте приведённым ниже шагам для корректной установки и настройки проекта:

#### 1. Создание виртуального окружения
```bash
python3.12 -m venv .venv
```

#### 2. Активация виртуального окружения
```bash
source .venv/bin/activate
```

#### 3. Установка Poetry
```bash
pip install poetry
```

#### 4. Настройка Poetry для использования виртуального окружения внутри проекта
```bash
poetry config virtualenvs.in-project true
```

#### 5. Установка зависимостей проекта
```bash
poetry install
```

#### 6. Сборка статических файлов
```bash
poetry run cmd collectstatic
```

---

> **Примечание:** Убедитесь, что все команды выполняются из корневой директории проекта. Для работы проекта требуется установленная версия Python 3.12.

## РУКОВОДСТВО ПО ЗАПУСКУ ПРОЕКТА

Для запуска проекта используйте следующие команды:

### Запуск в режиме разработки
```bash
poetry run cmd dev
```

### Запуск в режиме продакшн
```bash
poetry run cmd prod
```

### Остановка режима продакшн
```bash
poetry run cmd stop_prod
```

---

> **Примечание:** Убедитесь, что все зависимости установлены и выполнена настройка проекта перед запуском.

## Структура проекта

- **`commands/`**: [Директория](commands/README.md), предоставляющая функционал для выполнения и управления командами в проекте. Состоит из базовых классов и реализации команд для работы с Python, Django и Poetry.

- **`src/config/`**: [Директория](src/config/README.md), конфигурация Django проекта.

- **`src/core/`**: [Директория](src/core/README.md), ядро функционала Django проекта.

- **`src/external/`**: [Директория](src/external/README.md), сторонние модули Django проекта.

- **`logs`**: [Директория], директория для хранения логов.
- **`media`**: [Директория], директория для хранения медиафайлов.
- **`static`**: [Директория], директория для хранения статических файлов.

- **`.gitignore`**: [Файл], сторонние модули Django проекта.
- **`poetry.lock`**: [Файл], сторонние модули Django проекта.
- **`pyproject.toml`**: [Файл], сторонние модули Django проекта.

- **`TASKS.md`**: [Файл], файл с задачами по Django-API проекту.
---

## Руководство по командам 

[Руководство по модулям и подмодулям](MODULES.md)