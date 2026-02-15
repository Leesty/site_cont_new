# Деплой на reg.ru — самый простой способ

**Почему так много шагов?** Reg.ru продаёт сервер (VPS), а не «готовый хостинг для Django». То есть вы получаете пустую машину — на ней сами ставите базу, сайт и домен. Другого «одной кнопкой» варианта у reg.ru нет. Ниже — минимальный набор шагов.

---

## Вариант «попроще»: VPS с шаблоном Django

В **Рег.облако** иногда есть образ/шаблон **«Django»** (уже стоят Nginx, Python, PostgreSQL, Gunicorn). Тогда шагов меньше.

### 1. Создать сервер

- Зайти на [reg.ru](https://www.reg.ru) → **Облако** / **VPS**.
- Создать сервер и в каталоге образов выбрать **шаблон «Django»** (или «Python»), если он есть.
- Записать **IP сервера**, подключиться по SSH (логин/пароль из письма или панели).

Если шаблона Django нет — см. раздел «Без шаблона» в конце.

### 2. Залить проект на сервер

Через **SFTP** (FileZilla, WinSCP) или по SSH:

- Скопировать папку проекта (весь каталог с `manage.py`, `base_site`, `core`, `templates`, `static` и т.д.) на сервер, например в `/home/ваш_логин/web/`.

Или по SSH, если есть git:

```bash
cd /home/ваш_логин
mkdir -p web && cd web
git clone <адрес_вашего_репозитория> .
```

### 3. Создать на сервере файл `.env`

В папке с проектом (рядом с `manage.py`) создать файл `.env` с содержимым (подставьте свои данные):

```env
DJANGO_SECRET_KEY=сгенерируйте_длинный_ключ
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=ваш-домен.ru,www.ваш-домен.ru,IP_вашего_сервера

DB_NAME=имя_базы
DB_USER=пользователь_базы
DB_PASSWORD=пароль_базы
DB_HOST=127.0.0.1
DB_PORT=5432
```

Секретный ключ сгенерировать:  
`python3 -c "import secrets; print(secrets.token_urlsafe(50))"`

Если использовали шаблон Django — база и пользователь могли создаться автоматически; данные смотрите в инструкции к шаблону или в панели.

### 4. Запустить проект (миграции и статика)

По SSH:

```bash
cd /home/ваш_логин/web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Если шаблон уже настроил Gunicorn и Nginx — может быть свой каталог и свой способ запуска (например, через systemd). Тогда смотрите справку по шаблону и положите проект в указанную папку, а в настройках укажите путь к вашему приложению (`base_site.wsgi:application`).

### 5. Домен — привязать к серверу

- В reg.ru: **Домены** → ваш домен → **Управление зоной** (или «DNS-записи»).
- Добавить **A-запись**: имя `@`, значение — **IP вашего VPS**. Чтобы работал и `www` — ещё одну A: имя `www`, значение — тот же IP.
- Сохранить. Через 10–30 минут сайт начнёт открываться по `http://ваш-домен.ru`.

### 6. HTTPS (по желанию)

На сервере:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d ваш-домен.ru -d www.ваш-домен.ru
```

Дальше отвечать на вопросы. После этого сайт будет открываться по **https://ваш-домен.ru**.

---

## Если шаблона «Django» нет (голый VPS)

Тогда один раз ставите всё сами. По SSH на новом сервере (Ubuntu):

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx postgresql libpq-dev
sudo -u postgres createuser --createdb -P myuser
sudo -u postgres createdb -O myuser mydb
```

Дальше — шаги 2–6 из раздела выше: залить проект в каталог (например `/var/www/web`), создать `.env` с теми же переменными и правильными `DB_NAME`/`DB_USER`/`DB_PASSWORD`, сделать `venv`, `pip install -r requirements.txt`, `migrate`, `collectstatic`, `createsuperuser`. Запуск через Gunicorn и настройку Nginx для вашего проекта (путь к папке, сокету, `base_site.wsgi:application`) можно взять из полной инструкции в интернете (например, «Django + Gunicorn + Nginx на Ubuntu»).

---

## Кратко

- **Почему много шагов:** reg.ru даёт только сервер, без «деплой одной кнопкой» для Django.
- **Самый простой путь:** VPS с шаблоном Django (если есть) → залить проект → настроить `.env` → migrate, collectstatic, createsuperuser → в DNS указать домен на IP → при желании включить SSL через certbot.

Подробные пошаговые гайды с картинками можно поискать по запросу «развернуть Django на reg.ru» или «Django VPS Ubuntu Nginx Gunicorn».
