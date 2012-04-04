#!/usr/bin/env python
from __future__ import with_statement
from fabric.api import local, settings, abort, run, cd, env
from fabric.contrib.console import confirm
import os

# glogal env
env.warn_only = True
env.supervisor = '/etc/supervisord'
env.nginx = '/etc/nginx/sites-enabled'

def clean():
    local("find . -name '*.DS_Store' -type f -delete")
    local("find . -name '*.pyc' -type f -delete")

def tx_push():
    """
    push translations
    """
    local('cd website && ./manage.py makemessages --all --ignore=socialregistration/* --ignore=filer/*')
    local('tx push -t -s') 

def tx_pull():
    """
    push translations
    """
    local('tx pull')
    local('cd website && ./manage.py compilemessages') 
    




"""
ad definition for your domains, eg:
"""

    
def hzlfbase_com():
    env.site_id = 'hzlfbase.com'
    env.hosts = ['node05.daj.anorg.net']
    env.git_url = 'git@lab.anorg.net:com-hazelfire.git'
    env.git_branch = 'trunk'
    env.path = '/var/www/hzlfbase.com'
    env.storage = '/var/www_data/hzlfbase.com'
    env.user = 'root'
    

def deploy():
    """
    """
    with cd(env.path):  
        
        """
        create directory to save the local_config
        """
        try:
            run('mkdir config')
        except Exception, e:
            print e
            pass
        
        try:
            run('cp src/website/local_settings.py config/')  
        except Exception, e:
            print e
        
        """
        recreate src directory
        """    
        try:
            run('rm -Rf src')
        except Exception, e:
            print e
        
        run('mkdir src')

        
    with cd(env.path + '/src'):
        
        """
        aquire code from repository
        """
        run('git init')
        run('git remote add -t %s -f origin %s' % (env.git_branch, env.git_url))
        run('git checkout %s' % (env.git_branch))
        
    with cd(env.path): 

        """
        copy back the local_settings
        """
        try:
            run('cp config/local_settings.py src/website/')
        except Exception, e:
            print e
            
        
        """
        virtualenv and requirements
        """
        try:
            run('virtualenv --no-site-packages /srv/%s' % env.site_id)
        except Exception, e:
            print e

        run('pip -E /srv/%s install -r %s' % (env.site_id, 'src/website/requirements/requirements.txt'))
        
            
        """
        linking storage directories
        """
        try:
            run('ln -s %s/media %s/src/website/media' % (env.storage, env.path))
            run('ln -s %s/smedia %s/src/website/smedia' % (env.storage, env.path))
        except Exception, e:
            print e
            
            
        """
        linking config files
        """
        try:
            run('rm %s/%s.conf' % (env.supervisor, env.site_id))
            run('ln -s %s/src/conf/%s.supervised.conf %s/%s.conf' % (env.path, env.site_id, env.supervisor, env.site_id))
        except Exception, e:
            print e
            
        try:
            run('rm %s/%s' % (env.nginx, env.site_id))
            run('ln -s %s/src/conf/%s.nginx.conf %s/%s' % (env.path, env.site_id, env.nginx, env.site_id))
        except Exception, e:
            print e
            
        """
        run migrations
        """
        try:
            run('/srv/%s/bin/python /%s/src/website/manage.py migrate' % (env.site_id, env.path))
        except Exception, e:
            print e
            
        """
        staticfiles & compress
        """
        try:
            run('/srv/%s/bin/python /%s/src/website/manage.py collectstatic --noinput' % (env.site_id, env.path))
            run('/srv/%s/bin/python /%s/src/website/manage.py compress -f' % (env.site_id, env.path))
        except Exception, e:
            print e
            
        """
        (re)start gunicorn worker
        """
        try:
            run('supervisorctl restart %s' % env.site_id)
            run('supervisorctl status')
        except Exception, e:
            print e
        
        
        
        
