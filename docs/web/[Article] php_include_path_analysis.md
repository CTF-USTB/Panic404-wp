# php include 路径解析

PHP是一种解释型语言，先通过编译函数 `zend_compile_file()` 进行词法分析和语法分析，得到指令码（opcode），然后交由 `Zend` 虚拟机调用 `zend_execute()` 执行指令。

对于下面的php代码

```php
<?php
include("source/../file.php");
?>
```

zend引擎会首先将源码转为中间代码如下，这一转化过程可通过 `vld` 插件实现

```shell
line      #* E I O op                               fetch          ext  return  operands
-----------------------------------------------------------------------------------------
    4     0  E >   EXT_STMT                                                     
          1        INCLUDE_OR_EVAL                                              'source%2F..%2Ffile.php', INCLUDE
    5     2      > RETURN                                                       1
```

## 调用栈分析

`include` 被转化为opcode `ZEND_INCLUDE_OR_EVAL` ，通过跟踪[php内核代码](https://github.com/php/php-src)（php8.x），发现该操作码的处理函数为 `ZEND_INCLUDE_OR_EVAL_SPEC_CONST_HANDLER()` (Zend/zend_vm_execute.h)，其中调用 `zend_include_or_eval()` 函数（Zend/zend_execute.c），注意到代码中通过一个 `switch` 区分了 `include_once` 、 `require_once`、`include`、`require` 和 `eval`，意味着这几个函数其实都会调用这个函数

```c
static zend_never_inline zend_op_array* ZEND_FASTCALL zend_include_or_eval(zval *inc_filename_zv, int type) 
{
	zend_op_array *new_op_array = NULL;
	zend_string *tmp_inc_filename;
	zend_string *inc_filename = zval_try_get_tmp_string(inc_filename_zv, &tmp_inc_filename);
	if (UNEXPECTED(!inc_filename)) {
		return NULL;
	}

	switch (type) {
		case ZEND_INCLUDE_ONCE:
		case ZEND_REQUIRE_ONCE: {
				zend_file_handle file_handle;
				zend_string *resolved_path;

				resolved_path = zend_resolve_path(inc_filename);
				if (EXPECTED(resolved_path)) {
					if (zend_hash_exists(&EG(included_files), resolved_path)) {
						new_op_array = ZEND_FAKE_OP_ARRAY;
						zend_string_release_ex(resolved_path, 0);
						break;
					}
				} else if (UNEXPECTED(EG(exception))) {
					break;
				} else if (UNEXPECTED(zend_str_has_nul_byte(inc_filename))) {
					zend_message_dispatcher(
						(type == ZEND_INCLUDE_ONCE) ?
							ZMSG_FAILED_INCLUDE_FOPEN : ZMSG_FAILED_REQUIRE_FOPEN,
							ZSTR_VAL(inc_filename));
					break;
				} else {
					resolved_path = zend_string_copy(inc_filename);
				}

				zend_stream_init_filename_ex(&file_handle, resolved_path);
				if (SUCCESS == zend_stream_open(&file_handle)) {

					if (!file_handle.opened_path) {
						file_handle.opened_path = zend_string_copy(resolved_path);
					}

					if (zend_hash_add_empty_element(&EG(included_files), file_handle.opened_path)) {
						new_op_array = zend_compile_file(&file_handle, (type==ZEND_INCLUDE_ONCE?ZEND_INCLUDE:ZEND_REQUIRE));
					} else {
						new_op_array = ZEND_FAKE_OP_ARRAY;
					}
				} else if (!EG(exception)) {
					zend_message_dispatcher(
						(type == ZEND_INCLUDE_ONCE) ?
							ZMSG_FAILED_INCLUDE_FOPEN : ZMSG_FAILED_REQUIRE_FOPEN,
							ZSTR_VAL(inc_filename));
				}
				zend_destroy_file_handle(&file_handle);
				zend_string_release_ex(resolved_path, 0);
			}
			break;
		case ZEND_INCLUDE:
		case ZEND_REQUIRE:
			if (UNEXPECTED(zend_str_has_nul_byte(inc_filename))) {
				zend_message_dispatcher(
					(type == ZEND_INCLUDE) ?
						ZMSG_FAILED_INCLUDE_FOPEN : ZMSG_FAILED_REQUIRE_FOPEN,
						ZSTR_VAL(inc_filename));
				break;
			}
			new_op_array = compile_filename(type, inc_filename);
			break;
		case ZEND_EVAL: {
				char *eval_desc = zend_make_compiled_string_description("eval()'d code");
				new_op_array = zend_compile_string(inc_filename, eval_desc, ZEND_COMPILE_POSITION_AFTER_OPEN_TAG);
				efree(eval_desc);
			}
			break;
		EMPTY_SWITCH_DEFAULT_CASE()
	}

	zend_tmp_string_release(tmp_inc_filename);
	return new_op_array;
}
```

重点关注 `ZEND_INCLUDE` 部分

```c
if (UNEXPECTED(zend_str_has_nul_byte(inc_filename))) {
    zend_message_dispatcher(
        (type == ZEND_INCLUDE) ?
        ZMSG_FAILED_INCLUDE_FOPEN : ZMSG_FAILED_REQUIRE_FOPEN,
        ZSTR_VAL(inc_filename));
    break;
}
new_op_array = compile_filename(type, inc_filename);
```

前面的if语句是**安全检查**，专门用于防止路径字符串中包含 **NUL 字节 (`\0`)**，然后调用 `compile_filename()` （Zend/zend_language_scanner.l），原型如下

```c
zend_op_array *compile_filename(int type, zend_string *filename)
{
	zend_file_handle file_handle;
	zend_op_array *retval;
	zend_string *opened_path = NULL; //保存文件的真实路径

	zend_stream_init_filename_ex(&file_handle, filename);

	retval = zend_compile_file(&file_handle, type);
    // 如果编译成功且文件句柄有效
	if (retval && file_handle.handle.stream.handle) {
		if (!file_handle.opened_path) {
			file_handle.opened_path = opened_path = zend_string_copy(filename);
		}
		
        // 把这个文件加入“已包含文件”全局表
		zend_hash_add_empty_element(&EG(included_files), file_handle.opened_path);

        // 释放本地临时路径字符串，防止内存泄漏
		if (opened_path) {
			zend_string_release_ex(opened_path, 0);
		}
	}
    // 销毁文件句柄
	zend_destroy_file_handle(&file_handle);

	return retval;
}
```

然后在 `zend_compile_file()` 中对文件句柄中的文件路径进行解析，调用栈如下

```c
zend_compile_file()
    | // 赋值发生在 Zend/zend.c
    └─> compile_file() // Zend/zend_language_scanner.l
    		└─> open_file_for_scanning() // Zend/zend_language_scanner.l
    				└─> zend_stream_fixup() // Zend/zend_stream.c
    						└─> zend_stream_open() // Zend/zend_stream.c
    								└─> zend_fopen() // Zend/zend.h
    										| // 赋值发生在 main/main.c
    										└─> php_fopen_wrapper_for_zend() // main/main.c
    												└─> _php_stream_open_wrapper_as_file() // main/streams/php_stream_plain_wrapper.h
    														└─> _php_stream_open_wrapper_ex() // main/php_streams.h
																	└─> php_resolve_path() // main/streams/fopen_wrappers.c
```

接着大概就是

```c
php_resolve_path()
    ↓
tsrm_realpath_str()
    ↓
tsrm_realpath()
    ↓
virtual_file_ex() // Resolve path relatively to state and put the real path into state
    ↓
tsrm_realpath_r()
```

`tsrm_realpath_r()` 函数原型为

```c
static size_t tsrm_realpath_r(char *path, size_t start, size_t len, int *ll, time_t *t, int use_realpath, bool is_dir, int *link_is_dir)
```

返回值为路径长度，关键代码如下

```c
while (1) {
		if (len <= start) {
			if (link_is_dir) {
				*link_is_dir = 1;
			}
			return start;
		}

		i = len;
    	// 移动 i 到路径最末尾的 '/' 的后一个字符
		while (i > start && !IS_SLASH(path[i-1])) {
			i--;
		}
		assert(i < MAXPATHLEN);

		if (i == len ||
			(i + 1 == len && path[i] == '.')) {
			/* remove double slashes and '.' */
			len = EXPECTED(i > 0) ? i - 1 : 0;
			is_dir = true;
			continue;
		} else if (i + 2 == len && path[i] == '.' && path[i+1] == '.') {
			/* remove '..' and previous directory */
			is_dir = true;
			if (link_is_dir) {
				*link_is_dir = 1;
			}
			if (i <= start + 1) {
				return start ? start : len;
			}
			j = tsrm_realpath_r(path, start, i-1, ll, t, use_realpath, true, NULL);
			if (j > start && j != (size_t)-1) {
				j--;
				assert(i < MAXPATHLEN);
				while (j > start && !IS_SLASH(path[j])) {
					j--;
				}
				assert(i < MAXPATHLEN);
				if (!start) {
					/* leading '..' must not be removed in case of relative path */
					if (j == 0 && path[0] == '.' && path[1] == '.' &&
							IS_SLASH(path[2])) {
						path[3] = '.';
						path[4] = '.';
						path[5] = DEFAULT_SLASH;
						j = 5;
					} else if (j > 0 &&
							path[j+1] == '.' && path[j+2] == '.' &&
							IS_SLASH(path[j+3])) {
						j += 4;
						path[j++] = '.';
						path[j++] = '.';
						path[j] = DEFAULT_SLASH;
					}
				}
			} else if (!start && !j) {
				/* leading '..' must not be removed in case of relative path */
				path[0] = '.';
				path[1] = '.';
				path[2] = DEFAULT_SLASH;
				j = 2;
			}
			return j;
		}
    
    	// 切割path，递归调用 tsrm_realpath_r()
    	path[len] = 0;

    ... // 以下省略
```

## 规约化情况

### 第一种规约

```c
if (i == len || (i + 1 == len && path[i] == '.')) {
    /* remove double slashes and '.' */
    len = EXPECTED(i > 0) ? i - 1 : 0;
    is_dir = true;
    continue;
}
```

删除路径末尾的 `/` 或 `/.` （或特例全路径 `.`）（前部分代码保证这里不会出现特例全路径 `/`），判断该路径为一个目录，并进入下一次循环

### 第二种规约

```c
if (i + 2 == len && path[i] == '.' && path[i+1] == '.') {
    /* remove '..' and previous directory */
    is_dir = true;
    if (link_is_dir) {
        *link_is_dir = 1;
    }
    if (i <= start + 1) {
        return start ? start : len;
    }
    j = tsrm_realpath_r(path, start, i-1, ll, t, use_realpath, true, NULL);
    if (j > start && j != (size_t)-1) {
        j--;
        ...
    } else if (!start && !j) {
        ...
    }
    return j;
}
```

#### 去掉 `..`

当路径以 `/..` 结尾时，递归调用 `tsrm_realpath_r()` ，传入的参数 `i-1` 表示路径字符串长度减3（此时 `i` 指向中间的 `.` ，字符串下标从0开始），得到去掉末尾 `/..` 后的**规约字符串的长度**

例如对于路径 `/usr/local/..` ，`j = len("/usr/local")` 

#### 去掉上级目录

如果 `j` 没有到达开头，也没有出错

```c
if (j > start && j != (size_t)-1)
```

`j--` 后指向路径串最后一个字符，然后再通过前面类似的 `while` 循环再找到最末尾的 `/` 的位置（注意这里**不是** `/` 的后一个位置）或开头位置

```c
j--;
assert(i < MAXPATHLEN);
while (j > start && !IS_SLASH(path[j])) {
    j--;
}
assert(i < MAXPATHLEN);
```

然后如果整个路径为相对路径（即 `start==0` ，表示路径开头没有 `/` ，如果是绝对路径，`tsrm_realpath_r()` 传入的start为1），**保留 `../../` 和 `usr/../../` 的情况（ `usr` 表示一般目录）**

```c
if (!start) {
    /* leading '..' must not be removed in case of relative path */
    if (j == 0 && path[0] == '.' && path[1] == '.' &&
        IS_SLASH(path[2])) {
        path[3] = '.';
        path[4] = '.';
        path[5] = DEFAULT_SLASH;
        j = 5;
    } else if (j > 0 &&
               path[j+1] == '.' && path[j+2] == '.' &&
               IS_SLASH(path[j+3])) {
        j += 4;
        path[j++] = '.';
        path[j++] = '.';
        path[j] = DEFAULT_SLASH;
    }
}
```

若 `j` 到达了开头且没有出错，并且是相对路径，则**保留 `..` 的情况**

```c
if (!start && !j) {
    /* leading '..' must not be removed in case of relative path */
    path[0] = '.';
    path[1] = '.';
    path[2] = DEFAULT_SLASH;
    j = 2;
}
```

最后返回 `j` 作为外层 `tsrm_realpath_r()` 的返回值，表示输入路径串规约化后的长度

<p style="text-align: right;">
by. Spark0618
</p>



