{% import 'project/_vars.sls' as vars with context %}
{% set venv_dir = vars.path_from_root('env') %}
{% set requirements = vars.build_path(vars.source_dir, 'requirements/production.txt') %}

include:
  - memcached
  - postfix
  - version-control
  - python
  - supervisor
  - project.venv

root_dir:
  file.directory:
    - name: {{ vars.root_dir }}
    - user: {{ pillar['project_name'] }}
    - group: admin
    - mode: 775
    - makedirs: True
    - require:
      - user: project_user

log_dir:
  file.directory:
    - name: {{ vars.log_dir }}
    - user: {{ pillar['project_name'] }}
    - group: www-data
    - mode: 775
    - makedirs: True
    - require:
      - file: root_dir

project_repo:
  git.latest:
    - name: https://github.com/caktus/rapidsms-salt-multi-server.git
    - rev: master
    - target: {{ vars.source_dir }}
    - runas: {{ pillar['project_name'] }}
    - require:
      - file: root_dir
      - pkg: git-core

collectstatic:
  cmd.run:
    - name: . {{ venv_dir }}/bin/secrets && {{ venv_dir }}/bin/django-admin.py collectstatic --noinput --settings={{ pillar['project_name'] }}.settings.{{ pillar['environment'] }}
    - require:
      - git: project_repo
      - virtualenv: venv

syncdb:
  cmd.run:
    - name: . {{ venv_dir }}/bin/secrets && {{ venv_dir }}/bin/django-admin.py syncdb --noinput --settings={{ pillar['project_name'] }}.settings.{{ pillar['environment'] }}
    - require:
      - git: project_repo
      - virtualenv: venv

group_conf:
  file.managed:
    - name: /etc/supervisor/conf.d/{{ vars.project }}-group.conf
    - source: salt://project/supervisor/group.conf
    - user: root
    - group: root
    - mode: 644
    - template: jinja
    - context:
        programs: "{{ vars.project }}-server"
        project: "{{ vars.project }}"
    - require:
      - pkg: supervisor
      - file: log_dir
    - watch_in:
      - cmd: supervisor_update

gunicorn_conf:
  file.managed:
    - name: /etc/supervisor/conf.d/{{ vars.project }}-gunicorn.conf
    - source: salt://project/supervisor/gunicorn.conf
    - user: root
    - group: root
    - mode: 644
    - template: jinja
    - context:
        log_dir: "{{ vars.log_dir }}"
        virtualenv_root: "{{ venv_dir }}"
        settings: "{{ pillar['project_name']}}.settings.{{ pillar['environment'] }}"
        project: "{{ vars.project }}"
        socket: "{{ vars.server_socket }}"
    - require:
      - pkg: supervisor
      - file: log_dir
    - watch_in:
      - cmd: supervisor_update

gunicorn_process:
  supervisord:
    - name: {{ vars.project }}:{{ vars.project }}-server
    - running
    - restart: True
    - require:
      - pkg: supervisor
      - file: gunicorn_conf

node_ppa:
  pkgrepo.managed:
    - ppa: chris-lea/node.js

nodejs:
  pkg.installed:
    - version: 0.10.18-1chl1~precise1
    - require:
      - pkgrepo: node_ppa
    - refresh: True

less:
  cmd.run:
    - name: npm install less@1.4.1 -g
    - user: root
    - unless: which lessc
    - require:
      - pkg: nodejs
