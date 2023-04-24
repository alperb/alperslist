FROM python:3.7

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
# RUN mysql --host="192.168.0.20" -u root --pasword="root123" alperslist < dump.sql
ENTRYPOINT [ "python3", "app.py" ]