> 江苏工匠杯

![](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251001153644034.png)

___
`waf()` 函数过滤了 `|`、`&`、`;`、`[sapce]`、`/`、`cat`、`flag`、`tac`、`php`、`ls`

shell中可以使用 `l''s` 绕过 `ls`，使用 `${IFS}` 绕过空格

或者直接用下面字符串实现任意命令执行，其中 `$payload` 为八进制或十六进制编码过后的命令串

```php
<?php
'$(printf${IFS}"'.$payload.'")'
```



___



## highlight_file()

```php
<?php
highlight_file(__FILE__);
```
highlight_file() 函数对文件进行 PHP 语法高亮显示。语法通过使用 HTML 标签进行高亮。

### 语法

```php
<?php
highlight_file(filename, return)
```

| 参数       | 描述                                                         |
| ---------- | ------------------------------------------------------------ |
| *filename* | 必需。规定要显示的文件。                                     |
| *return*   | 可选。如果该参数设置为 TRUE，该函数将以字符串形式返回高亮显示的代码，而不是直接进行输出。默认是 FALSE。 |

### 技术细节

|            |                                                              |
| ---------- | ------------------------------------------------------------ |
| 返回值：   | 如果 *return* 参数设置为 TRUE，该函数将以字符串形式返回高亮显示的代码，而不是直接进行输出。否则，如果成功则返回 TRUE，如果失败则返回 FALSE。 |
| PHP 版本： | 4+                                                           |
| 更新日志： | 自 PHP 4.2.1 起，该函数现在也受 safe_mode 和 open_basedir 影响。然而，在 PHP 5.4 中 safe_mode 被移除。      在 PHP 4.2.0 中新增了 return 参数。 |

## preg_match_all()

```php
<?php
preg_match_all("/(\||&|;| |\/|cat|flag|tac|php|ls)/", $str, $pat_array)
```
preg_match_all 函数用于执行一个全局正则表达式匹配。

### 语法

```php
<?php
int preg_match_all ( string $pattern , string $subject [, array &$matches [, int $flags = PREG_PATTERN_ORDER [, int $offset = 0 ]]] )
```

搜索 subject 中所有匹配 pattern 给定正则表达式的匹配结果并且将它们以 flag 指定顺序输出到 matches 中。

在第一个匹配找到后, 子序列继续从最后一次匹配位置搜索。

参数说明：

- $pattern: 要搜索的模式，字符串形式。
- $subject: 输入字符串。
- $matches: 多维数组，作为输出参数输出所有匹配结果, 数组排序通过flags指定。
- $flags：可以结合下面标记使用(注意不能同时使用PREG_PATTERN_ORDER和 PREG_SET_ORDER)：

```
1. PREG_PATTERN_ORDER: 结果排序为$matches[0]保存完整模式的所有匹配, $matches[1] 保存第一个子组的所有匹配，以此类推。

2. PREG_SET_ORDER: 结果排序为$matches[0]包含第一次匹配得到的所有匹配(包含子组)， $matches[1]是包含第二次匹配到的所有匹配(包含子组)的数组，以此类推。

3. PREG_OFFSET_CAPTURE: 如果这个标记被传递，每个发现的匹配返回时会增加它相对目标字符串的偏移量。
```

- offset: 通常， 查找时从目标字符串的开始位置开始。可选参数offset用于 从目标字符串中指定位置开始搜索(单位是字节)。

## in_array()
```php
<?php
in_array($this->method, array("ping"))
```
in_array() 函数搜索数组中是否存在指定的值。

### 语法

```php
<?php
bool in_array ( mixed $needle , array $haystack [, bool $strict = FALSE ] )
```

| 参数       | 描述                                                         |
| ---------- | ------------------------------------------------------------ |
| *needle*   | 必需。规定要在数组搜索的值。                                 |
| *haystack* | 必需。规定要搜索的数组。                                     |
| *strict*   | 可选。如果该参数设置为 TRUE，则 in_array() 函数检查搜索的数据与数组的值的类型是否相同。 |

### 技术细节

|            |                                                 |
| ---------- | ----------------------------------------------- |
| 返回值：   | 如果在数组中找到值则返回 TRUE，否则返回 FALSE。 |
| PHP 版本： | 4+                                              |
| 更新日志   | 自 PHP 4.2 起，search 参数可以是一个数组。      |

## call_user_func_array()
```php
<?php
call_user_func_array(array($this, $this->method), $this->args);
```
调用回调函数，并把一个数组参数作为回调函数的参数。

### 说明

```php
<?php
call_user_func_array(callable $callback, [array] $args): [mixed]
```

把第一个参数作为回调函数（`callback`）调用，把参数数组作（`args`）为回调函数的的参数传入。

### 参数

```
callback
```

被调用的回调函数。

```
args
```

要被传入回调函数的数组。
如果 `args` 的 key 都是数字，则会忽略 key，并按顺序将每个元素作为位置参数传递给 `callback` 。
如果 `args` 的任一 key 是字符串，则这些元素将作为命名参数传递给 `callback`，名称由 key 指定。
在 `args` 中，如果数字 key 在 字符串 key 之后出现，或者字符串 key 与 `callback` 的任何参数名称不匹配，将会导致 fatal error。

### 返回值

返回回调函数的结果。如果出错的话就返回 `false`

<p style="text-align: right;">
by. Spark0618
</p>
