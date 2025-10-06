# 2025山东省大学生网络安全技能大赛-rev

共两道题，ak，其中第二道题的flag checker疑似出错（）

### game

ida打开到main，反编译

![image-20250927121214365](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251005191839849.png)

进sub_136D发现是迷宫的初始化

sub_1992是读取输入内容

sub_171E是判断，所以进去看

```
__int64 __fastcall sub_171E(char a1)
{
  unsigned int v2; // [rsp+18h] [rbp-8h]
  unsigned int v3; // [rsp+1Ch] [rbp-4h]

  v2 = dword_4468;
  v3 = dword_446C;
  switch ( a1 )
  {
    case 'w':
      v2 = dword_4468 - 1;
      break;
    case 's':
      v2 = dword_4468 + 1;
      break;
    case 'a':
      v3 = dword_446C - 1;
      break;
    case 'd':
      v3 = dword_446C + 1;
      break;
  }
  if ( (unsigned __int8)sub_1486(v2, v3) )
  {
    dword_4468 = v2;
    dword_446C = v3;
    sub_14FA(v2, v3);
    if ( byte_4140[40 * dword_4468 + dword_446C] == 35 )
    {
      sub_1805();
      return 1LL;
    }
  }
  else
  {
    puts(asc_2242);
  }
  return 0LL;
}
```

进入sub_1805

```
int sub_1805()
{
  unsigned __int8 v1; // [rsp+Bh] [rbp-5h]
  int i; // [rsp+Ch] [rbp-4h]

  putchar(10);
  for ( i = 0; i <= 38; ++i )
  {
    v1 = byte_4020[i] ^ byte_4060[i];
    if ( v1 <= 0x1Fu || v1 > 0x7Eu )
      putchar(46);
    else
      putchar(v1);
  }
  return putchar(10);
}
```

看到byte_4020，byte_4060有异或

sub_14FA：

```c
int __fastcall sub_14FA(int a1, int a2)
{
  __int64 v2; // rdx
  int result; // eax
  __int64 v4; // rdx
  int v5; // eax
  char v6; // [rsp+13h] [rbp-Dh]
  int i; // [rsp+14h] [rbp-Ch]
  unsigned int v8; // [rsp+18h] [rbp-8h]
  int v9; // [rsp+1Ch] [rbp-4h]

  v2 = 40LL * a1 + a2;
  result = (unsigned __int8)byte_4140[v2];
  v6 = byte_4140[v2];
  if ( v6 > 48 && v6 <= 52 )
  {
    v4 = 40LL * a1 + a2;
    result = byte_4480[v4] ^ 1;
    if ( byte_4480[v4] != 1 )
    {
      v8 = v6 - 48;
      v5 = time(0LL);
      srand(v5 ^ (31 * a1 + 17 * a2));
      v9 = rand() % 5 + 1;
      if ( v9 > 0 && v9 <= 4 )
      {
        printf("浣犳寫鎴楤oss %d澶辫触锛屾父鎴忕粨鏉燂紒\n", v8);
        exit(1);
      }
      for ( i = 0; i <= 38; ++i )
      {
        switch ( v6 )
        {
          case '1':
            --byte_4020[i];
            break;
          case '2':
            byte_4020[i] -= 2;
            break;
          case '3':
            byte_4020[i] += 3;
            break;
          case '4':
            byte_4020[i] += 4;
            break;
        }
      }
      byte_4480[40 * a1 + a2] = 1;
      return printf(asc_222A, v8);
    }
  }
  return result;
}
```

这里对进行了4次操作，-1-2+3+4，所以在脚本上加上，提出来byte_4020和byte_4060

```python
a=[0x22,0xC6,0x39,0x8E,0xDC,0x0B,0x59,0x4C,0xFA,0xA3,0x05,0x86,0xCF,0x3D,0xB7,0x1D,0x63,0xAC,0x2E,0xEF,0x44,0x97,0x5C,0x7B,0xD2,0x08,0x89,0xB9,0x36,0xC9,0x4A,0x13,0x9C,0xDE,0x29,0x6C,0xF7,0x53,0x82,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
b=[0x40,0xA6,0x5C,0xF5,0x9B,0x4B,0x38,0x36,0x9B,0xC6,0x7D,0xEF,0xB7,0x1E,0xD9,0x11,0x14,0xC3,0x6D,0x92,0x26,0xFF,0x3F,0x08,0xB7,0x60,0xE6,0xD8,0x5E,0x92,0x01,0x62,0xD4,0xBD,0x60,0x11,0x81,0x32,0xFB,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]

for i in range(len(a)):
    a[i]-=1
    a[i]-=2
    a[i]+=3
    a[i]+=4
    a[i] = a[i] ^ b[i]
    print(chr(a[i]), end="")
```



### error

ida打开到main，反编译

![image-20250927122302362](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251005191839850.png)

发现这里对s1和s2进行了比较

提出来s2='d2e7f6d2f17123532dd8996ec04d94a6912dafd6f1b37c1d264d43a91d804d63542ef89b'

看sub_127E是加密操作，所以让gpt写，但是乱码，观察汇编，发现loc_12A7中

![image-20250927123748284](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251005191839851.png)

所以把12AE这里改成1

![image-20250927123832100](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251005191839853.png)

之后代码就完整了，扔给gpt

```c
__int64 __fastcall sub_127E(__int64 a1, int a2)
{
  __int64 result; // rax
  char v3; // [rsp+1Ah] [rbp-1Eh]
  char v4; // [rsp+1Bh] [rbp-1Dh]
  int i; // [rsp+1Ch] [rbp-1Ch]
  int j; // [rsp+20h] [rbp-18h]
  int m; // [rsp+24h] [rbp-14h]
  int k; // [rsp+28h] [rbp-10h]

  for ( i = 0; ; ++i )
  {
    result = 3LL;
    if ( i >= 3 )
      break;
    for ( j = 0; j < a2; ++j )
    {
      *(_BYTE *)(j + a1) ^= byte_2060[j % 16];
      *(_BYTE *)(j + a1) = sub_1249(*(unsigned __int8 *)(j + a1), (unsigned int)(i + 1));
    }
    if ( (i & 1) != 0 )
    {
      for ( k = 0; k < a2 / 2; ++k )
      {
        v3 = *(_BYTE *)(k + a1);
        *(_BYTE *)(k + a1) = *(_BYTE *)(a2 - 1 - k + a1);
        *(_BYTE *)(a1 + a2 - 1 - k) = v3;
      }
    }
    else
    {
      for ( m = 0; m < a2 - 1; m += 2 )
      {
        v4 = *(_BYTE *)(m + a1);
        *(_BYTE *)(m + a1) = *(_BYTE *)(m + 1LL + a1);
        *(_BYTE *)(a1 + m + 1LL) = v4;
      }
    }
  }
  return result;
}
```



https://chatgpt.com/share/e/68d75349-faf8-8005-9b4d-0c997b462607



解密需按 i=2→0 逆序执行，先还原置换（i 偶数：两两交换；i 奇数：整体反转），再对每字节做`inv_sub_1249(x, i+1)`，最后异或同一轮密钥 `byte_2060[j%16]`。下面给出 Python 脚本，默认把 `sub_1249` 视为“左循环位移 ROL n”，其逆为“右循环位移 ROR n”

拿byte_2060=[

  0x1A, 0x2B, 0x3C, 0x4D, 0x5E, 0x6F, 0x70, 0x81, 0x92, 0xA3, 

  0xB4, 0xC5, 0xD6, 0xE7, 0xF8, 0x09, 0x10, 0x00, 0x00, 0x00, 

  0x03, 0x00, 0x00, 0x00]

```python
# -*- coding: utf-8 -*-
from typing import ByteString

KEY = [
    0x1A, 0x2B, 0x3C, 0x4D, 0x5E, 0x6F, 0x70, 0x81,
    0x92, 0xA3, 0xB4, 0xC5, 0xD6, 0xE7, 0xF8, 0x09,
]
# 仅用前16字节；其余 db 未被用到，因为代码里 j % 16

def ror8(x: int, n: int) -> int:
    n &= 7
    return ((x >> n) | ((x << (8 - n)) & 0xFF)) & 0xFF

def inv_sub_1249(x: int, n: int) -> int:
    # 假设 sub_1249 是 ROL(x, n)，逆为 ROR(x, n)
    return ror8(x, n)

def undo_pair_swap(b: bytearray) -> None:
    for m in range(0, len(b) - 1, 2):
        b[m], b[m + 1] = b[m + 1], b[m]

def undo_reverse(b: bytearray) -> None:
    b.reverse()

def decrypt(buf: ByteString) -> bytes:
    b = bytearray(buf)
    for i in (2, 1, 0):
        if (i & 1) != 0:
            undo_reverse(b)
        else:
            undo_pair_swap(b)
        for j in range(len(b)):
            b[j] = inv_sub_1249(b[j], (i + 1) & 0xFF)
            b[j] ^= KEY[j % 16]
    return bytes(b)

if __name__ == "__main__":
    # 硬编码十六进制密文
    s = "d2e7f6d2f17123532dd8996ec04d94a6912dafd6f1b37c1d264d43a91d804d63542ef89b"
    data = bytes.fromhex(s)

    plain = decrypt(data)

    import sys
    try:
        sys.stdout.buffer.write(plain)
    except BrokenPipeError:
        pass
#flag{Th1s_1s_My_S1mpl3_Fl4g_f0r_CTF}
```

