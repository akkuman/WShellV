# coding: utf-8

import bottle
import bottle.ext.sqlite
from Shell import Shell

app = bottle.Bottle()
plugin = bottle.ext.sqlite.Plugin(dbfile="./data.db")
app.install(plugin)


'''增加某个shell
POST /addshell
data = {
    url=
    pwd=
    plugin=
    method=
}
'''
@app.route("/addshell", method='POST')
def addshell(db):
    url = bottle.request.forms.get('url')
    pwd = bottle.request.forms.get('pwd')
    plugin = bottle.request.forms.get('plugin')
    method = bottle.request.forms.get('method')
    sql = 'INSERT INTO shell (url, pwd, plugin, method) VALUES ("%s", "%s", "%s", "%s");' % (url, pwd, plugin, method)
    db.execute(sql)


'''删除某个shell
POST /delshell
data = {
    id=
}
'''
@app.route("/delshell", method='POST')
def delshell(db):
    id = bottle.request.forms.get('id')
    sql = "DELETE from SHELL where id=%s;" % id
    db.execute(sql)


'''更新某个shell
POST /updateshell
data = {
    id =
    url =
    pwd =
    plugin =
    method =
}
'''
@app.route("/updateshell", method='POST')
def updateshell(db):
    id = bottle.request.forms.get('id')
    url = bottle.request.forms.get('url')
    pwd = bottle.request.forms.get('pwd')
    plugin = bottle.request.forms.get('plugin')
    method = bottle.request.forms.get('method')
    sql = 'UPDATE SHELL SET url = "%s", pwd = "%s", plugin = "%s", method = "%s" WHERE id=%s;' % (url, pwd, plugin, method, id)
    db.execute(sql)


'''查询某个shell的信息
POST /selectshell
data = {
    id =
}
'''
@app.route("/selectshell", method='POST')
def selectshell(db):
    id = bottle.request.forms.get('id')
    sql = 'SELECT id, url, pwd, plugin, method FROM SHELL WHERE id=%s' % id
    row = db.execute(sql)
    shell_info = {}
    shell_info["id"] = row[0]
    shell_info["url"] = row[1]
    shell_info["pwd"] = row[2]
    shell_info["plugin"] = row[3]
    shell_info["method"] = row[4]
    return shell_info


'''查询数据库所有的shell
GET /showshells
'''
@app.route("/showshells")
def showshells(db):
    sql = "SELECT id, url, pwd, plugin, method FROM SHELL;"
    rows = db.execute(sql)
    shell_list = []
    for row in rows:
        shell_info = {}
        shell_info["id"] = row[0]
        shell_info["url"] = row[1]
        shell_info["pwd"] = row[2]
        shell_info["plugin"] = row[3]
        shell_info["method"] = row[4]
        shell_list.append(shell_info)
    print(shell_list)
    allshell = {}
    allshell["shelllist"] = shell_list
    return allshell



@app.get("/")
def home():
    return "hello"


app.run(host="0.0.0.0",port=8080,debug=True)