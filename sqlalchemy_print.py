from sqlalchemy_declarative import Metric, Base
from sqlalchemy import create_engine
engine = create_engine('sqlite:///sqlalchemy_example.db')
Base.metadata.bind = engine
from sqlalchemy.orm import sessionmaker
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

# Return the first Metrics from all Persons in the database
metrics = session.query(Metric).all()
for metric in metrics:
	print '-------------------'
	print metric.reponame
	print metric.branch
	print metric.username
	print metric.build_url
	print metric.status
	print metric.retry_of
	print metric.build_time_millis
	print metric.user.name
