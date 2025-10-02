>Git是一个版本控制系统，它允许开发者在本地计算机上跟踪和管理代码的历史变更。而GitHub则是一个在线平台，它使用Git作为版本控制工具，允许开发者存储、共享和协作代码项目。

## 基本操作
首先本地没有仓库，把远程仓库完整地 **克隆（clone）** 到本地
```sh
git clone https://github.com/CTF-USTB/Panic404-wp.git
```

这个时候就可以对本地仓库中的文件进行修改了，此时你处于git的工作区
修改完后需要 **添加（add）** 文件到暂存区
```sh
# .表示工作区中所有修改的文件
git add .
```

可以多次修改多次添加，当所有改动都加入暂存区后，需要 **提交（commit）** 到本地仓库
```sh
# "description" 字符串为这次提交的描述
git commit -m "description"
```

然后可以将提交 **推送（push）** 到github云端仓库
```sh
# 默认推送当前分支
git push
# 然后会让你验证你的账户身份
```

后续在本地获取云端最新仓库需要 **拉取（pull）**
```sh
# origin 为一个默认变量，存储云端仓库地址
# main 为主分支名
git pull origin main
```

拉取完毕后可以接着在本地仓库编辑
## Fork & Pull request
>Github平台提供的协作机制

当你没有对远程仓库的写入权限时，可以使用 **Fork**，在你账户下复制一个远程仓库，生成独立仓库，然后你可以对自己账户下的这个远程仓库进行上述的基本操作

![屏幕截图 2025-10-02 153002](https://cdn.jsdelivr.net/gh/CTF-USTB/Panic404-wp-images/images/20251002153344188.png)

Fork完成后首先 **clone**
```sh
# fork时默认仓库名为Panic404-wp
git clone https://github.com/你的用户名/Panic404-wp.git
cd Panic404-wp
```

然后添加原始仓库为 upstream
```sh
git remote add upstream https://github.com/CTF-USTB/Panic404-wp.git
```

同步原始仓库最新提交
```sh
git fetch upstream
git checkout main
git merge upstream/main
```

然后为了不污染main分支，一般需要新建一个分支用于编辑开发
```sh
# git checkout 可以切换到对应分支
# git branch 可以创建一个分支
# git checkout -b 为创建并切换到该分支
# [username] 为你的Github用户名，便于我们管理
git checkout -b [username]-wp
```

然后将所有改动在这个分支上提交，并推送该分支到自己的远程仓库
```sh
# 编辑、提交
git add .
git commit -m "Add my writeup"

# 推送到自己的 Fork
git push origin [username]-wp
```

最后在Github上的该Fork仓库中提交 **Pull request（PR）**，请求原仓库的审核者 **pull** 你的分支，然后等待审核或修改意见

## 后续提交PR的一般流程

进入本地仓库（*此时位于之前新建的分支上*），拉取上游仓库更新本地fork仓库（*确保upstream地址在上述过程中配置完成*）

```sh
git pull --rebase upstream main
```

添加、提交编辑好的wp

```sh
git add .
git commit -m "Add my writeup"
```

将分支推送到自己的 Fork仓库

```sh
git push --force-with-lease origin [username]-wp
```

登入Github对应Fork仓库提交PR，等待审核或修改意见

