FROM python:3.10

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY src .

# Comando per eseguire l'app Flask
CMD ["python", "/app/app.py"]
