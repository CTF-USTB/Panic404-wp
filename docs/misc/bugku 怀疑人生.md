<span style="color:#808080; font-size:2.5em;">怀疑人生</span>



> <span style="font-size:1.3em;">bugku misc題</span>

## 第一個文件 ctf1.zip

打開壓縮包有三個文件，當中 `ctf1.zip` 是加密的，不能直接解壓。

![image-20251003192229926](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251003213657300.png)



![image-20251003192349426](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251003213657301.png)

可以使用 ARCHPR 工具進行破解，得到密碼為 `password`。

![image-20251003192820147](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251003213657302.png)

成功解壓後得到一個 txt 文件，里面內容為 ``XHU2Nlx1NmNcdTYxXHU2N1x1N2JcdTY4XHU2MVx1NjNcdTZiXHU2NVx1NzI=``

猜測為 base64 加密，通過在線工具解密(https://ctf.bugku.com/tool/base64)，得到 ![image-20251003193041600](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251003213657303.png)

繼續用在線工具處理 Unicode 碼，得到 **flag{hacker**

![image-20251003193607788](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251003213657304.png)

由於沒有得到的 flag 有 `"{"` 但沒有 `"}"`，所以應該只是一部份的 flag，剩下的 flag 可能在兩張圖片上。

## 第二個文件 ctf3.jpg

扫描二维码(ctf3.jpg)的圖片，得到 **12580}**

![image-20251003194223004](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251003213657305.png)

## 第三個文件 ctf2.jpg

还有一個圖片沒有分析，可以用010editor先分析，發現jpg文件中有一個txt文件

![image-20251005001808174](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251005002215995.png)

再用binwalk進行分析，得到隐藏有一个加密的 ZIP 归档文件，里面包含 `ctf2.txt`

![image-20251003203528664](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251003213657306.png)

使用 `binwalk -e ctf2.jpg` 命令尝试提取

![image-20251003203753156](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251003213657307.png)

得到這兩個文件，當中 `ctf2.txt` 內容為

`..... ..... ....! ?!!.? ..... ..... ....? .?!.? ....! .?... ..... .....
..!?! !.?.. ..... ..... ..?.? !.?.. ..... ..... ..... ..... !.?.. .....
..... .!?!! .?!!! !!!!! !!!!? .?!.? !!!!! !!!!! !!!!! .?... ....! ?!!.?
!!!!! !?.?! .?!!! !!!!! !!!!! .!!!. ?.... ..... ..... .!?!! .?... .....
..... .?.?! .?!.? .`應該是一種加密，上網找一下是 OoK 加密。通過線上工具解碼(<https://www.splitbrain.org/services/ook>)

![image-20251003204546890](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251003213657308.png)

解碼得 **3oD54e**，和前面的部分 flag 組合在一起，可以得到 flag{hacker3oD54e12580}，提交後提示不正確，查看題目中的評論得知中間是 base58 加密，再解密得到中間部分 flag 為 misc

![image-20251003205059121](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251003213657309.png) 所以正確的flag：flag{hackermisc12580}

![image-20251003205159250](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251003213657310.png)
