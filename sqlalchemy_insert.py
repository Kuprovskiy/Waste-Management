import urllib3
import requests
import json
import sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_declarative import Base, Metric, User, MetricSchema
from datetime import datetime

metric_schema = MetricSchema()
metric_schema = MetricSchema(many=True)

engine = create_engine('sqlite:///sqlalchemy_example.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()
 
# urllib3.disable_warnings()
url = 'http://circleci.com/api/v1.1/recent-builds?circle-token=99de86208b9f8a6cd52e1a8e0534b7dc8c45862a'
payload = open("/home/user/apps/flask/request.json")
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
r = requests.get(url, data=payload, headers=headers)
data = r.json()

for build in data:
	# session.query(User).all()
	new_user = session.query(User).filter(User.name == build['username']).first()
	if not new_user:
		new_user = User(name=build['username'])
		session.commit()
		session.add(new_user)

	# if not build['status'] == 'running' or not build['status'] == 'queued':
	if build['status'] == 'failed' or build['status'] == 'no_tests' or build['status'] == 'success' or build['status'] == 'fixed' or build['status'] == 'timedout':
		metric = session.query(Metric).filter(Metric.build_url == build['build_url']).first()
		if not metric:
			merged_to_master = True if build['all_commit_details'] and len(build['all_commit_details']) > 1 else False
			related_branch = build['branch']
			if build['all_commit_details'] and len(build['all_commit_details']) > 1:
				# print build['all_commit_details'][0]['commit']
				prev_revisions = session.query(Metric).filter(Metric.vcs_revision == build['all_commit_details'][0]['commit']).all()
				prev_revision = metric_schema.dump(prev_revisions)
				if prev_revision.data and len(prev_revision.data) > 0:
					# print prev_revision.data[0]['branch']
					related_branch = prev_revision.data[0]['branch']
			new_metric = Metric(reponame=build['reponame'], branch=build['branch'], username=build['username'], build_url=build['build_url'], status=build['status'], retry_of=build['retry_of'], build_time_millis=build['build_time_millis'], vcs_revision=build['vcs_revision'], vcs_tag=build['vcs_tag'], merged_to_master=merged_to_master, related_branch=related_branch, user=new_user)
			session.add(new_metric)
			session.commit()

# statuses :retried, :canceled, :infrastructure_fail, :timedout, :not_run, :running, :failed, :queued, :scheduled, :not_running, :no_tests, :fixed, :success