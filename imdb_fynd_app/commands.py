import click
from flask.cli import with_appcontext

from .extensions import db
from .models import *

@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()

@click.option('--username', '-u', default='admin', help='Please enter your username')
@click.option('--email', '-e',default='admin@mailinator.com', help="whats your email")
@click.option('--password', '-p', default='admin', help='Please enter your secured password')
@click.command(name='create_superuser')
@with_appcontext
def create_superuser(username,email,password):
    # usage- https://pymbook.readthedocs.io/en/latest/click.html
    # flask create_superuser -e yajant@mailinator.com -u iamyajant -p admin
    # or
    # flask create_superuser
    
    db.create_all()
    # Only needed on first execution to create first user       
    super_user = User(username=username,email=email, password=password, is_superuser=True, is_active=True) 
    # super_user = User(username='admin',email='admin@mailinator.com', password='download123', superuser=True)  
    db.session.add(super_user)
    db.session.commit()
