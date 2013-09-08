{% import 'project/_vars.sls' as vars with context %}
{% set venv_dir = vars.path_from_root('env') %}

venv:
  virtualenv.managed:
    - name: {{ venv_dir }}
    - no_site_packages: True
    - distribute: True
    - requirements: {{ vars.build_path(vars.source_dir, 'requirements/production.txt') }}
    - require:
      - pip: virtualenv
      - file: root_dir
      - git: project_repo

venv_dir:
  file.directory:
    - name: {{ venv_dir }}
    - user: {{ pillar['project_name'] }}
    - group: {{ pillar['project_name'] }}
    - recurse:
      - user
      - group
    - require:
      - virtualenv: venv

project_path:
  file.managed:
    - source: salt://project/venv/project.pth
    - name: {{ vars.build_path(venv_dir, 'lib/python2.7/site-packages/project.pth') }}
    - user: {{ pillar['project_name'] }}
    - group: {{ pillar['project_name'] }}
    - template: jinja
    - context:
      source_dir: {{ vars.source_dir }}

activate:
  file.append:
    - name: {{ vars.build_path(venv_dir, "bin/activate") }}
    - text: source {{ vars.build_path(venv_dir, "bin/secrets") }}
    - require:
      - virtualenv: venv

secrets:
  file.managed:
    - name: {{ vars.build_path(venv_dir, "bin/secrets") }}
    - source: salt://project/env_secrets.jinja2
    - user: {{ pillar['project_name'] }}
    - group: {{ pillar['project_name'] }}
    - template: jinja
    - require:
      - file: activate
