base:
  '*':
    - base
    - sudoers
    - users.devs
    - sshd.github
    - locale.utf8
    - fail2ban
    - version-control
  "*vagrant":
    - vagrant.user
  'web*':
    - sshd
    - project.user
    - project.app
    - project.web
    # - project.db
    # Uncomment to enable celery worker configuration
    # - project.worker
