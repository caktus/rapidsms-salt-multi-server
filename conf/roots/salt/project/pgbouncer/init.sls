postgresql-client:
  pkg:
    - installed

pgbouncer:
  pkg:
    - installed
    - require:
      - pkg: postgresql-client
  service:
    - running
    - enable: True

pgbouncer_ini:
  file.managed:
    - name: /etc/pgbouncer/9.1/pgbouncer.ini
    - source: salt://project/pgbouncer/pgbouncer.ini
    - user: root
    - group: root
    - mode: 0640
    - template: jinja
    - require:
      - pkg: pgbouncer
