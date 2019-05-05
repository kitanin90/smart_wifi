FROM freeradius/freeradius-server:3.0.19

COPY sql /etc/raddb/mods-enabled/
COPY default /etc/raddb/sites-available/
COPY queries.conf /etc/raddb/mods-config/sql/main/mysql/