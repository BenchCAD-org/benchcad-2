# 上手指南 — 写给不用 GitHub 的机械工程师

你**不需要**懂 GitHub。照下面的步骤逐条做即可。English:
[GETTING_STARTED.md](GETTING_STARTED.md)

**黑话一次讲清:** *repo(仓库)* = 放在网上的项目文件夹 · *issue* = 一个讨论帖/工作项 ·
*assign(认领)* = 把你的名字挂上去 · *fork* = 复制一份项目到你名下 ·
*PR(pull request)* = "请审核并收录我的文件夹" · *CI* = 自动检查机器人 · *merge* = 收录通过。

---

## 路径 0 — 只出工程知识,零代码(约 15 分钟)

你懂零件、标准和选型手册——这就是最值钱的那一半,代码我们来写。

1. 在 github.com 注册免费账号(邮箱+密码,和普通网站一样)。
2. 打开 [family issue 列表](../../../issues?q=is%3Aissue+is%3Aopen+label%3Afamily),每个帖子是一个我们想要的机械零件。
3. 点开你熟的零件(没有的话点 **New issue** 新建,标题写 `[family] 零件名`)。
4. 回帖,内容包含:
   - **datasheet 或选型手册链接**(诺锐来姆/米思米/怡合达/标准表格…)
   - **一张图**——把 datasheet 工程图截图或零件照片直接拖进评论框
   - **参数表**(哪些尺寸是变量、各自范围)
   - **工程约束,用大白话写**——"老师傅一眼毙掉"的规则(比如
     *"螺栓孔中心到板边必须 ≥1.5 倍孔径,否则拉脱"*)。这些规则就是全部重点。
5. 完事。维护者把它变成代码;**数据集和论文上都署你的名**(见 CONTRIBUTING.md 规则 9)。

## 路径 1 — 完整贡献,自己写代码(约半天,需基础 Python)

### 一次性环境(约 15 分钟)

1. GitHub 账号(同上),登录。
2. 装 **git**:macOS 自带(终端里敲 `git` 试试);Windows 到 git-scm.com 装
   "Git for Windows",之后用它带的 "Git Bash" 程序操作。
3. 装 **uv**(Python 环境管理器,一行命令,来自 astral.sh/uv):
   `curl -LsSf https://astral.sh/uv/install.sh | sh`
4. 在本仓库页面右上角点 **Fork** → Create fork(复制一份到你名下)。
5. 终端里:
   ```bash
   git clone https://github.com/<你的用户名>/benchcad-2.git
   cd benchcad-2
   uv sync        # 一次性装好全部依赖,几分钟
   ```

### 认领 → 做 → 自查(核心循环)

6. 在 [family issue 列表](../../../issues?q=is%3Aissue+is%3Aopen+label%3Afamily) 打开你想做的零件
   → 右侧栏 **Assignees → assign yourself**(或直接回帖"我来做")。
   挂上名字后这个零件就是你的,别人不会动。
7. 生成骨架:
   ```bash
   uv run bench2 new my_family
   ```
8. 填 `designs/my_family/` 下的两个文件 `part.py` 和 `spec.py`,用工程师的话说:
   - `build(...)`(在 `part.py`)—— 零件本体:具名参数 → 实体,用普通 CadQuery 写(把形状建出来)
   - `PARAM_SPEC`(在 `spec.py`)—— **参数表**(名称、单位、每档难度的范围、**范围出处**:标准表格或"比例惯例")
   - `check(p)`(在 `spec.py`)—— **否决规则**(哪些参数组合不可制造,每条写清理由)。人工评审读的就是这个。
   - `refine(p, difficulty, rng)`(在 `spec.py`)—— **仅当**参数之间有耦合(某个值由其它值算出,或整行取自标准表);抽样由框架自己完成,你不用手写生成器
   `bench2 new` 生成的文件已经用 TODO 标出每个必填项。再填
   `family.json`(标签);如果零件依赖尺寸表或公式,用 `NOTES.md` 记录
   来源符号 → 参数 → 公式的映射。
9. 自查,两条命令,本机秒出结果:
   ```bash
   uv run bench2 validate my_family   # PASS = 你的代码没问题,这就是标准
   uv run bench2 preview my_family    # 渲染 preview.png + preview_views.png
   ```
   `preview_views.png` 是**模型将看到的 4 个视角**——拿它和 issue 里的
   datasheet 工程图并排对照。改到 PASS、渲染像真零件为止。

### 提交

10. ```bash
    git add designs/my_family
    git commit -s -m "Add my_family"     # -s 会加署名行(必须)
    git push
    ```
11. 回到你 fork 的网页——顶部有黄条 **"Compare & pull request"**,点它。
    描述里写一句 `Closes #<对应 issue 编号>`,点 **Create pull request**。
12. 机器人自动跑和你本地一样的检查(绿勾=通过)并贴出你的 preview 图。
    然后一位真人**只审两件事**:你的约束是不是真的、标签对不对。
13. 如果被要求修改:在本地改同样的文件,然后
    `git add … && git commit -s -m "fix" && git push` —— PR 会自动更新。
    **千万不要为改动重开一个新 PR。**
14. Merge = 完成。署名自动兑现(CONTRIBUTORS.md、数据卡、论文共同作者)。
    之后的事(实例生成、难度筛选、发布)全自动——在 [STATUS.md](../STATUS.md)
    看你的零件走到哪一站。merge 之后你什么都不用做。

## 出问题了怎么办

- **CI 红叉 ✗** → 点旁边的 "Details",日志最后几行写着哪道门没过——和本地
  `bench2 validate` 的输出一模一样。
- **"DCO" 检查红了** → commit 缺署名:执行
  `git commit --amend -s --no-edit && git push --force-with-lease`。
- **validate 报 "sample violates check"** → 你的参数范围和约束打架了;
  调范围或改规则(**别为了通过而删掉规则**——评审第一眼看的就是规则)。
- **卡住超过 20 分钟** → 在你的 issue 下面留言,会有人在帖子里回复。
  (不需要私聊——所有事都发生在 issue 里,见 CONTRIBUTING.md 规则 7。)
