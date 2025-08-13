# Проект библиотеки MRS REST API для Python.

## Установка

Данный пакет устанавливается через PIP. 

```shell
pip install pymrs
```

## Назначение:

Библиотека на языке Python для унифицированного использования REST API программного комплекса Memoza Rest Server (MRS). Основное применение - это создание программ и скриптов для обслуживания данных MRS, учитывая особености и требования многочисленных пользователей.
Для возможности работы с WRS в рамках модуля имплементированы классы AsyncMRSClient, MRSClient, Query и DataIterator. Все классы имеют возможность использования при мэнеджменте контекста.

## Класс AsyncMRSClient

AsyncMRSClient это основной класс, предназначенный для создания клиентской сессии и отправления запросов на сервер. При помощи него отправляются запросы во всех классах, реализованных в данном модуле. Инициализируется именем хоста (URL сервера MRS, на который будут отправляться запросы), токеном, именем пользователя и либо паролем, либо уже выданным тикетом.

### Методы класса

| Имя метода | Описание метода |
|-----------------------|-------------|
| `_authenticate()` | Аутентифицирует пользователя при помощи данных, заданных при инициализации, получая тикет для дальнейших запросов. |
| `validate_ticket()` | Проверяет валидность тикета, при необходимости запрашивает новый. |
| `close()` | Отправляет запрос на сервер для прекращения связи. |
| `_handle_error()` | Метод используется для обработки ошибок при отправлении запросов, поднимает ошибку `MRSClientError` с кодом ошибки и сообщением, полученным от сервера. |
| `request()` | Метод, при помощи которого отправляются запросы. |
| `get_all_namespaces()` | Метод, который возвращает список всех пространств имен, хранимых на сервере. |
| `get_namespace()` | Метод, который возвращает данные о метаклассах, хранящихся в рамках конкретного пространства имен. |
| `get_datatype()` | Метод, который возвращает данные о метаклассе, хранящегося в рамках конкретного пространства имен. |
| `es_request()` | Метод для отправки запроса Elasticsearch с возможностью фильтрации по ролям при необходимости. |
| `get_user_roles()` | Метод для получения информации о ролях пользователей в рамках конкретного пространства имен. |
| `upload_file()` | Метод для загрузки файлов на сервер. |

### Свойства класса

| Имя свойства | Описание |
|--------------|-------------|
| `headers` | При вызове данное свойство возвращает HTTP заголовки, хранящиеся в существующей сессии. |
| `ticket` | При вызове данное свойство возвращает тикет, хранящийся в существующей сессии. |
---

## Класс MRSClient

Данный класс является синхронной оболчкой вокруг асинхронной имплементации класса, позволяя использовать методы AsyncMRSClient в рамках синхронного кода.

## Класс Query

Класс Query является классом, который используется для сборки и отправки поисковых запросов. Иницииализируется сессией AsyncMRSClient и пространством имен, в котором будет производиться поиск.

### Основные методы поиска

#### `assemble_query(url=False, data=False)`

Собирает запрос на основании параметров поиска, заданных в качестве атрибутов класса. Этот метод является основой для всех поисковых операций.

**Параметры:**
- `url` (bool): Если True, возвращает запрос в виде URL-строки для GET-запросов
- `data` (bool): Если True, возвращает запрос в виде bytes для POST-запросов

**Возвращает:**
- `str`: JSON-строка с собранным запросом (по умолчанию)
- `str`: URL-строка (при url=True)
- `bytes`: Данные в формате bytes (при data=True)

**Примеры использования:**

```python
# Базовый поиск по метаклассу со скроллингом
query = Query(client=client, namespace="tps71")
query.metaclass = "WellHistory"
query.scroll = True
query.scroll_count = 1000  # Размер батча для скроллинга

# Получить JSON-строку запроса
json_query = query.assemble_query()
print(json_query)
# {"query":{"classname":"tps71:WellHistory"},"scroll":true,"count":1000}

# Получить URL для GET-запроса
url_query = query.assemble_query(url=True)
print(url_query)
# /data/tps71.json?q={"query":{"classname":"tps71:WellHistory"},"scroll":true,"count":1000}

# Получить данные в формате bytes для POST-запроса
data_query = query.assemble_query(data=True)
```

**Поиск с фильтрами и скроллингом:**

```python
# Поиск с условиями равенства
query = Query(client=client, namespace="tps71")
query.metaclass = "WellHistory"
query.query_eq = [{"wellName": "WELL-001"}, {"status": "active"}]
query.scroll = True
query.scroll_count = 500  # Размер батча

# Поиск с условиями сравнения
query.query_ge = [{"depth": 1000.0}]  # глубина >= 1000
query.query_lt = [{"depth": 5000.0}]  # глубина < 5000

# Поиск с текстовыми паттернами
query.query_like = [{"description": "*test*"}]
query.query_queryString = "well AND production"

# Настройка отображения результатов
query.loadProperties = ["tps71:WellHistory", "kmeta:QC"]
query.showGeom = True

json_query = query.assemble_query()
```

#### `get_records(return_iterator=True)`

Выполняет поисковый запрос и возвращает результаты. Этот метод автоматически вызывает `assemble_query()` для построения запроса.

**Параметры:**
- `return_iterator` (bool): Если True, возвращает DataIterator для итерации по результатам

**Возвращает:**
- `DataIterator`: Итератор для обхода результатов (по умолчанию)
- `list`: Список сущностей (при return_iterator=False)
- `None`: При ошибке соединения

**Примеры использования:**

```python
# Базовый поиск с итератором и скроллингом
query = Query(client=client, namespace="tps71")
query.metaclass = "WellHistory"
query.scroll = True
query.scroll_count = 1000  # Размер батча для эффективного скроллинга

data_iterator = await query.get_records()
if data_iterator:
    async for entity in data_iterator:
        print(f"Entity URI: {entity.get('uri')}")
        print(f"Properties: {entity.get('properties', {})}")
    # Скролл автоматически закрывается при завершении итерации
```

```python
# Поиск с фильтрами и ограничением количества записей
query = Query(client=client, namespace="tps71")
query.metaclass = "WellHistory"
query.query_eq = [{"status": "active"}]
query.scroll = True
query.scroll_count = 500
query.loadProperties = ["tps71:WellHistory", "kmeta:QC"]

data_iterator = await query.get_records()
if data_iterator:
    count = 0
    async for entity in data_iterator:
        count += 1
        print(f"Entity {count}: {entity.get('uri')}")
        if count >= 1000:  # Ограничить обработку 1000 записями
            break
    
    # При преждевременном завершении закрыть скролл вручную
    await query.close_scroll()
```

#### `close_scroll()`

Закрывает контекст скроллинга на сервере. Этот метод должен вызываться после завершения работы со скроллингом для освобождения ресурсов сервера.

**Возвращает:**
- `dict`: Ответ сервера при успешном закрытии
- `None`: Если scrollId не установлен

**Примеры использования:**

```python
# Ручное управление скроллингом
query = Query(client=client, namespace="tps71")
query.metaclass = "WellHistory"
query.scroll = True
query.scroll_count = 1000

data_iterator = await query.get_records()
try:
    count = 0
    async for entity in data_iterator:
        count += 1
        print(f"Processing entity {count}")
        if count >= 5000:  # Прервать после 5000 записей
            break
finally:
    # Обязательно закрыть скроллинг
    await query.close_scroll()
```

### Совместное использование методов

Методы Query работают в следующей последовательности:

1. **Настройка параметров запроса** - установка атрибутов класса
2. **Сборка запроса** - `assemble_query()` (вызывается автоматически в `get_records()`)
3. **Выполнение запроса** - `get_records()`
4. **Обработка результатов** - итерация через DataIterator
5. **Очистка ресурсов** - `close_scroll()` (вызывается автоматически в DataIterator)

### Важно: Скроллинг vs Пагинация

**Рекомендуется использовать скроллинг** для всех поисковых запросов, поскольку:
- Скроллинг полностью поддерживается модулем и стабильно работает
- Пагинация имеет ограниченную поддержку и может работать нестабильно
- DataIterator оптимизирован для работы со скроллингом

```python
# Рекомендуемый подход - скроллинг
query.scroll = True
query.scroll_count = 1000

# Не рекомендуется - пагинация
# query.pagination_start = 0
# query.pagination_count = 100
```

**Полный пример со скроллингом:**

```python
async def search_with_scrolling():
    query = Query(client=client, namespace="tps71")
    query.metaclass = "WellHistory"
    query.scroll = True
    query.scroll_count = 1000  # Размер батча
    query.query_eq = [{"status": "active"}]
    
    try:
        data_iterator = await query.get_records()
        if data_iterator:
            async for entity in data_iterator:
                # Обработка каждой сущности
                process_entity(entity)
        # close_scroll() вызывается автоматически при завершении итерации
    except Exception as e:
        # В случае ошибки принудительно закрыть скроллинг
        await query.close_scroll()
        raise e
```

**Пример с батчевой обработкой через скроллинг:**

```python
async def search_with_batching():
    query = Query(client=client, namespace="tps71")
    query.metaclass = "WellHistory"
    query.scroll = True
    query.scroll_count = 1000  # Размер батча
    query.query_eq = [{"status": "active"}]
    
    data_iterator = await query.get_records()
    if data_iterator:
        batch_num = 0
        processed_in_batch = 0
        
        async for entity in data_iterator:
            if processed_in_batch == 0:
                batch_num += 1
                print(f"Processing batch {batch_num}")
            
            processed_in_batch += 1
            
            # Обработка сущности
            process_entity(entity)
            
            # Лог каждые 1000 записей
            if processed_in_batch == 1000:
                print(f"Completed batch {batch_num}: {processed_in_batch} entities")
                processed_in_batch = 0
        
        # Финальная статистика
        if processed_in_batch > 0:
            print(f"Final batch {batch_num}: {processed_in_batch} entities")
```

**Пример с расширенным поиском:**

```python
async def advanced_search():
    query = Query(client=client, namespace="tps71")
    query.metaclass = "WellHistory"
    
    # Комбинированные условия поиска
    query.query_eq = [{"status": "active"}]
    query.query_ge = [{"depth": 1000.0}]
    query.query_like = [{"wellName": "WELL-*"}]
    query.query_queryString = "production AND oil"
    
    # Настройка скроллинга
    query.scroll = True
    query.scroll_count = 500
    
    # Настройка отображения результатов
    query.loadProperties = ["tps71:WellHistory", "kmeta:QC"]
    query.showGeom = True
    query.highlighted = True
    
    # Отладочная информация
    print("Assembled query:", query.assemble_query())
    print("Query URL:", query.assemble_query(url=True))
    
    # Выполнение запроса
    data_iterator = await query.get_records()
    if data_iterator:
        count = 0
        async for entity in data_iterator:
            count += 1
            print(f"Entity {count}: {entity.get('uri')}")
        print(f"Total entities processed: {count}")
```

### Другие методы класса

| Имя метода | Описание метода |
|-----------------------|-------------|
| `get_entities()` | Возвращает список сущностей, хранимых в рамках конкретного класса. |
| `get_content()` | Возвращает содержимое конкретной сущности. |
| `register_entities()` | Регистрирует список новых сущностей в указанном пространстве имен. Позволяет автоматически генерировать URI, если они не предоставлены. Обрабатывает сущности пакетами. |
| `patch_entities()` | Обновляет указанные свойства для списка существующих сущностей в указанном пространстве имен. Требует URI для каждой сущности. Обрабатывает сущности пакетами. |

### Свойства класса

| Имя свойства | Описание |
|-----------------------|-------------|
| `url` | При вызове данное свойство возвращает ссылку для отправки запроса. |
| `data` | При вызове данное свойство возвращает собранный поисковый запрос. |

## Класс DataIterator

Данный класс является итерируемым контейнером данных, полученных в результате поискового запроса метода Query.get_records(). DataIterator обеспечивает эффективную обработку больших объемов данных через механизм скроллинга, автоматически управляя жизненным циклом скролл-сессии.

### Основные возможности

- **Асинхронная итерация**: Поддержка `async for` для обработки данных по одной записи
- **Автоматическое управление скроллингом**: Автоматическое получение новых батчей данных при исчерпании текущего
- **Управление ресурсами**: Автоматическое закрытие скролл-сессии при завершении итерации
- **Контекстный менеджер**: Поддержка `async with` для гарантированной очистки ресурсов

### Методы и свойства

| Метод/Свойство | Описание |
|----------------|----------|
| `__init__(query, entities, length)` | Инициализация с объектом Query, первым батчем данных и общим количеством записей |
| `__aiter__()` | Возвращает асинхронный итератор |
| `__anext__()` | Возвращает следующую сущность, автоматически загружая новые батчи при необходимости |
| `__len__()` | Возвращает количество записей в текущем батче |
| `__aenter__()` | Вход в контекстный менеджер |
| `__aexit__()` | Выход из контекстного менеджера |
| `total_length` | Общее количество записей в результате поиска |
| `current_batch` | Номер текущего батча |
| `total_batches` | Общее количество батчей |

### Примеры использования

#### Базовая итерация

```python
query = Query(client=client, namespace="tps71")
query.metaclass = "WellHistory"
query.scroll = True
query.scroll_count = 1000

data_iterator = await query.get_records()
async for entity in data_iterator:
    print(f"Processing: {entity.get('uri')}")
    # Автоматически закрывает скролл-сессию при завершении
```

#### Использование с контекстным менеджером

```python
query = Query(client=client, namespace="tps71")
query.metaclass = "WellHistory"
query.scroll = True
query.scroll_count = 1000

async with await query.get_records() as data_iterator:
    count = 0
    async for entity in data_iterator:
        count += 1
        print(f"Entity {count}/{data_iterator.total_length}: {entity.get('uri')}")
        
        if count >= 5000:  # Ограничить обработку
            break
# Ресурсы автоматически освобождаются при выходе из контекста
```

#### Обработка с отслеживанием прогресса

```python
async def process_with_progress():
    query = Query(client=client, namespace="tps71")
    query.metaclass = "WellHistory"
    query.scroll = True
    query.scroll_count = 1000
    
    data_iterator = await query.get_records()
    print(f"Total records to process: {data_iterator.total_length:,}")
    print(f"Processing in {data_iterator.total_batches} batches")
    
    processed = 0
    async for entity in data_iterator:
        processed += 1
        
        # Отображение прогресса каждые 1000 записей
        if processed % 1000 == 0:
            progress = (processed / data_iterator.total_length) * 100
            print(f"Progress: {processed:,}/{data_iterator.total_length:,} ({progress:.1f}%)")
        
        # Обработка сущности
        process_entity(entity)
    
    print(f"Processing completed: {processed:,} entities")
```

#### Обработка ошибок

```python
async def safe_processing():
    query = Query(client=client, namespace="tps71")
    query.metaclass = "WellHistory"
    query.scroll = True
    query.scroll_count = 1000
    
    try:
        data_iterator = await query.get_records()
        async for entity in data_iterator:
            try:
                process_entity(entity)
            except Exception as e:
                print(f"Error processing entity {entity.get('uri', 'unknown')}: {e}")
                continue
    except Exception as e:
        print(f"Fatal error during iteration: {e}")
        # Принудительно закрыть скролл-сессию
        await query.close_scroll()
        raise
```

#### Раннее завершение с очисткой ресурсов

```python
async def early_termination():
    query = Query(client=client, namespace="tps71")
    query.metaclass = "WellHistory"
    query.scroll = True
    query.scroll_count = 1000
    
    data_iterator = await query.get_records()
    
    try:
        async for entity in data_iterator:
            if should_stop_processing():
                print("Early termination requested")
                break
            
            process_entity(entity)
    finally:
        # Обязательно закрыть скролл-сессию при раннем завершении
        if query.scrollId:
            await query.close_scroll()
            print("Scroll session closed")
```

### Внутренний механизм работы

1. **Инициализация**: DataIterator создается с первым батчем данных и метаинформацией о запросе
2. **Итерация**: При каждом вызове `__anext__()` возвращается следующая сущность из текущего батча
3. **Автозагрузка**: При исчерпании текущего батча автоматически запрашивается следующий батч
4. **Завершение**: При исчерпании всех данных автоматически закрывается скролл-сессия
5. **Логирование**: Каждые 10 батчей выводится информация о прогрессе обработки

### Интеграция с Query

DataIterator тесно интегрирован с классом Query:

```python
# Query создает DataIterator
data_iterator = await query.get_records()

# DataIterator использует query для получения новых батчей
# query.client.request() для запроса данных
# query.url и query.data для параметров запроса
# query.close_scroll() для закрытия сессии

# Автоматическое обновление scrollId в query
# query.scrollId обновляется при получении каждого нового батча
```
