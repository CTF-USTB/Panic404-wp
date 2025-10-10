# 2025山东省大学生网络安全技能大赛-crypto

三道题出了两个

### ezcrypto

![image-20250927120542463](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251005192255891.png)

```python
from Crypto.Util.number import long_to_bytes, inverse
from math import isqrt

N = 27471366612277687007582969113484500296001065780066244888800712342807125394382681326213781865815461951298727242405665286291957769318403190235219727462190547340268057407480936794909750874545280586676586199139504945994789654115224950518297646992315179314766094156202525491469674180110591820099543752380512935927805722237181
e = 65537
g = 111684314954681193048509857146926361842347687090472066568935363273885037337811
C = 12643371534391958135236095622827564261907624974618206428861944879376238094269846145595767463703827586815298891013812360542402349502974102836324041194817837979051818191875704215738686008582339520686043633518534916826599993931844826243220488649199690449278527396151017995036899907805560418507134336681609833081538329779248

r = 2 * g
h = (N - 1) // r
s0 = h % r

S_min = 1 << 274
S_max = (1 << 275) - 2

k_min = (S_min - s0 + r - 1) // r
k_max = (S_max - s0) // r

p = q = None
for k in range(k_min, k_max + 1):
    S = s0 + k * r          # a+b 候选
    sum_pq = r * S + 2      # p+q
    D = sum_pq * sum_pq - 4 * N
    if D < 0:
        continue            # 跳过无效候选
    t = isqrt(D)
    if t * t != D:
        continue
    p_candidate = (sum_pq + t) // 2
    q_candidate = (sum_pq - t) // 2
    if p_candidate * q_candidate == N:
        p, q = p_candidate, q_candidate
        break

assert p and q, "factor failed"

phi = (p - 1) * (q - 1)
d = inverse(e, phi)
m = pow(C, d, N)
pt = long_to_bytes(m)
print(pt)
# b'flag{d39691fd3467e11c5c4443e65a93ab37}'
```



### rsaaa

当 p 和 q 很大时，n4 是这个表达式中的绝对主导项，而 p4+q4 相对于 n4 是一个较小的项。所以，我们可以做出一个关键的近似：

ϕ≈n4

题目给出的核心关系是：

e⋅d≡1(modϕ)

这等价于存在一个整数 k，使得：

e⋅d−k⋅ϕ=1

现在，我们用 n4 来近似 ϕ：

e⋅d−k⋅n4≈1

由于 e⋅d 和 k⋅n4 都非常大，这个 "1" 可以忽略不计，所以：

e⋅d≈k⋅n4

![image-20250927120742487](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251005192255893.png)

https://g.co/gemini/share/78a8a156a7f5

```python
from Crypto.Util.number import long_to_bytes

# 已知参数
c = 4569479985227351005063785995135067032720378517762895932536659766750620715910605148533244779487921315047171013575610160508152407529266889273867903198797261
n = 4886488210976342084709096740163565218271041981736454979038282347346782586289498952728993072164156014308360739234075655553608312787941314479273226321644139
e = 69226245919249557284362852197482448692961051575353210229155811272280423133461036546714805862880491826820998627526504053578014404131806296413582035968459012627551356400980693085358304615504234701685438459878813948020276726029476169237998655600278740940333141714850818687244699016224065398835277355085190021649464175896949882797374785669601481278636634767170296279707462651980061069176263757678901169598571771064631589157944694386675873019622753613139854047148807223799604198162775252510345809461265433420840521382586775251192251617135265179686326411651203242167525116012981497530813723052998392487942518359093767791

def continued_fraction_convergents(num, den):
    """计算 num/den 的连分数渐近分数"""
    a_list = []
    while den != 0:
        a = num // den
        a_list.append(a)
        num, den = den, num % den
    
    p_prev, q_prev = 1, 0
    p_curr, q_curr = a_list[0], 1
    yield p_curr, q_curr # 第一个渐近分数
    
    for i in range(1, len(a_list)):
        a_i = a_list[i]
        p_next = a_i * p_curr + p_prev
        q_next = a_i * q_curr + q_prev
        
        yield p_next, q_next
        
        p_prev, q_prev = p_curr, q_curr
        p_curr, q_curr = p_next, q_next

def solve():
    print("正在计算 n^4 ...")
    n4_approx = n**4
    print("正在计算 e / n^4 的连分数渐近分数...")

    # 获取渐近分数 k/d
    convergents = continued_fraction_convergents(e, n4_approx)

    for i, (k, d) in enumerate(convergents):
        # 基本的合理性检查
        if k == 0 or d == 0:
            continue
        
        print(f"尝试第 {i+1} 组候选 (k, d)，d 的位数为 {d.bit_length()}...")

        # 尝试用候选的 d 解密
        try:
            m = pow(c, d, n)
            flag_bytes = long_to_bytes(m)
            
            # 检查 flag 格式
            if b"flag{" in flag_bytes:
                print("\n[+] 成功找到 Flag!")
                print(f"  [-] 私钥 d: {d}")
                print(f"  [-] 明文: {flag_bytes.decode()}")
                return
        except Exception as err:
            # 可能会出现 long_to_bytes 转换失败等问题，忽略即可
            continue
    
    print("\n[-] 未能找到 Flag。")

if __name__ == '__main__':
    solve()
 	#[+] 成功找到 Flag!
    #[-] 私钥 d: 1338133894393370430259101557054242526599331059586233740134637750356111
    #[-] 明文: flag{fc3f4ce8dc3eaca8807812b8c0435cd4}
```

### 

<p style="text-align: right;">
by. Huaji
</p>