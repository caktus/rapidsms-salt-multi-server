base:
  "*":
    - devs
    - project
  "*staging*":
    - staging.env
    - staging.secrets
  "*production*":
    - production.env
    - production.secrets
