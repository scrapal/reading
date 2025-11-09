# 阅读空间 – 本地原型

一个用于演示的本地网站，当前已具备注册/登录、书籍评论同步、每日任务赚金币以及照顾虚拟宠物等核心流程。

## 快速开始

### 1. 配置 Supabase 数据库

本项目现已迁移到 PostgreSQL，推荐使用 Supabase 云数据库（免费套餐包含 500MB）。

1. 访问 [Supabase](https://supabase.com) 并创建账号
2. 创建新项目（New Project）
3. 在项目设置（Settings → Database）中找到连接字符串（Connection String）
4. 复制 URI 格式的连接字符串（类似 `postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres`）

### 2. 安装依赖
```bash
cd /Users/a8cde/Desktop/reading
python3 -m venv .venv  # 可选，但推荐
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 Supabase 数据库连接字符串
# DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

### 4. 初始化数据库并运行项目
```bash
flask --app app run --debug  # 或 python app.py
```
首次运行会自动在 Supabase 数据库中创建所有表并写入示例书籍与任务。

### 5. 访问
打开浏览器访问 http://127.0.0.1:5000

## 主要功能
- **用户体系**：注册/登录/退出，密码以哈希方式保存在 PostgreSQL 数据库。
- **书籍板块**：展示封面+书名，支持在书页下方发表评论。
- **年级书单**：预置六、七、八年级 24 本推荐图书，包含封面、作者、出版社信息。
- **讨论总板**：任意书页的评论会同步到全站讨论区，并附带返回书页的超链接；页面分为“讨论/读后感”两个板块。
- **评论回复**：支持在书籍页面或讨论区对任意讨论/读后感进行嵌套回复，保持交流上下文；用户可以删除自己发布的评论或回复。
- **每日任务与金币**：预置“读书打卡、写读后感、发布书评”三个任务；每天完成一次即可领取金币。其中“讨论/读后感”任务只能在书籍页面完成（按钮无法直接领取），系统会根据你的发帖类型与字数自动发放奖励。
- **虚拟宠物**：金币可用于喂食、玩耍或送礼，实时更新宠物的饱食度和快乐值；可以自定义宠物昵称并通过玩具装饰草坪。
- **个人设置**：新增设置页面，可修改宠物昵称、头像链接及用户名（7 天限一次）。
- **玩具系统**：在宠物页面花金币购买玩具，它们会实时出现在草坪场景中，营造更生动的互动氛围。
- **后台管理**：首位注册用户自动成为管理员，可在“后台”页面添加/删除书籍、删除任意评论或用户玩具，并为其他账号授予/移除管理员权限、调整金币、甚至删除用户账号。

## 数据与结构
- 数据存储在 **Supabase PostgreSQL** 云数据库，包含 8 张核心表：`users / books / comments / tasks / task_completions / pets / toys / user_toys / comment_replies`。
- `books` 表保存 `author / publisher / grade / cover_url` 字段，可按年级分组展示。
- 所有封面已下载到 `static/covers/*.jpg` 并在 `BOOK_SEED` 中引用（原始图片来源：豆瓣读书）。
- `comments` 表包含 `category` 字段，用户可在书籍页面选择"讨论"或"读后感"，并在总讨论区按板块查看。
- `users` 表包含 `is_admin` 字段，管理员可在后台界面直接切换权限，并可修改任意账号的金币数。
- `toys` / `user_toys` 表记录玩具配置及用户拥有的玩具与摆放位置。
- `comment_replies` 表支持评论的嵌套回复功能。
- 每次启动会确保数据表存在，并自动补全 `books`、`tasks`、`toys` 示例数据。

## 后续可扩展方向
- 为任务、宠物或评论增加更多交互（上传图片、等级系统等）。
- 引入真正的书籍元数据、搜索与推荐。
- 拆分前后端并提供 API 以便移动端/小程序复用。
