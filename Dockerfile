FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

COPY run.sh /app/run.sh


RUN chmod +x /app/run.sh

CMD ["/app/run.sh"]