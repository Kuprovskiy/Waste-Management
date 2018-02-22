#!flask/bin/python
from flask import Flask, make_response, jsonify
from sqlalchemy_declarative import Metric, Base, User, MetricSchema, UserSchema, ProjectSchema, BranchSchema
from sqlalchemy import create_engine, func
from flask_cors import CORS
engine = create_engine('sqlite:///sqlalchemy_example.db')
Base.metadata.bind = engine
from sqlalchemy.orm import sessionmaker
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

app=Flask(__name__)

project_schema = ProjectSchema()
project_schema = ProjectSchema(many=True)

branchSchema = BranchSchema()
branchSchema = BranchSchema(many=True)

metric_schema = MetricSchema()
metric_schema = MetricSchema(many=True)

user_schema = UserSchema()
user_schema = UserSchema(many=True)

CORS(app)

@app.route('/api', methods=['GET'])
def index():
    return "Hello, World!"

# endpoint to get all metrics
@app.route('/api/metrics', methods = ['GET'])
def metrics():
    all_metrics = session.query(Metric).all()
    result = metric_schema.dump(all_metrics)
    return jsonify(result.data)

# endpoint to get metrics by user id
@app.route('/api/users/<id>/metrics', methods = ['GET'])
def user_metrics(id):
    all_metrics = session.query(Metric).filter(Metric.user_id == id).all()
    result = metric_schema.dump(all_metrics)
    return jsonify(result.data)

# endpoint to get user statistic
@app.route('/api/users/<id>/projects/<name>', methods = ['GET'])
def user_statistic(id, name):
    all_metrics = session.query(Metric).filter(Metric.user_id == id, Metric.reponame == name).all()
    result = metric_schema.dump(all_metrics)
    return jsonify(result.data)

# endpoint to get user statistic
@app.route('/api/users/<id>/projects/<name>/statistic', methods = ['GET'])
def user_statistic_by_project(id, name):
    all_metrics = session.query(Metric).filter(Metric.user_id == id, Metric.reponame == name).all()
    result = metric_schema.dump(all_metrics)
    return jsonify(
    	{
    		'builds': {
	    		'success': sum(x['status'] == 'success' or x['status'] == 'fixed' for x in result.data),
	    		'failed': sum(x['status'] == 'failed' or x['status'] == 'no_tests' for x in result.data),
	    		'master_after_merge': {
	    			'success': sum(x['branch'] == 'master' and x['merged_to_master'] and (x['status'] == 'success' or x['status'] == 'fixed') for x in result.data),
	    			'failed': sum(x['branch'] == 'master' and x['merged_to_master'] and (x['status'] == 'failed' or x['status'] == 'no_tests') for x in result.data)
	    		}
	    	},
	    	'last_activity': '1 day ago',
	    	'data': result.data
    	})

# endpoint to get user statistic
@app.route('/api/users/<id>/projects/<name>/<feature>/statistic', methods = ['GET'])
def user_statistic_by_project_and_feature(id, name, feature):
    all_metrics = session.query(Metric).filter(Metric.user_id == id, Metric.reponame == name, Metric.related_branch == feature).all()
    result = metric_schema.dump(all_metrics)
    return jsonify(
    	{
    		'builds': {
	    		'success': sum(x['status'] == 'success' or x['status'] == 'fixed' for x in result.data),
	    		'failed': sum(x['status'] == 'failed' or x['status'] == 'no_tests' for x in result.data),
	    		'master_after_merge': {
	    			'success': sum(x['branch'] == 'master' and x['merged_to_master'] and (x['status'] == 'success' or x['status'] == 'fixed') for x in result.data),
	    			'failed': sum(x['branch'] == 'master' and x['merged_to_master'] and (x['status'] == 'failed' or x['status'] == 'no_tests') for x in result.data)
	    		}
	    	},
	    	'last_activity': '1 day ago',
	    	'data': result.data
    	})

# endpoint to get projects assigned to user 
@app.route('/api/users/<id>/projects', methods = ['GET'])
def user_projects(id):
	# session.query(Table.column, func.count(Table.column)).group_by(Table.column).all()
    all_metrics = session.query(func.count(Metric.reponame), Metric.reponame, Metric.username).group_by(Metric.reponame, Metric.username).filter(Metric.user_id == id).all()
    result = project_schema.dump(all_metrics)
    return jsonify({'projects': result.data})

# endpoint to get projects assigned to user 
@app.route('/api/users/<id>/projects/<name>/branches', methods = ['GET'])
def user_project_branches(id, name):
	# session.query(Table.column, func.count(Table.column)).group_by(Table.column).all()
    all_metrics = session.query(func.count(Metric.branch), Metric.branch, Metric.reponame).group_by(Metric.branch, Metric.reponame).filter(Metric.user_id == id, Metric.reponame == name).all()
    result = branchSchema.dump(all_metrics)
    return jsonify({'branches': result.data})

# endpoint to get all users
@app.route('/api/users', methods = ['GET'])
def users():
    all_users = session.query(User).all()
    result = user_schema.dump(all_users)
    return jsonify(result.data)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.run(debug=True)
