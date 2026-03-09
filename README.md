
# 📝 api_dog

Мини-программа для получения случайной фотографии по названию породы собак. 
Используется бесплатный api: https://dog.ceo/dog-api/
Программа создает для каждой породы новую папку на Яндекс Диске и загружает в нее полученные картинки.
Информация о загруженных фотографиях собирается в JOIN файле.
---

## 📦 Состав проекта

- `api_dog.py` — основной файл запуска программы 
- `settings.py` — файл настройки с токеном Яндекс Диска
- `requirements.txt` — список зависимостей проекта  

---

## 🚀 Инструкция по запуску проекта

### 1. Установите Python

Убедитесь, что у вас установлен **Python 3.8+**

```bash
python --version
```

Если Python не установлен: https://www.python.org/downloads/

---

### 2. Клонируйте проект

Клонируйте проект на свой компьютер:

```bash
git clone https://github.com/yarmanyan/CourseWorkOOP_API.git
```

### 3. Установите зависимости

Создайте виртуальное окружение (по желанию):

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate   # Windows
```

Установите библиотеки:

```bash
pip install -r requirements.txt
```

---

### 4. Запустите программу 

api_dog.py