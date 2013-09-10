include:
  - postgresql

user-{{ pillar['project_name'] }}:
  postgres_user.present:
    - name: {{ pillar['project_name'] }}
    - password: {{ pillar['secrets']['db_password'] }}
    - require:
      - service: postgresql

database-{{ pillar['project_name'] }}:
  postgres_database.present:
    - name: {{ pillar['project_name'] }}_{{ pillar['environment'] }}
    - owner: {{ pillar['project_name'] }}
    - template: template0
    - encoding: UTF8
    - locale: en_US.UTF-8
    - lc_collate: en_US.UTF-8
    - lc_ctype: en_US.UTF-8
    - require:
      - postgres_user: user-{{ pillar['project_name'] }}
      - file: /var/lib/postgresql/configure_utf-8.sh
      - file: hba_conf
      - file: postgresql_conf

postgresql_restart:
  cmd.run:
    - name: service postgresql restart
    - user: root
    - require:
      - pkg: postgresql

hba_conf:
  file.managed:
    - name: /etc/postgresql/9.1/main/pg_hba.conf
    - source: salt://project/db/pg_hba.conf
    - user: postgres
    - group: postgres
    - mode: 0640
    - template: jinja
    - require:
      - pkg: postgresql
    - watch_in:
      - cmd: postgresql_restart

postgresql_conf:
  file.managed:
    - name: /etc/postgresql/9.1/main/postgresql.conf
    - source: salt://project/db/postgresql.conf
    - user: postgres
    - group: postgres
    - mode: 0644
    - template: jinja
    - require:
      - pkg: postgresql
    - watch_in:
      - cmd: postgresql_restart

allow_postgres_conns:
  ufw.allow:
    - name: '5432'
    - enabled: true
    - require:
      - pkg: ufw
