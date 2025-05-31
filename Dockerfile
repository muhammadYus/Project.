# Rasm: eng so‘nggi Python
FROM python:3.12

# Loyihaning ishchi papkasini belgilash
WORKDIR /app

# Kutubxonalar uchun
COPY requirements.txt .

# Paketlarni o‘rnatish
RUN pip install --no-cache-dir -r requirements.txt

# Butun loyihani nusxalash
COPY . .

# Standart port
EXPOSE 8000

# Standart server komandasi
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
