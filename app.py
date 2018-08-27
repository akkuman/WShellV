# coding: utf-8

import bottle
import bottle.ext.sqlite
import sqlite3
import os
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

'''获取指定id的shell的文件列表
POST /getflielist
data = {
    url=
    pwd=
    plugin=
    method=
    path=
}
'''
@app.route("/getfilelist", method="POST")
def getfilelist():
    url = bottle.request.forms.get('url')
    pwd = bottle.request.forms.get('pwd')
    plugin = bottle.request.forms.get('plugin')
    method = bottle.request.forms.get('method')
    path = bottle.request.forms.get('path')
    shell = Shell(url, pwd, plugin, method)
    info = {
        'sysinfo': shell.get_sys_info(),
        'filelist': shell.get_dir(path),
    }
    return info


'''上传文件到指定id的shell指定文件夹下
POST /uploadfile
data = {
    shellid=
    file=
    path=
}
'''
@app.route("/uploadfile", method="POST")
def uploadfile():
    id = bottle.request.forms.get('shellid')
    path = bottle.request.forms.get('path')
    formfile = bottle.request.files.get('file')
    formfile.save('./upload', overwrite=True)
    shellinfo = get_shell_from_id(id)
    shell = Shell(shellinfo['url'], shellinfo['pwd'], shellinfo['plugin'], shellinfo['method'])
    info = shell.upload_file('./upload/%s'%formfile.filename, path)
    os.remove('./upload/%s'%formfile.filename)
    return info


'''删除指定id的shell指定文件夹下的文件
POST /delfile
data = {
    shellid=
    filename=
    path=
}
'''
@app.route("/delfile", method="POST")
def delfile():
    id = bottle.request.forms.get('shellid')
    filename = bottle.request.forms.get('filename')
    path = bottle.request.forms.get('path')
    shellinfo = get_shell_from_id(id)
    shell = Shell(shellinfo['url'], shellinfo['pwd'], shellinfo['plugin'], shellinfo['method'])
    return shell.del_file(filename, path)


'''在指定id的shell指定文件夹下创建新文件夹
POST /createfolder
data = {
    shellid=
    foldername=
    path=
}
'''
@app.route("/createfolder", method="POST")
def createfolder():
    id = bottle.request.forms.get('shellid')
    foldername = bottle.request.forms.get('foldername')
    path = bottle.request.forms.get('path')
    shellinfo = get_shell_from_id(id)
    shell = Shell(shellinfo['url'], shellinfo['pwd'], shellinfo['plugin'], shellinfo['method'])
    return shell.mkdir(foldername, path)


'''在指定id的shell指定文件夹下执行命令
POST /createfolder
data = {
    shellid=
    command=
    path=
}
'''
@app.route("/command", method="POST")
def command():
    id = bottle.request.forms.get('shellid')
    cmd = bottle.request.forms.get('command')
    path = bottle.request.forms.get('path')
    shellinfo = get_shell_from_id(id)
    shell = Shell(shellinfo['url'], shellinfo['pwd'], shellinfo['plugin'], shellinfo['method'])
    return shell.execute_command(cmd, path)


'''获取插件列表
GET /getpluginlist
'''
@app.route("/getpluginlist")
def getpluginlist():
    plugin_list = [os.path.splitext(i)[0] for i in os.listdir('./plugins') if i != '__init__.py']
    return {'plugins': plugin_list}

@app.get("/")
def home():
    return bottle.static_file('index.html',root='./')


@app.get("/static/<path>/<filename>")
def static(path, filename):
    pathroot = './static/%s/' % path
    return  bottle.static_file(filename, root=pathroot)


def get_shell_from_id(id):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    cursor = c.execute('SELECT id, url, pwd, plugin, method FROM SHELL WHERE id=%s' % id)
    row = cursor.fetchone()
    shell_info = {}
    shell_info["id"] = row[0]
    shell_info["url"] = row[1]
    shell_info["pwd"] = row[2]
    shell_info["plugin"] = row[3]
    shell_info["method"] = row[4]
    conn.close()
    return shell_info

app.run(host="0.0.0.0",port=8080,debug=True)