# Production Clocks / Производствени часовници

[English](#english) · [Български](#български)

---

## English

A real-time clock application for manufacturing environments.  
Each location (shop floor, line, department) has its own full-screen clock that changes colour based on the break schedule.

### How it works

The clock displays only the current time (HH:MM) on a full screen and changes colour automatically:

| Colour | Meaning |
|--------|---------|
| **Red** | Working time |
| **Green** | Break in progress |
| **Yellow** | Less than 5 minutes left in the current break |

Updates are delivered in real time via **Server-Sent Events (SSE)** — no page refresh needed.

### Project structure

```
clock/
├── main.py              # Entry point — registers routers, creates the database
├── database.py          # SQLAlchemy setup (SQLite)
├── models.py            # Models: Location, Break
├── translations.py      # All UI strings in Bulgarian and English
├── requirements.txt
├── routers/
│   ├── admin.py         # HTML pages and form handlers (CRUD)
│   └── stream.py        # SSE endpoint — sends time + colour every second
└── templates/
    ├── _navbar.html     # Shared navigation bar (included in admin pages)
    ├── index.html       # Admin page — list of locations
    ├── location.html    # Break management for a single location
    └── clock.html       # Full-screen clock display
```

### Installation

**1. Clone the repository**

```bash
git clone <repo-url>
cd clock
```

**2. Create a virtual environment (recommended)**

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

### Running the app

```bash
uvicorn main:app --reload
```

The application starts at **http://localhost:8000**

> For a production environment remove `--reload` and add `--host 0.0.0.0` to make it accessible on the network:
> ```bash
> uvicorn main:app --host 0.0.0.0 --port 8000
> ```

### URLs

| URL | Description |
|-----|-------------|
| `http://localhost:8000/` | Admin panel — all locations |
| `http://localhost:8000/locations/{id}` | Manage breaks for a location |
| `http://localhost:8000/clock/{id}` | Full-screen clock for a location |
| `http://localhost:8000/stream/{id}` | SSE stream (used internally by the clock) |
| `http://localhost:8000/lang/en` | Switch interface language to English |
| `http://localhost:8000/lang/bg` | Switch interface language to Bulgarian |

### Usage

**Add a location**
1. Open **http://localhost:8000/**
2. Click **"+ Add location"**
3. Enter a name (e.g. `Shop floor 1`, `Line A`)

**Add a break**
1. Click **"Manage"** next to the desired location
2. Click **"+ Add break"**
3. Enter a name, start time and end time in 24-hour format (`HH:MM`)
4. Overnight breaks are supported — e.g. `23:50 → 00:10`

**Display the clock**
1. Click **"Clock"** or **"Open clock"**
2. Open in the browser on the production monitor (32"+ recommended)
3. The clock updates automatically and reconnects after a network interruption

### Tech stack

| Component | Technology |
|-----------|------------|
| Backend | [FastAPI](https://fastapi.tiangolo.com/) |
| Database | SQLite + [SQLAlchemy](https://www.sqlalchemy.org/) |
| Templates | Jinja2 |
| Real-time | Server-Sent Events (SSE) |
| Frontend | [Bootstrap 5](https://getbootstrap.com/) |
| Server | Uvicorn |

**Requirements:** Python 3.10+

---

## Български

Уеб приложение за визуализация на работното време и почивките в производствена среда.  
Всяка локация (цех, линия, отдел) има собствен часовник, който се показва на голям екран и сменя цвета си спрямо графика на почивките.

### Как работи

Часовникът показва само текущия час (ЧЧ:ММ) на цял екран и се оцветява автоматично:

| Цвят | Значение |
|------|----------|
| **Червен** | Работно време |
| **Зелен** | Тече почивка |
| **Жълт** | Почивката приключва след по-малко от 5 минути |

Актуализацията е в реално време чрез **Server-Sent Events (SSE)** — без опресняване на страницата.

### Структура на проекта

```
clock/
├── main.py              # Входна точка — регистрира рутерите и създава базата
├── database.py          # SQLAlchemy конфигурация (SQLite)
├── models.py            # Модели: Location, Break
├── translations.py      # Всички текстове на български и английски
├── requirements.txt
├── routers/
│   ├── admin.py         # HTML страници и форми (CRUD)
│   └── stream.py        # SSE endpoint — праща час + цвят всяка секунда
└── templates/
    ├── _navbar.html     # Споделен navbar (включен в admin страниците)
    ├── index.html       # Администраторска страница — списък с локации
    ├── location.html    # Управление на почивките за дадена локация
    └── clock.html       # Часовник на цял екран
```

### Инсталация

**1. Клонирай проекта**

```bash
git clone <repo-url>
cd clock
```

**2. Създай виртуална среда (препоръчително)**

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

**3. Инсталирай зависимостите**

```bash
pip install -r requirements.txt
```

### Стартиране

```bash
uvicorn main:app --reload
```

Приложението стартира на **http://localhost:8000**

> За production среда премахни `--reload` и добави `--host 0.0.0.0` ако трябва да е достъпно в мрежата:
> ```bash
> uvicorn main:app --host 0.0.0.0 --port 8000
> ```

### Адреси

| Адрес | Описание |
|-------|----------|
| `http://localhost:8000/` | Администраторски панел — всички локации |
| `http://localhost:8000/locations/{id}` | Управление на почивките за локация |
| `http://localhost:8000/clock/{id}` | Часовник на цял екран за локация |
| `http://localhost:8000/stream/{id}` | SSE поток (ползва се вътрешно от часовника) |
| `http://localhost:8000/lang/bg` | Смени езика на български |
| `http://localhost:8000/lang/en` | Смени езика на английски |

### Употреба

**Добавяне на локация**
1. Отвори **http://localhost:8000/**
2. Натисни **„+ Добави локация"**
3. Въведи наименование (напр. `Цех 1`, `Линия А`)

**Добавяне на почивка**
1. Натисни **„Управление"** до избраната локация
2. Натисни **„+ Добави почивка"**
3. Въведи наименование, начало и край в 24-часов формат (`ЧЧ:ММ`)
4. Нощните смени са поддържани — може `23:50 → 00:10`

**Показване на часовника**
1. Натисни **„Часовник"** или **„Отвори часовник"**
2. Отвори в браузър на производствения монитор (32"+ препоръчително)
3. Часовникът се актуализира автоматично и при прекъсване на връзката се свързва наново

### Технологии

| Компонент | Технология |
|-----------|------------|
| Backend | [FastAPI](https://fastapi.tiangolo.com/) |
| База данни | SQLite + [SQLAlchemy](https://www.sqlalchemy.org/) |
| Шаблони | Jinja2 |
| Реалtime | Server-Sent Events (SSE) |
| Frontend | [Bootstrap 5](https://getbootstrap.com/) |
| Сървър | Uvicorn |

**Изисквания:** Python 3.10+
