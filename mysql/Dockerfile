FROM mysql:8.0

WORKDIR /app

# Script for creating init.sql
COPY ./init-mysql.sh /app/init-mysql.sh
RUN chmod +x /app/init-mysql.sh

ENTRYPOINT [ "/app/init-mysql.sh" ]