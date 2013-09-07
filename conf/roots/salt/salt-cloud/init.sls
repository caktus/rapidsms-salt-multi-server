{% set master = grains['ip_interfaces']['eth0'][0] %}

apache-libcloud:
  pip.installed

salt-cloud:
  pip.installed

cloud_map:
  file.managed:
    - name: /etc/salt/cloud.map
    - source: salt://salt-cloud/cloud.map
    - user: root
    - group: root
    - mode: 600
    
cloud_profiles:
  file.managed:
    - name: /etc/salt/cloud.profiles
    - source: salt://salt-cloud/cloud.profiles
    - user: root
    - group: root
    - mode: 600

cloud_config:
  file.managed:
    - name: /etc/salt/cloud
    - source: salt://salt-cloud/cloud.dist
    - user: root
    - group: root
    - mode: 600
    - template: jinja
    - context:
      aws_ssh_privkey: /root/aws.pem
      master: {{ master }}
