from flask import Flask, jsonify, request, redirect
from flask_pymongo import PyMongo
from flask_cors import CORS
import jwt
import time

app = Flask(__name__)
MONGODBHOST = "mongodb://dongkirk:Python1112@207.246.123.115:27017/IdleFish"
mongo = PyMongo(app, uri=MONGODBHOST)
jwtsecret = "xianyuzhiding"

CORS(app, supports_credentials=True)

# baseurl="/api1"
baseurl = ""

# 拦截器
@app.before_request
def before_action():
    if request.path in [baseurl + "/login" ,baseurl + "/squery",baseurl +'/gethomeInfo']:
        return
    # print("拦截器",request.cookies)
    token = request.cookies.get("token")
    # print("token:",token)
    try:
        usertokenInfo = jwt.decode(token, jwtsecret, algorithms=['HS256'])
        ctime = usertokenInfo.get("ctime")
        expires = usertokenInfo.get("expires")
        # print("离身份过期的秒数:",int(expires)-int(time.time()-ctime))
        if int(time.time() - ctime) > int(expires):
            # print("身份信息过期")
            return jsonify(
                {
                    'status': 1,
                    'msg': "身份信息已过期"
                }
            )
    except Exception as e:
        print(e)
        return jsonify(
            {
                'status': 1,
                'msg': "请重新登陆"
            }
        )


# 登录验证
@app.route(baseurl + '/login', methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "status": 1,
            "msg": "请求失败"
        })
    loginname = data.get("loginname")
    password = data.get("password")
    if loginname == "dongkirk" and password == "githubisNo.1":
        token = jwt.encode({'loginname': loginname, "ctime": int(time.time()), 'expires': 60 * 60 * 24 * 7}, jwtsecret,
                           algorithm='HS256')
        # print(token)
        return jsonify({
            "status": 0,
            "msg": "登陆成功",
            "token": token.decode()
        })
    else:
        return jsonify({
            "status": 1,
            "msg": "用户名密码错误"
        })


@app.route(baseurl + '/add', methods=["POST"])
def addData():
    try:
        data = request.get_json(silent=True)
        set = mongo.db.topInfo
        ticketNo = int(time.time() * 100)
        data["ticketNo"] = ticketNo
        set.insert(data)

        return jsonify({
            "status": 0,
            "msg": "操作成功",
        })
    except Exception as e:
        print(e)
        return jsonify({
            "status": 1,
            "msg": "添加失败",
        })


@app.route(baseurl + '/query')
def query():
    try:
        set = mongo.db.topInfo
        qres = set.find()
        data = []
        for i in qres:
            i['_id'] = str(i['_id'])
            data.append(i)
        return jsonify({
            "status": 0,
            "data": data
        })
    except Exception as e:
        print(e)
        return jsonify({
            "status": 1,
            "msg": "查询失败",
        })


@app.route(baseurl + '/modify', methods=["POST"])
def modify():
    try:
        data = request.get_json(silent=True)
        ticketNo = data.get("ticketNo")
        set = mongo.db.topInfo
        obj = set.find_one({'ticketNo': ticketNo})
        for k, v in data.items():
            if k == "_id":
                continue
            obj[k] = v
        set.update({'ticketNo': ticketNo}, obj)
        return jsonify({
            "status": 0,
            "msg": "修改成功"
        })
    except Exception as e:
        print(e)
        return jsonify({
            "status": 1,
            "msg": "修改失败",
        })


@app.route(baseurl + '/delete', methods=["POST"])
def deleteInfo():
    try:
        data = request.get_json(silent=True)
        ticketNo = data.get("id")
        if not ticketNo:
            raise Exception("id不存在")
        set = mongo.db.topInfo
        set.delete_one({'ticketNo': ticketNo})
        return jsonify({
            "status": 0,
            "msg": "删除成功"
        })
    except Exception as e:
        print(e)
        return jsonify({
            "status": 1,
            "msg": "删除失败",
        })


@app.route(baseurl + '/squery')
def singleQuery():
    try:
        param = request.args
        name = param.get("name")
        if not name:
            raise Exception("id不存在")
        set = mongo.db.topInfo
        data = []
        for x in set.find({"name": name}, {"_id": 0, "name": 1, "stime": 1, "etime": 1}):
            data.append(x)
        return jsonify({
            "status": 0,
            "data": data
        })
    except Exception as e:
        print(e)
        return jsonify({
            "status": 1,
            "msg": "查询失败",
        })


@app.route(baseurl + '/addhomeInfo',methods=["POST"])
def homeInfo():
    try:
        data = request.get_json(silent=True)
        set = mongo.db.homeInfo
        set.remove({'name': "infos"})
        set.insert(data)
        return jsonify({
            "status": 0,
            "msg": "操作成功"
        })
    except Exception as e:
        print(e)
        return jsonify({
            "status": 1,
            "msg": "操作失败",
        })

@app.route(baseurl + '/gethomeInfo')
def gethomeInfo():
    try:
        set = mongo.db.homeInfo
        result = set.find({'name': "infos"},{"_id": 0})
        data=""
        for x in result:
            data =x
        return jsonify({
            "status": 0,
            "data":data,
        })
    except Exception as e:
        print(e)
        return jsonify({
            "status": 1,
            "msg": "操作失败",
        })


if __name__ == '__main__':
    app.run()
