# 羊城杯2025-Crypro

### 瑞德的一生


$$
\begin{aligned}
&\text{已知 } n,x,\; c_i,c_{i+1}. \\
&s_i^{(b)} \equiv c_i\cdot x^{-b}\pmod n,\quad b\in\{0,1\}. \\
&\text{若猜测正确，则 } s_i^{(b_i)} \equiv y_i^2. \\
&R \coloneqq y_{i+1}-y_i \in (0,2^{48}).\\[2mm]
&F(R) \equiv \big(s_{i+1}^{(b_{i+1})}-s_i^{(b_i)}-R^2\big)^2-4\,s_i^{(b_i)}\,R^2 \equiv 0 \pmod n.\\[2mm]
&\text{用 Coppersmith 单变量小根在 } 0<R<2^{48} \text{ 内求 } R. \\
&y_i \equiv \big(s_{i+1}^{(b_{i+1})}-s_i^{(b_i)}-R^2\big)\,(2R)^{-1}\pmod n,\\
&y_{i+1}\equiv y_i+R\pmod n.\\[2mm]
&m=\sum_{k} b_k\,2^{k}\quad(\text{密文按 LSB}\to\text{MSB}).
\end{aligned}
$$

exp：

```sage
from sage.all import *
import re, ast, sys

txt = open('output.txt','r',encoding='utf-8').read()
n  = Integer(re.search(r'n\s*=\s*(\d+)', txt).group(1))
x  = Integer(re.search(r'x\s*=\s*(\d+)', txt).group(1))
enc = list(map(Integer, ast.literal_eval(re.search(r'enc\s*=\s*(\[.*\])', txt, re.S).group(1))))

ZmodN = Zmod(n)
invx  = Integer(inverse_mod(x, n))
Rbound = 2^48  # r 的已知上界

# 预计算去掉 x 因子的两套残差：b=0 -> s0[i]=enc[i]， b=1 -> s1[i]=enc[i]*x^{-1}
s0 = [ZmodN(c) for c in enc]
s1 = [ZmodN(c) * invx for c in enc]

def try_seed_at(i):
    """
    在位置 i 尝试四种 (b_i, b_{i+1}) ∈ {(0,0),(0,1),(1,0),(1,1)}
    用 F_i(r) = ((Δs)-r^2)^2 - 4 r^2 s_i 做一次四次小根，返回首个成功的 (r_i, y_i, b_i, b_{i+1})
    """
    PR = PolynomialRing(ZmodN, 'r'); r = PR.gen()
    for bi in (0,1):
        for bj in (0,1):
            si  = s0[i] if bi==0 else s1[i]
            sip = s0[i+1] if bj==0 else s1[i+1]
            Ds  = (sip - si)  # Δs = s_{i+1}-s_i  (mod n)
            F   = (Ds - r^2)^2 - 4*r^2*si          # 一元四次
            # Coppersmith 小根：r < 2^48 远小于 n^{1/4}，beta=1 即可
            roots = F.small_roots(X=Rbound, beta=1)
            for rr in roots:
                rr = Integer(rr)
                if rr <= 0 or rr >= Rbound: 
                    continue
                # 反推 y_i ，并校验
                inv_2r = inverse_mod(2*rr, n)
                yi = Integer(( (Ds - rr*rr) * inv_2r ) % n)
                # 校验：y_i^2 ≡ s_i, (y_i+r)^2 ≡ s_{i+1}
                if (Integer(yi)^2 % n) != Integer(si):
                    continue
                if (Integer(yi+rr)^2 % n) != Integer(sip):
                    continue
                return rr, yi, bi, bj
    return None

def step_forward(j, yj, bj):
    """
    已知 y_j 与 b_j，向前解第 j+1 位：
      解 r^2 + 2*yj*r - (s_{j+1}-s_j) ≡ 0 (mod n), 0<r<2^48
      试 b_{j+1}=0 或 1，哪个给出小根且通过校验，就选哪个
    返回 (r_j, y_{j+1}, b_{j+1}) 或 None
    """
    PR = PolynomialRing(ZmodN, 'r'); r = PR.gen()
    sj = s0[j] if bj==0 else s1[j]
    for bnext in (0,1):
        sj1 = s0[j+1] if bnext==0 else s1[j+1]
        Ds  = (sj1 - sj)
        F   = r^2 + 2*Integer(yj)*r - Ds
        roots = F.small_roots(X=Rbound, beta=1)
        for rr in roots:
            rr = Integer(rr)
            if rr <= 0 or rr >= Rbound:
                continue
            y1 = yj + rr
            # 校验两边平方
            if (Integer(y1)^2 % n) != Integer(sj1):
                continue
            return rr, Integer(y1), bnext
    return None

def step_backward(j, yj, bjm1):
    """
    已知 y_j 与 b_{j-1}，向后解第 j-1 位：
      用等式：s_j - s_{j-1} ≡ 2*y_{j-1} r + r^2 ，代入 y_{j-1}=y_j - r
      得：r^2 - 2*y_j*r + (s_j - s_{j-1}) ≡ 0 (mod n)
      同样试 b_{j-1}=0 或 1，哪个有小根且通过校验选哪个
    返回 (r_{j-1}, y_{j-1}, b_{j-1}) 或 None
    """
    PR = PolynomialRing(ZmodN, 'r'); r = PR.gen()
    sj = s0[j] if (bjm1 is None) else None  # 这里我们按需要分别试 b_{j-1}
    for bprev in (0,1):
        sjm1 = s0[j-1] if bprev==0 else s1[j-1]
        # s_j 未知 b 时需要两种都试；为简单起见分别构造
        for bj in (0,1):
            sj  = s0[j] if bj==0 else s1[j]
            Ds  = (sj - sjm1)
            F   = r^2 - 2*Integer(yj)*r + Ds
            roots = F.small_roots(X=Rbound, beta=1)
            for rr in roots:
                rr = Integer(rr)
                if rr <= 0 or rr >= Rbound:
                    continue
                y0 = yj - rr
                if (Integer(y0)^2 % n) != Integer(sjm1):
                    continue
                # 返回时一并确定 b_{j-1}, 以及我们选择的 b_j
                return rr, Integer(y0), bprev, bj
    return None

# 2) 寻找一个“种子” i
seed = None
for i in range(len(enc)-1):
    seed = try_seed_at(i)
    if seed:
        r0, y0, b_i, b_ip = seed
        seed_idx = i
        break

if not seed:
    print("[-] 未在默认搜索里找到可用种子；可调大搜索范围或换机器再试。")
    sys.exit(1)

print(f"[+] seed at i={seed_idx}: r={r0} (<2^48), got y_i, bits {b_i}{b_ip}")

# 3) 向右推进
bits = [None]*len(enc)
y_vals = [None]*len(enc)
bits[seed_idx]   = b_i
bits[seed_idx+1] = b_ip
y_vals[seed_idx] = y0
y_vals[seed_idx+1] = y0 + r0

j = seed_idx+1
while j < len(enc)-1:
    step = step_forward(j, y_vals[j], bits[j])
    if not step:
        print(f"[-] forward 失败在 j={j}，可换另一个 seed 重试。")
        sys.exit(1)
    rj, yj1, bnext = step
    bits[j+1] = bnext
    y_vals[j+1] = yj1
    j += 1

# 4) 向左推进
j = seed_idx
while j > 0:
    # 这里我们只需要 b_{j-1} 和 y_{j-1}；本实现选择较直接但略保守的双试
    # 为简洁起见，构造一个和 forward 对称的 “后退二次”：
    # 利用：s_j - s_{j-1} = 2*y_{j-1}*r_{j-1} + r_{j-1}^2
    found = None
    PR = PolynomialRing(ZmodN, 'r'); r = PR.gen()
    sj = s0[j] if bits[j]==0 else s1[j]
    for bprev in (0,1):
        sjm1 = s0[j-1] if bprev==0 else s1[j-1]
        Ds   = (sj - sjm1)
        F    = r^2 - 2*Integer(y_vals[j])*r + Ds
        roots = F.small_roots(X=Rbound, beta=1)
        for rr in roots:
            rr = Integer(rr)
            if rr <= 0 or rr >= Rbound: 
                continue
            yjm1 = Integer(y_vals[j] - rr)
            if (Integer(yjm1)^2 % n) != Integer(sjm1):
                continue
            found = (rr, yjm1, bprev)
            break
        if found: break
    if not found:
        print(f"[-] backward 失败在 j={j-1}，可换 seed 或调参数。")
        sys.exit(1)
    rr, yjm1, bprev = found
    bits[j-1]   = bprev
    y_vals[j-1] = yjm1
    j -= 1

# 5) 组装明文（注意 enc 是 LSB->MSB）
m = 0
for i,b in enumerate(bits):
    if b not in (0,1):
        print("[-] 有未确定位，异常。"); sys.exit(1)
    m |= (b << i)

digits_256 = [int(d) for d in Integer(m).digits(256)]
bs = bytes(reversed(digits_256))
try:
    print("FLAG =", bs.decode())
except UnicodeDecodeError:
    print("FLAG(hex) =", bs.hex())
    
    
#[+] seed at i=0: r=31335709591515 (<2^48), got y_i, bits 10
#FLAG = DASCTF{Wh@t_y0u_See_Is_r3a1??}
```

### Ridiculous LFSR

题面建模

- 出题脚本：每轮取 `temp = LFSR.next(L)`，记其 1 的个数为 `l[i]`；输出 `c[i] = temp ⊕ m_i`，其中 `m_{i+1} = rotl(m_i,1)`（比特循环左移 1）

- 为与初始明文 m 对齐，做 `t_i = rotr(c[i], i)`，则 `t_i = rotl(temp,i) ⊕ m`。因旋转不改比特个数：`popcount(rotl(temp,i)) = l[i]`。

将 popcount 变成线性方程

- 记 `x = rotl(temp,i)` 的第 j 位为 `x_{ij}`，`z_j = m` 的第 j 位。
- 恒等式：`x_j ⊕ z_j = x_j + z_j - 2 x_j z_j`。两侧对 j 求和并移项，可化成
  `popcount(x ⊕ z) - popcount(x) = Σ_j (2·x_{ij}-1)·z_j`。
- 对本题：左边等于 `a[i] - l[i]`，其中 `a[i] = popcount(t_i)`，右边的系数定义为 `V_{ij} = 2·t_i[j]-1`（±1）。于是得到整数线性系统 `V z = target`，`target[i]=a[i]-l[i]`。

数值求解

变量 `z_j ∈ {0,1}`。采用启发式坐标下降：反复试翻某一位 `z_j`，若能降低残差平方和 `‖Vz-target‖²` 就接受；停在 0 残差时得到精确解。

复现器实现：

​	右回转 `c[i]` 得 `t_i`，计算 `a[i]=bit_count(t_i)`，构造 `V` 与 `target`；

​	逐位随机采样+最佳翻转，直到残差为 0；

​	组回 `m` 并转为字节输出

```python
# 核心复现器（基于题面数据），Python 3.10+
# 说明：把 output.txt 里的 c 与 l 列表填入即可。
LENGTH = 295
# c = [...]  # 来自 output.txt
# l = [...]  # 来自 output.txt

def rotl(x, r, n=LENGTH):
    s = bin(x)[2:].zfill(n); r %= n
    return int(s[r:]+s[:r], 2)
def rotr(x, r, n=LENGTH):
    return rotl(x, n - (r % n), n)

# t_i = rotate_right(c[i], i)
t = [rotr(ci, i, LENGTH) for i, ci in enumerate(c)]
a = [ti.bit_count() for ti in t]
b = l[:]  # popcount(temp_i)

# V_{ij} = 2*t_i[j] - 1  (±1)
m, n = len(t), LENGTH
def bit_at(x, j):  # j: 0..n-1, MSB first
    return (x >> (n-1-j)) & 1
V = [[ (1 if bit_at(t[i], j) else -1) for j in range(n) ] for i in range(m)]
target = [a[i] - b[i] for i in range(m)]

# 启发式坐标下降：逐位翻转 z_j (0/1) 以减少平方误差，直到恰好 0。
z = [0]*n
# r = Vz - target
r = [-target[i] for i in range(m)]  # 因为 Vz 初始为 0
def deltaE(j):
    sign = 1 if z[j]==0 else -1
    col = [V[i][j] for i in range(m)]
    new = [r[i] + sign*col[i] for i in range(m)]
    return sum(v*v for v in new) - sum(v*v for v in r)

import random
random.seed(0)
E = sum(v*v for v in r)
for _ in range(20000):
    best, best_j = 0, None
    for _ in range(100):  # 采样若干位，选最优翻转
        j = random.randrange(n)
        dE = deltaE(j)
        if dE < best:
            best, best_j = dE, j
    if best_j is None:
        # 走不动就随机扰动一位
        j = random.randrange(n)
        best_j = j
    # 应用翻转
    sign = 1 if z[best_j]==0 else -1
    for i in range(m):
        r[i] += sign * V[i][best_j]
    z[best_j] ^= 1
    E = sum(v*v for v in r)
    if E == 0: break

# 组回明文
m_int = 0
for j in range(n):
    m_int = (m_int<<1) | z[j]
m_bytes = m_int.to_bytes((n+7)//8, 'big')
print(m_bytes)  # b"It'5_4_pr0bl3m_0f_L4ttice!_n0t_LFSR!!"
```

<p style="text-align: right;"> by. Huaji </p> 