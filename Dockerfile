FROM python:3.12.9-alpine3.21

WORKDIR /app
COPY  ./ /app

EXPOSE 80

CMD ["python3", "httpd.py", "-w", "4"]