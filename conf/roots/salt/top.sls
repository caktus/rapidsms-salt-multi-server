base:
  '*':
    - base
    - sudoers
    - users.devs
    - sshd.github
    - locale.utf8
    - fail2ban
    - version-control
  # 'salt-master':
  #   - python
  #   - salt-cloud
  # 'db-master':
  #   - postgresql
  # 'web1':
  #   - project.user
  #   - project.app
  #   - project.web
  #   - project.db
  #   # Uncomment to enable celery worker configuration
  #   # - project.worker
