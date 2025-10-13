首先根据页面源码提示找到 `source.php`

![屏幕截图 2025-10-05 154003](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251013092754173.png)

访问后显示页面源码如下

```php
<?php
    highlight_file(__FILE__);
    class emmm
    {
        public static function checkFile(&$page)
        {
            $whitelist = ["source"=>"source.php","hint"=>"hint.php"];
            if (! isset($page) || !is_string($page)) {
                echo "you can't see it";
                return false;
            }

            if (in_array($page, $whitelist)) {
                return true;
            }

            $_page = mb_substr(
                $page,
                0,
                mb_strpos($page . '?', '?')
            );
            if (in_array($_page, $whitelist)) {
                return true;
            }

            $_page = urldecode($page);
            $_page = mb_substr(
                $_page,
                0,
                mb_strpos($_page . '?', '?')
            );
            if (in_array($_page, $whitelist)) {
                return true;
            }
            echo "you can't see it";
            return false;
        }
    }

    if (! empty($_REQUEST['file'])
        && is_string($_REQUEST['file'])
        && emmm::checkFile($_REQUEST['file'])
    ) {
        include $_REQUEST['file'];
        exit;
    } else {
        echo "<br><img src=\"https://i.loli.net/2018/11/01/5bdb0d93dc794.jpg\" />";
    }  
?>
```

`$_REQUEST['file']` 默认包含了 `$_GET`、`$_POST` 和 `$_COOKIE` 的内容

最后是要绕过过滤执行 `include $_REQUEST['file'];`

源码使用了白名单过滤

```php
<?php
$whitelist = ["source"=>"source.php","hint"=>"hint.php"];
if (! isset($page) || !is_string($page)) {
    echo "you can't see it";
    return false;
}

if (in_array($page, $whitelist)) {
    return true;
}
```

看到有 `hint.php`，访问得到hint，猜测flag文件名为 `ffffllllaaaagggg`

```
flag not here, and flag in ffffllllaaaagggg
```

整个过滤要求传参为字符串（存储在 `$page` 中），满足以下任意条件即可通过：

1. `$page == "source.php"` 或 `"hint.php"`

2. `$page` 以 `source.php?` 或 `hint.php?` 开头

3. `urldecode($page)` 以 `source.php?` 或 `hint.php?` 开头

因此 `payload` 如下（工作目录下没找到，依次往上级目录查找，最终在根目录下找到）

??? note inline end

    为什么 `../../../` 抵达的是根目录？
    
    因为web服务的工作目录一般位于/var/www/html/

```
file=source.php?/../../../../ffffllllaaaagggg
```

其中 `include` 在linux下会将 `source.php?` 视为一个目录（因为linux下目录命名可含 `'?'`，但windows下不行，所以无法在windows下复现，因为 `include` 底层调用的是操作系统api来检查文件存在性的），`source.php?/../` 等效于 `./` 

注意，这是 `include` 的路径规约（clear/normalize）特性，详见 [include路径解析]([Article] php_include_path_analysis.md)，而你如果在shell中访问 `source.php?/../` 这样一段路径，操作系统会先检查 `source.php?` 目录是否存在，若不存在会直接报错

___



<p style="text-align: right;">
by. Spark0618
</p>
