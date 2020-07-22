from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import pymongo, datetime

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = b'#3/\xd5\x05\xbb\xe4$;\xc1\xf5XO\x00+\xdb'
app.config['MONGO_URI'] = "mongodb://localhost:27017/Todo_apps"
mongo = PyMongo(app)

# MONGODB CHEATSHEET:
	# use/create db: use namadb
	# create collection/table: db.createCollection("user")
	# delete collection/table: db.user.drop()
	# add unique to attribute: db.user.createIndex({"username":1},{unique:true})
	# insert: mongo.db.user.insert({'name':'setya',"username":'MasTya',"password":"IniMasTya"})
	# update: mongo.db.user.update({'_id':ObjectId(str(id_user))},{'$set':{'name':"Setyawan",'password':"IniPasswordMasTya"}})
	# delete: mongo.db.user.remove({'_id':ObjectId(str(id_user))})
	# query: mongo.db.user.find()
	# query with where: mongo.db.user.find({'_id':ObjectId(str(id_user))})
	# join: mongo.db.todo.aggregate([{"$lookup":{"from":"user", "localField":"id_user", "foreignField":"_id", "as":"user"}}])
	# join with where: mongo.db.todo.aggregate([{'$lookup':{"from":"user","localField":"id_user","foreignField":"_id","as":"user"}},{"$match":{"_id":ObjectId(str(args['id_todo']))}}])

class resource_user(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_user',type=str,help='id_user, Must STR')
		args = parser.parse_args()
		if args['id_user'] is None:
			data_user = []
			query_user = mongo.db.user.find()
			for i in query_user:
				data = {"_id":str(i['_id']),
					"name":i['name'],
					'username':i['username'],
					'password':i['password']
				}
				data_user.append(data)
			return jsonify({"status":"success","result":data_user})
		else:
			query_user = mongo.db.user.find_one({'_id':ObjectId(str(args['id_user']))})
			if query_user is None:
				return jsonify({"status":"error","message":"User Does Not Exist"})
			else:
				data_user = {
					'_id':str(query_user['_id']),
					'name':query_user['name'],
					'username':query_user['username'],
					'password':query_user['password']
				}
				return jsonify({"status":"success","result":data_user})

	def post(self):
		try:
			data = request.json
			name = str(data['name'])
			username = str(data['username'])
			password = str(data['password'])

			create_user = mongo.db.user.insert({'name':name,"username":username,"password":password})
			return jsonify({"status":"success","message":"User Created"})

		except pymongo.errors.DuplicateKeyError as e:
			return jsonify({"status":"error",'message':str(e)})
		except KeyError:
			return jsonify({"status":"error","message":"data invalid"})

	def put(self):
		try:
			data = request.json
			id_user = str(data['id_user'])
			name = str(data['name'])
			password = str(data['password'])

			user = mongo.db.user.update({'_id':id_user},{'$set':{'name':name,'password':password}})

			return jsonify({"status":"success",'message':"Updated"})
		except KeyError:
			return jsonify({"status":"error","message":"data invalid"})

	def delete(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_user',type=str,required=True,help="id_user, Must STR, Required")
		args = parser.parse_args()

		user = mongo.db.user.remove({'_id':args['id_user']})
		return jsonify({"status":"success","message":"User Deleted"})

class resource_todo(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_user',type=str,help="id_user, STR")
		args = parser.parse_args()
		if args['id_user'] is None:
			todo_data = []
			get_data = mongo.db.todo.aggregate([{"$lookup":{"from":"user", "localField":"id_user", "foreignField":"_id", "as":"user"}}])
			for i in get_data:
				data = {}
				data['_id'] = str(i['_id'])
				data['id_user'] = str(i['id_user'])
				data['note'] = i['note']
				data['deadline'] = i['deadline']
				data['complete_mark'] = i['complete_mark']
				data_user = []
				for j in i['user']:
					user = {'_id':str(j['_id']),"name":j['name'],'username':j['username'],'password':j['password']}
					data_user.append(user)
				data['user'] = data_user
				todo_data.append(data)
			return jsonify({"status":"success",'result':todo_data})
		else:
			get_user = mongo.db.user.find_one({"_id":ObjectId(str(args['id_user']))})
			if get_user is not None:
				get_todo = mongo.db.todo.find({"id_user":ObjectId(str(args['id_user']))})
				result = {}
				result['_id'] = str(get_user['_id'])
				result['name'] = get_user['name']
				result['username'] = get_user['username']
				result['password'] = get_user['password']
				data_todo = []
				for i in get_todo:
					data = {}
					data['_id'] = str(i['_id'])
					data['id_user'] = str(i['id_user'])
					data['note'] = i['note']
					data['deadline'] = i['deadline']
					data['complete_mark'] = i['complete_mark']
					data_todo.append(data)
				result['todo'] = data_todo

				return jsonify({"status":"success","result":result})
			else:
				return jsonify({"status":"error","message":"user not found"})

	def post(self):
		try:
			data = request.json
			id_user =  str(data['id_user'])
			note = str(data['note'])
			deadline = datetime.datetime.strptime(data['deadline'],"%Y-%m-%d %H:%M:%S")
			complete_mark = False

			todo = mongo.db.todo.insert({"id_user":ObjectId(id_user),"note":note,"deadline":deadline,"complete_mark":complete_mark})

			return jsonify({"status":"success","message":"Todo Created"})

		except ValueError:
			return jsonify({"status":"error","message":"format error"})
		except KeyError:
			return jsonify({"status":"error","message":"data invalid"})

	def put(self):
		try:
			data = request.json
			id_todo = str(data['id_todo'])
			note = str(data['note'])
			deadline = datetime.datetime.strptime(data['deadline'],"%Y-%m-%d %H:%M:%S")
			
			todo = mongo.db.todo.update({"_id":ObjectId(id_todo)},{"$set" : {"note":note,"deadline":deadline}})

			return jsonify({"status":"success","message":"Todo Updated"})

		except ValueError:
			return jsonify({"status":"error","message":"format error"})
		except KeyError:
			return jsonify({"status":"error","message":"data invalid"})

	def delete(self):
		parser = reqparse.RequestParser()
		parser.add_argument('id_todo',type=str,required=True,help="id_todo, must str, required")
		args = parser.parse_args()

		todo = mongo.db.todo.remove({"_id":ObjectId(str(args['id_todo']))})

		return jsonify({"status":"success","message":"Todo Deleted"})

class resource_todo_detail(Resource):
	def get(self):
		parser = reqparse.RequestParser()
		parser.add_argument("id_todo",type=str,required=True,help='id_todo, must STR, required')
		args = parser.parse_args()

		todos = mongo.db.todo.aggregate([{'$lookup':{"from":"user","localField":"id_user","foreignField":"_id","as":"user"}},{"$match":{"_id":ObjectId(str(args['id_todo']))}}])
		todo_data = {}
		for i in todos:
			todo_data['_id'] = str(i['_id'])
			todo_data['id_user'] = str(i['id_user'])
			todo_data['note'] = i['note']
			todo_data['deadline'] = i['deadline']
			todo_data['complete_mark'] = i['complete_mark']
			data_user = []
			for j in i['user']:
				user = {'_id':str(j['_id']),"name":j['name'],'username':j['username'],'password':j['password']}
				data_user.append(user)
			todo_data['user'] = data_user
		return jsonify({"status":"success",'result':todo_data})

class resource_mark(Resource):
	def put(self):
		parser = reqparse.RequestParser()
		parser.add_argument("id_todo",type=str,required=True,help='id_todo, must STR, required')
		args = parser.parse_args()

		todo = mongo.db.todo.update({"_id":ObjectId(str(args['id_todo']))},{'$set':{'complete_mark':True}})

		return jsonify({"status":"success","message":"Mark As Complete"})

api.add_resource(resource_user, '/api/user/')
api.add_resource(resource_todo, '/api/todo/')
api.add_resource(resource_todo_detail, '/api/todo-detail/')
api.add_resource(resource_mark, '/api/mark-todo/')


if __name__ == '__main__':
	app.run(debug=True, port=5001)