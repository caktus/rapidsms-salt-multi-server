import json
import os
import re
import time

from fabric.api import cd, env, get, hide, local, put, require, run, settings, sudo, task
from fabric.colors import red
from fabric.contrib import files, project
from fabric.utils import abort, error

# Directory structure
PROJECT_ROOT = os.path.dirname(__file__)
CONF_ROOT = os.path.join(PROJECT_ROOT, 'conf')
SALT_ROOT = os.path.join(CONF_ROOT, 'roots')
env.project = 'project'
env.project_user = 'project'
env.repo = u'' # FIXME: Add repo URL
env.shell = '/bin/bash -c'
env.disable_known_hosts = True
env.forward_agent = True


@task
def vagrant():
    env.environment = 'staging'
    env.hosts = ['10.10.10.2', ]
    env.branch = 'master'
    setup_path()


@task
def staging():
    env.environment = 'staging'
    env.hosts = [] # FIXME: Add staging server hosts
    env.branch = 'master'
    setup_path()


@task
def production():
    env.environment = 'production'
    env.hosts = [] # FIXME: Add production hosts
    env.branch = 'master'
    setup_path()


def setup_path():
    env.home = '/home/%(project_user)s/' % env
    env.root = os.path.join('/var/www/', '%(project)s-%(environment)s' % env)
    env.code_root = os.path.join(env.root, 'source')
    env.virtualenv_root = os.path.join(env.root, 'env')
    env.db = '%s_%s' % (env.project, env.environment)
    env.settings = '%(project)s.settings.%(environment)s' % env


@task
def provision(common='master'):
    """Provision master with salt-master and salt-minion."""
    require('environment')
    # Install salt minion
    with settings(warn_only=True):
        with hide('running', 'stdout', 'stderr'):
            installed = run('which salt-call')
    if not installed:
        # resolve salt hostnames to localhost
        sudo('echo "127.0.0.1 salt master" >> /etc/hosts')
        sudo('echo "salt" >> /etc/hostname')
        sudo('hostname salt')
        # install salt-master and salt-minion on master
        sudo('apt-get update -q -y')
        sudo('apt-get install python-software-properties -q -y')
        sudo('add-apt-repository ppa:saltstack/salt -y')
        sudo('apt-get update -q')
        sudo('apt-get install salt-master salt-minion -q -y')
        # temporarily stop minon and master
        with settings(warn_only=True):
            sudo('service salt-minion stop')
            sudo('service salt-master stop')
        # pre-seed the master's minion with accepted key
        with cd('/etc/salt/pki/minion/'):
            sudo('salt-key --gen-keys=minion')
        with cd('/etc/salt/pki/master/minions/'):
            sudo('cp /etc/salt/pki/minion/minion.pub /etc/salt/pki/master/minions/salt')
    # make sure git is installed for gitfs
    with settings(warn_only=True):
        with hide('running', 'stdout', 'stderr'):
            installed = run('which git')
    if not installed:
        sudo('apt-get install python-pip git-core -q -y')
        sudo('pip install -U GitPython')
    update_salt_config()


@task
def update_salt_config():
    require('environment')
    with settings(warn_only=True):
        sudo('service salt-master stop')
        sudo('service salt-minion stop')
    # upload master config file
    master_file = os.path.join(CONF_ROOT, 'master.yaml')
    put(master_file, '/etc/salt/master', use_sudo=True)
    sudo('service salt-master start')
    time.sleep(2)
    sudo('service salt-minion start')
    time.sleep(2)
    with settings(warn_only=True):
        sudo("salt '*' test.version -t 15")


@task
def sync():
    """Upload local states to master"""
    require('environment')
    # Rsync local states and pillars
    salt_root = SALT_ROOT if SALT_ROOT.endswith('/') else SALT_ROOT + '/'
    project.rsync_project(local_dir=salt_root, remote_dir='/tmp/salt', delete=True)
    sudo('rm -rf /srv/*')
    sudo('mv /tmp/salt/* /srv/')
    sudo('rm -rf /tmp/salt/')


@task
def highstate(target='*'):
    """Run highstate command on master"""
    require('environment')
    # Update to highstate
    with settings(warn_only=True):
        sudo("salt '{}' state.highstate".format(target))


@task
def bootstrap_minion(name, master):
    """Setup with salt-minion and point to proper master"""
    # point salt hostname to master address
    sudo('echo "{} salt" >> /etc/hosts'.format(master))
    # set hostname
    sudo('echo "{}" >> /etc/hostname'.format(name))
    sudo('hostname {}'.format(name))
    # install salt-minion
    sudo('apt-get update -q -y')
    sudo('apt-get install python-software-properties -q -y')
    sudo('add-apt-repository ppa:saltstack/salt -y')
    sudo('apt-get update -q -y')
    sudo('apt-get install salt-minion -q -y')


@task
def accept_keys(name):
    """Accept specific key on master"""
    require('environment')
    sudo('salt-key --accept={} -y'.format(name))
    sudo('salt-key -L')
    sudo("salt '*' test.ping")


@task
def provision_minions(delete=False):
    cmd = ['salt-cloud -m /etc/salt/cloud.map -P']
    if delete:
        cmd.append('-d')
    sudo(' '.join(cmd))


@task
def salt(cmd, target='*'):
    sudo("salt '%s' %s" % (target, cmd))


@task
def supervisor_command(command):
    """Run a supervisorctl command."""
    sudo(u'supervisorctl %s' % command)


def project_run(cmd):
    """ Uses sudo to allow developer to run commands as project user."""
    sudo(cmd, user=env.project_user)


@task
def update_requirements():
    """Update required Python libraries."""
    require('environment')
    project_run(u'HOME=%(home)s %(virtualenv)s/bin/pip install --use-mirrors -r %(requirements)s' % {
        'virtualenv': env.virtualenv_root,
        'requirements': os.path.join(env.code_root, 'requirements', 'production.txt'),
        'home': env.home,
    })


@task
def manage_run(command):
    """Run a Django management command on the remote server."""
    require('environment')
    manage_base = u"source %(virtualenv_root)s/bin/activate && %(virtualenv_root)s/bin/django-admin.py " % env
    if '--settings' not in command:
        command = u"%s --settings=%s" % (command, env.settings)
    project_run(u'%s %s' % (manage_base, command))


@task
def manage_shell():
    """Drop into the remote Django shell."""
    manage_run("shell")


@task
def syncdb():
    """Run syncdb and South migrations."""
    manage_run('syncdb --noinput')
    manage_run('migrate --noinput')


@task
def collectstatic():
    """Collect static files."""
    manage_run('collectstatic --noinput')


def match_changes(changes, match):
    pattern = re.compile(match)
    return pattern.search(changes) is not None


@task
def deploy(branch=None):
    """Deploy to a given environment."""
    require('environment')
    if not env.repo:
        abort('env.repo is not set.')
    if branch is not None:
        env.branch = branch
    requirements = False
    migrations = False
    if files.exists(env.code_root):
        # Fetch latest changes
        with cd(env.code_root):
            run('git fetch origin')
            # Look for new requirements or migrations
            changes = run("git diff origin/%(branch)s --stat-name-width=9999" % env)
            requirements = match_changes(changes, r"requirements/")
            migrations = match_changes(changes, r"/migrations/")
            if requirements or migrations:
                supervisor_command('stop %(project)s-%(environment)s:*' % env)
            run("git reset --hard origin/%(branch)s" % env)
    else:
        # Initial clone
        run('git clone %(repo)s %(code_root)s' % env)
        with cd(env.code_root):
            run('git checkout %(branch)s' % env)
        requirements = True
        migrations = True
        # Add code root to the Python path
        path_file = os.path.join(env.virtualenv_root, 'lib', 'python2.7', 'site-packages', 'project.pth')
        files.append(path_file, env.code_root, use_sudo=True)
        sudo('chown %s:%s %s' % (env.project_user, env.project_user, path_file))
        sudo('chmod 775 %(code_root)s' % env)
    sudo('chown %(project_user)s:admin -R %(code_root)s' % env)
    if requirements:
        update_requirements()
        # New requirements might need new tables/migrations
        syncdb()
    elif migrations:
        syncdb()
    collectstatic()
    supervisor_command('restart %(project)s-%(environment)s:*' % env)


@task
def get_db_dump(clean=True):
    """Get db dump of remote enviroment."""
    require('environment')
    dump_file = '%(project)s-%(environment)s.sql' % env
    temp_file = os.path.join(env.home, dump_file)
    flags = '-Ox'
    if clean:
        flags += 'c'
    sudo('pg_dump %s %s > %s' % (flags, env.db, temp_file), user=env.project_user)
    get(temp_file, dump_file)


@task
def load_db_dump(dump_file):
    """Load db dump on a remote environment."""
    require('environment')
    temp_file = os.path.join(env.home, '%(project)s-%(environment)s.sql' % env)
    put(dump_file, temp_file, use_sudo=True)
    sudo('psql -d %s -f %s' % (env.db, temp_file), user=env.project_user)
