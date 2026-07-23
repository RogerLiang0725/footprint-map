# 手把手：从解压到网站上线

写给"知道命令行是什么但没怎么用过 git"的人。每一步都写清楚**在哪里操作、
输入什么、应该看到什么**。全程 10–15 分钟。

目标产物：`https://你的用户名.github.io/footprint-map/`

---

# 一、认识两个"入口"

整个过程只在两个地方操作，先分清楚：

| 入口 | 在哪 | 干什么 |
|---|---|---|
| **终端 Terminal** | 你电脑上的一个 App | 敲 `git` 命令，把文件传上去 |
| **github.com** | 浏览器 | 建仓库、开网站开关 |

`git init` 这类命令**全部在终端里敲**，GitHub 网页上没有这个按钮。

## 怎么打开终端

**macOS：** 按 `Command + 空格` 打开 Spotlight → 输入 `terminal` → 回车。
（也可以在 访达 → 应用程序 → 实用工具 → 终端）

**Windows：** 开始菜单搜 `PowerShell` → 打开。（下文命令通用，个别差异会标注）

打开后你会看到类似这样的一行，末尾有个光标在闪：

```
roger@Rogers-MacBook-Pro ~ %
```

`%`（或 Windows 的 `>`）叫**提示符**，它后面才是你输入的地方。
本文代码块里出现的命令，**不要连提示符一起复制**，只复制命令本身。

每输完一条命令要按**回车**才会执行。

---

# 二、准备工作

## 2.1 确认 git 装好了

在终端里输入，回车：

```bash
git --version
```

看到 `git version 2.39.3` 之类的就是有了，跳到 2.2。

看到 `command not found: git`：

- macOS：输入 `xcode-select --install`，回车，会弹窗让你装命令行工具，点"安装"，等几分钟
- Windows：去 https://git-scm.com/download/win 下载安装，一路下一步，**装完要关掉终端重开**

## 2.2 告诉 git 你是谁

只需做一次。把引号里的换成你自己的（邮箱建议用注册 GitHub 那个）：

```bash
git config --global user.name "Roger"
git config --global user.email "roger@example.com"
```

这两条**执行完不会有任何输出**，这是正常的——git 的哲学是"没消息就是成功"。
想确认的话：

```bash
git config --global user.name
```

会把刚才设的名字打印出来。

## 2.3 有 GitHub 账号

没有就去 https://github.com/signup 注册，记住你的**用户名**（下文所有 `USERNAME`
都要换成它）。

---

# 三、把项目放到一个你找得到的地方

## 3.1 解压

双击 `footprint-map.zip`，macOS 会在同目录解出一个 `footprint-map` 文件夹。
假设它在"下载"里。

## 3.2 让终端"进入"这个文件夹

这是新手最容易卡住的一步。终端任何时候都"站在"某个文件夹里，
`git init` 会作用在**当前所在的文件夹**上，所以必须先站对地方。

**方法 A（推荐，不会打错）：** 在终端里输入 `cd`，然后**敲一个空格**，
再把 `footprint-map` 文件夹从访达**拖进终端窗口**——路径会自动填进去。
然后回车。

```bash
cd /Users/roger/Downloads/footprint-map
```

**方法 B：** 手动敲

```bash
cd ~/Downloads/footprint-map
```

`~` 代表你的用户主目录。Windows 的话是 `cd $HOME\Downloads\footprint-map`。

## 3.3 确认站对了

```bash
pwd
```

打印出的路径末尾应该是 `/footprint-map`。再看看里面有什么：

```bash
ls
```

应该看到：

```
DEPLOY.md   README.md   data        index.html      scripts
LICENSE     dots.html   requirements.txt
```

**必须能看到 `index.html`**。如果 `ls` 出来只有一个 `footprint-map` 文件夹，
说明你多套了一层，再 `cd footprint-map` 进去一层。

> 从这一步开始，**终端窗口就别关了**，后面所有命令都在这个位置执行。
> 万一关了，重新打开后要再做一遍 3.2。

---

# 四、在 GitHub 网页上建一个空仓库

## 4.1 找到入口

浏览器打开 https://github.com 并登录，然后：

- **右上角**你的头像**左边**有个 `+` 号 → 点它 → 选 **New repository**
- 或者直接访问 https://github.com/new （更快）

## 4.2 填表

只有四个地方要动：

1. **Repository name**：填 `footprint-map`
   （只能用字母数字和 `-`，这个名字会出现在最终网址里）
2. **Description**：可留空，想填就写 `Mark the countries and provinces you've been to`
3. **Public / Private**：**必须选 Public**。免费账号的 GitHub Pages 只对公开仓库开放
4. **Initialize this repository with** 下面的三个勾选框
   —— **Add a README file / Add .gitignore / Choose a license**
   —— **一个都不要勾**

> 为什么不能勾：勾了 GitHub 会先自己提交一次，你本地的仓库就和它对不上，
> 后面 push 会被拒。（真勾了也能救，见第八章第 3 条。）

## 4.3 创建

点绿色的 **Create repository**。

跳转后的页面上会有一段代码，中间那行长这样：

```
git remote add origin https://github.com/USERNAME/footprint-map.git
```

**这行等下要用**，页面先别关。

---

# 五、把文件推上去（回到终端）

确认终端还站在 `footprint-map` 目录里（不确定就再 `pwd` 一次）。
下面五条命令**一条一条**执行，每条回车后等它跑完再敲下一条。

## 5.1 `git init` —— 把这个文件夹变成 git 仓库

```bash
git init
```

预期输出：

```
Initialized empty Git repository in /Users/roger/Downloads/footprint-map/.git/
```

这条命令做的事：在当前文件夹里悄悄建一个隐藏的 `.git` 目录，用来记录版本历史。
**它没有图形界面入口，就是在终端敲这一行。**

如果提示 `Reinitialized existing Git repository`，说明之前已经 init 过了，无所谓，继续。

## 5.2 `git add .` —— 把所有文件放进"待提交"

```bash
git add .
```

注意 `add` 后面有**一个空格加一个点**，点表示"当前目录下的全部文件"。

**没有任何输出是正常的。** 想看看它选中了什么：

```bash
git status
```

会列出一堆绿色的 `new file: ...`。确认里面有
`index.html`、`data/world.js`、`data/admin1.js`。

## 5.3 `git commit` —— 存一个版本快照

```bash
git commit -m "footprint map"
```

`-m` 后面引号里是这次改动的说明，随便写。预期输出：

```
[main (root-commit) a1b2c3d] footprint map
 13 files changed, 12345 insertions(+)
```

> 如果这里报 `Please tell me who you are`，说明 2.2 没做，回去做完再重新执行这条。

## 5.4 `git branch -M main` —— 把主分支改名叫 main

```bash
git branch -M main
```

无输出。老版本 git 默认叫 `master`，GitHub 现在用 `main`，统一一下免得后面对不上。

## 5.5 `git remote add origin` —— 告诉本地"要传去哪"

把 `USERNAME` 换成你的用户名（或者直接从 4.3 那个页面复制）：

```bash
git remote add origin https://github.com/USERNAME/footprint-map.git
```

无输出。确认一下：

```bash
git remote -v
```

会打印两行 origin 地址，检查用户名和仓库名有没有打错。

> 打错了不用慌：`git remote set-url origin 正确的地址` 覆盖掉就行。

## 5.6 `git push` —— 真正上传

```bash
git push -u origin main
```

**这一步会要求登录**，见下一节。成功的话最后几行是：

```
To https://github.com/USERNAME/footprint-map.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

刷新 GitHub 上的仓库页面，文件都在了。

---

# 六、push 时的登录（最容易卡的地方）

GitHub 从 2021 年起**不接受账号密码**。终端弹出的
`Password for 'https://USERNAME@github.com':` 要填的是 **Personal Access Token**。

## 6.1 生成 token（浏览器操作）

点击路径有点深，照着走：

1. 右上角**头像** → **Settings**（这是账号设置，不是仓库设置）
2. 左侧菜单拉到**最底下** → **Developer settings**
3. 左侧 → **Personal access tokens** → **Tokens (classic)**
4. 右上 **Generate new token** → **Generate new token (classic)**
5. 填写：
   - **Note**：随便写，比如 `mac-terminal`
   - **Expiration**：90 days 或 No expiration 都行
   - **Select scopes**：勾第一个大项 **`repo`**（勾它会自动带上下面几个子项）
6. 拉到底点绿色 **Generate token**
7. 页面顶部出现一串 `ghp_xxxxxxxxxxxx` —— **立刻复制，关掉就再也看不到了**

直达链接：https://github.com/settings/tokens

## 6.2 用它登录

回到终端，重新执行：

```bash
git push -u origin main
```

- `Username:` → 输入你的 GitHub 用户名，回车
- `Password:` → **粘贴那串 ghp_...**，回车

> **终端里粘贴密码时光标不动、什么都不显示，这是正常的**，不是没粘上。
> 粘完直接回车。

macOS 的钥匙串会记住，以后 push 不用再输。

## 6.3 懒人方案：GitHub CLI

不想折腾 token 的话：

```bash
brew install gh
gh auth login
```

按提示选 `GitHub.com` → `HTTPS` → `Login with a web browser`，
复制屏幕上的一次性码，浏览器里粘贴授权，完事。

装了 `gh` 之后，**第四章和第五章可以合并成一条命令**（前提是已经 `git init`、
`add`、`commit` 过）：

```bash
gh repo create footprint-map --public --source=. --push
```

---

# 七、打开 GitHub Pages 开关（浏览器操作）

文件传上去了，但网站还没开。

1. 进入你的仓库页面 `https://github.com/USERNAME/footprint-map`
2. 点顶部导航栏的 **⚙️ Settings**
   （在 Code / Issues / Pull requests / Actions ... 这一排的最右边。
   看不到就是屏幕窄了，点 `···` 展开）
3. 左侧菜单里找 **Pages**（在 "Code and automation" 分组下）
4. 中间的 **Build and deployment** 区域：
   - **Source** 下拉选 **Deploy from a branch**
   - 下面出现两个下拉框：左边选 **main**，右边选 **/ (root)**
   - 点 **Save**
5. 页面会刷新，出现一句 "Your site is live at ..." 或者先显示正在构建

**等 1–3 分钟**，刷新这个 Settings → Pages 页面，
顶部会出现一个绿色方框：

```
✓ Your site is live at https://USERNAME.github.io/footprint-map/
```

点 **Visit site**，地图就出来了。

> 也可以在仓库首页右侧的 **Deployments / github-pages** 看部署状态。

## 用 Actions 部署（可选，二选一）

仓库里自带 `.github/workflows/pages.yml`。如果你想要构建日志更清楚、
以后方便加构建步骤，把上面第 4 步的 **Source** 改成 **GitHub Actions** 即可，
之后每次 push 自动发布，进度在仓库顶部的 **Actions** 标签页看。

**两种方式只能开一种**，别同时配。

---

# 八、常见报错对照表

**`command not found: git`**
git 没装或没重启终端。回到 2.1。

**`fatal: not a git repository`**
终端不在项目文件夹里，或者没执行过 `git init`。`pwd` 看看在哪，回到 3.2。

**`! [rejected] main -> main (fetch first)`**
建仓库时勾了 README，远端有你本地没有的提交。执行：

```bash
git pull --rebase origin main
git push -u origin main
```

**`src refspec main does not match any`**
还没 commit 过。回到 5.3 执行 `git commit -m "init"`。

**`remote origin already exists`**
5.5 执行过两次。改成：

```bash
git remote set-url origin https://github.com/USERNAME/footprint-map.git
```

**`Support for password authentication was removed`**
你输的是登录密码。要用 token，回到第六章。

**`Permission denied` / `403`**
token 没勾 `repo` 权限，或者仓库地址里的用户名打错了。
重新生成 token，或 `git remote -v` 核对地址。

**网站打开是 404**
- 刚开 Pages 要等几分钟
- 网址结尾要有斜杠：`.../footprint-map/`
- 仓库必须是 **Public**
- `index.html` 必须在仓库**根目录**，不能套在子文件夹里
  （在 GitHub 仓库首页第一屏就应该看到 `index.html`）

**网页出来了，但切到「省·州」一直转圈**
`data/admin1.js` 没传上去。到 GitHub 仓库点进 `data/` 目录看看在不在。
不在的话：

```bash
git add -f data/admin1.js
git commit -m "add admin1"
git push
```

**本地双击 `index.html` 省级图层加载不出来**
正常现象，`file://` 协议下浏览器会拦截动态加载脚本。本地测试要起个小服务器：

```bash
python3 -m http.server 8000
```

然后浏览器打开 http://localhost:8000 。停止按 `Control + C`。
（`dots.html` 没有这个限制，双击就能开。）

**改了文件但网站没变**
先确认推上去了（`git status` 应该显示 nothing to commit），
然后强制刷新浏览器：Mac `Command + Shift + R`，Windows `Ctrl + F5`。
CDN 缓存有时会顶几分钟。

---

# 九、以后怎么更新

改完任何文件，在项目目录里三连：

```bash
git add .
git commit -m "改了什么"
git push
```

1–2 分钟后网站自动更新。不用再碰 Settings。

---

# 十、上线检查清单

- [ ] `git status` 显示 `nothing to commit, working tree clean`
- [ ] GitHub 仓库首页能看到 `index.html`、`dots.html`、`data/`
- [ ] 仓库是 Public
- [ ] Settings → Pages 显示绿色 "Your site is live at ..."
- [ ] 打开网址，点几个国家能变橙色
- [ ] 切到「省·州」，进度条转一下之后能点省
- [ ] 点「复制分享链接」，在无痕窗口打开，标记还在
- [ ] 手机上打开同一个网址也正常

---

# 附：可选的收尾

**换成更短的网址**
把仓库名改成 `USERNAME.github.io`（必须**精确等于**你的用户名），
网址就变成 `https://USERNAME.github.io/`，不带后缀路径。
一个账号只能有一个这种仓库。改名在 Settings → General → Repository name。

**绑自己的域名**
Settings → Pages → **Custom domain** 填域名 → Save，
然后到域名商后台加一条 CNAME 记录指向 `USERNAME.github.io`。
等十几分钟，回来勾上 **Enforce HTTPS**。

**把 README 里的占位符换掉**

```bash
# macOS 的 sed 必须写成 -i ''
sed -i '' 's/USERNAME/你的用户名/g' README.md
git commit -am "update url"
git push
```

Windows / Linux 用 `sed -i 's/USERNAME/你的用户名/g' README.md`。
