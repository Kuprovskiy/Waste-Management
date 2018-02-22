
import os
import sys
import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
app = Flask(__name__)
db = SQLAlchemy(app)
ma = Marshmallow(app)
Base = declarative_base()
 
class User(Base):
    __tablename__ = 'user'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

class Metric(Base):
    __tablename__ = 'metric'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    reponame = Column(String(250), nullable=False)
    branch = Column(String(250), nullable=False)
    username = Column(String(250), nullable=False)
    build_url = Column(String(250), nullable=False, unique=True)
    status = Column(String(250), nullable=False)
    retry_of = Column(Integer, nullable=True)
    build_time_millis = Column(Integer, nullable=True)
    vcs_revision = Column(String(250), nullable=False)
    vcs_tag = Column(String(250), nullable=True)
    committer_date = Column(DateTime, default=datetime.datetime.utcnow)
    merged_to_master = Column(Boolean, nullable=False)
    related_branch = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'name')

class MetricSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('reponame', 'branch', 'username', 'build_url', 'status', 'retry_of', 'build_time_millis', 'vcs_revision', 'vcs_tag', 'merged_to_master', 'related_branch')

class ProjectSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('reponame', 'username')

class BranchSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('branch', 'reponame')

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///sqlalchemy_example.db')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
