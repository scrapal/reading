from __future__ import annotations

import os
import random
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "reading.db"

BOOK_SEED = [
    {
        "slug": "shenghuo-shi-hen-haowan-de",
        "title": "生活，是很好玩的",
        "author": "汪曾祺",
        "publisher": "江西人民出版社",
        "grade": "六年级",
        "cover_url": "/static/covers/shenghuo-shi-hen-haowan-de.jpg",
        "cover_source": "https://img3.doubanio.com/view/subject/l/public/s29113352.jpg",
    },
    {
        "slug": "sushi-qiren",
        "title": "俗世奇人",
        "author": "冯骥才",
        "publisher": "人民文学出版社",
        "grade": "六年级",
        "cover_url": "/static/covers/sushi-qiren.jpg",
        "cover_source": "https://img3.doubanio.com/view/subject/l/public/s27275682.jpg",
    },
    {
        "slug": "tong-nian",
        "title": "童年",
        "author": "[俄] 高尔基",
        "publisher": "人民文学出版社",
        "grade": "六年级",
        "cover_url": "/static/covers/tong-nian.jpg",
        "cover_source": "https://img3.doubanio.com/view/subject/l/public/s2263997.jpg",
    },
    {
        "slug": "tangmu-suoya-lixianji",
        "title": "汤姆·索亚历险记",
        "author": "[美] 马克·吐温",
        "publisher": "人民文学出版社",
        "grade": "六年级",
        "cover_url": "/static/covers/tangmu-suoya-lixianji.jpg",
        "cover_source": "https://img2.doubanio.com/view/subject/l/public/s1537841.jpg",
    },
    {
        "slug": "renjian-zui-mei-shi-qinghuan",
        "title": "人间最美是清欢",
        "author": "林清玄",
        "publisher": "北京十月文艺出版社",
        "grade": "六年级",
        "cover_url": "/static/covers/renjian-zui-mei-shi-qinghuan.jpg",
        "cover_source": "https://img1.doubanio.com/view/subject/l/public/s28512879.jpg",
    },
    {
        "slug": "changan-ke",
        "title": "长安客",
        "author": "北冥鱼",
        "publisher": "天津人民出版社",
        "grade": "六年级",
        "cover_url": "/static/covers/changan-ke.jpg",
        "cover_source": "https://img1.doubanio.com/view/subject/l/public/s33657908.jpg",
    },
    {
        "slug": "caofangzi",
        "title": "草房子",
        "author": "曹文轩",
        "publisher": "中国少年儿童出版社",
        "grade": "六年级",
        "cover_url": "/static/covers/caofangzi.jpg",
        "cover_source": "https://img1.doubanio.com/view/subject/l/public/s2652540.jpg",
    },
    {
        "slug": "lubinxun-piaoliuji",
        "title": "鲁滨逊漂流记",
        "author": "[英] 丹尼尔·笛福",
        "publisher": "人民文学出版社",
        "grade": "六年级",
        "cover_url": "/static/covers/lubinxun-piaoliuji.jpg",
        "cover_source": "https://img3.doubanio.com/view/subject/l/public/s33876762.jpg",
    },
    {
        "slug": "chaohua-xishi",
        "title": "朝花夕拾",
        "author": "鲁迅",
        "publisher": "人民文学出版社",
        "grade": "七年级",
        "cover_url": "/static/covers/chaohua-xishi.jpg",
        "cover_source": "https://img1.doubanio.com/view/subject/l/public/s34099290.jpg",
    },
    {
        "slug": "feiniao-ji",
        "title": "飞鸟集",
        "author": "[印] 泰戈尔",
        "publisher": "译林出版社",
        "grade": "七年级",
        "cover_url": "/static/covers/feiniao-ji.jpg",
        "cover_source": "https://img3.doubanio.com/view/subject/l/public/s1044902.jpg",
    },
    {
        "slug": "maocheng-ji",
        "title": "猫城记",
        "author": "老舍",
        "publisher": "作家出版社",
        "grade": "七年级",
        "cover_url": "/static/covers/maocheng-ji.jpg",
        "cover_source": "https://img1.doubanio.com/view/subject/l/public/s29264220.jpg",
    },
    {
        "slug": "xiyou-ji",
        "title": "西游记",
        "author": "吴承恩",
        "publisher": "人民文学出版社",
        "grade": "七年级",
        "cover_url": "/static/covers/xiyou-ji.jpg",
        "cover_source": "https://img9.doubanio.com/view/subject/l/public/s1627374.jpg",
    },
    {
        "slug": "qianqiu-renwu",
        "title": "千秋人物",
        "author": "梁衡",
        "publisher": "北京联合出版公司",
        "grade": "七年级",
        "cover_url": "/static/covers/qianqiu-renwu.jpg",
        "cover_source": "https://img9.doubanio.com/view/subject/l/public/s28565656.jpg",
    },
    {
        "slug": "kangzhen-shici",
        "title": "康震讲诗词经典",
        "author": "康震",
        "publisher": "中华书局",
        "grade": "七年级",
        "cover_url": "/static/covers/kangzhen-shici.jpg",
        "cover_source": "https://img9.doubanio.com/view/subject/l/public/s29808536.jpg",
    },
    {
        "slug": "wanwu-youqing",
        "title": "万物有情",
        "author": "李汉荣",
        "publisher": "北京联合出版公司",
        "grade": "七年级",
        "cover_url": "/static/covers/wanwu-youqing.jpg",
        "cover_source": "https://img1.doubanio.com/view/subject/l/public/s33306548.jpg",
    },
    {
        "slug": "haidiliangwanli",
        "title": "海底两万里",
        "author": "[法] 儒勒·凡尔纳",
        "publisher": "人民文学出版社",
        "grade": "七年级",
        "cover_url": "/static/covers/haidiliangwanli.jpg",
        "cover_source": "https://img9.doubanio.com/view/subject/l/public/s1817666.jpg",
    },
    {
        "slug": "zhuzhiqing-sanwenji",
        "title": "朱自清散文集",
        "author": "朱自清",
        "publisher": "商务印书馆",
        "grade": "八年级",
        "cover_url": "/static/covers/zhuzhiqing-sanwenji.jpg",
        "cover_source": "https://img3.doubanio.com/view/subject/l/public/s10042853.jpg",
    },
    {
        "slug": "hongxing-zhaoyao-zhongguo",
        "title": "红星照耀中国",
        "author": "[美] 埃德加·斯诺",
        "publisher": "人民教育出版社",
        "grade": "八年级",
        "cover_url": "/static/covers/hongxing-zhaoyao-zhongguo.jpg",
        "cover_source": "https://img2.doubanio.com/view/subject/l/public/s29109031.jpg",
    },
    {
        "slug": "jiangxun-shuo-songci",
        "title": "蒋勋说宋词",
        "author": "蒋勋",
        "publisher": "中信出版社",
        "grade": "八年级",
        "cover_url": "/static/covers/jiangxun-shuo-songci.jpg",
        "cover_source": "https://img1.doubanio.com/view/subject/l/public/s27526958.jpg",
    },
    {
        "slug": "hongyan",
        "title": "红岩",
        "author": "罗广斌 / 杨益言",
        "publisher": "中国青年出版社",
        "grade": "八年级",
        "cover_url": "/static/covers/hongyan.jpg",
        "cover_source": "https://img9.doubanio.com/view/subject/l/public/s21406804.jpg",
    },
    {
        "slug": "fulei-jiashu",
        "title": "傅雷家书",
        "author": "傅雷",
        "publisher": "生活·读书·新知三联书店",
        "grade": "八年级",
        "cover_url": "/static/covers/fulei-jiashu.jpg",
        "cover_source": "https://img9.doubanio.com/view/subject/l/public/s1216085.jpg",
    },
    {
        "slug": "gangtie-shi-zenyang-lianchengde",
        "title": "钢铁是怎样炼成的",
        "author": "[苏] 尼·奥斯特洛夫斯基",
        "publisher": "人民文学出版社",
        "grade": "八年级",
        "cover_url": "/static/covers/gangtie-shi-zenyang-lianchengde.jpg",
        "cover_source": "https://img1.doubanio.com/view/subject/l/public/s2241708.jpg",
    },
    {
        "slug": "leiyu",
        "title": "雷雨",
        "author": "曹禺",
        "publisher": "北京十月文艺出版社",
        "grade": "八年级",
        "cover_url": "/static/covers/leiyu.jpg",
        "cover_source": "https://img3.doubanio.com/view/subject/l/public/s34263503.jpg",
    },
    {
        "slug": "shashibiya-xi-beijuji",
        "title": "莎士比亚喜/悲剧集",
        "author": "[英] 威廉·莎士比亚",
        "publisher": "中央编译出版社",
        "grade": "八年级",
        "cover_url": "/static/covers/shashibiya-xi-beijuji.jpg",
        "cover_source": "https://img3.doubanio.com/view/subject/l/public/s29567432.jpg",
    },
]

GRADE_ORDER = ["六年级", "七年级", "八年级"]
COMMENT_CATEGORIES = {"discussion": "讨论", "reflection": "读后感"}
AUTO_COMMENT_TASKS = {"share_comment", "write_reflection"}
TOY_SEED = [
    {
        "slug": "squan-ball",
        "name": "弹力球",
        "price": 12,
        "icon": "⚽",
        "description": "丢出去就会弹回来，陪宠物玩耍。",
    },
    {
        "slug": "rainbow-windmill",
        "name": "彩虹风车",
        "price": 18,
        "icon": "🌈",
        "description": "转动的风车让草坪更热闹。",
    },
    {
        "slug": "music-box",
        "name": "音乐盒",
        "price": 25,
        "icon": "🎶",
        "description": "播放舒缓音乐，提升快乐值。",
    },
    {
        "slug": "book-pile",
        "name": "迷你书堆",
        "price": 15,
        "icon": "📚",
        "description": "让宠物也沉浸在阅读氛围中。",
    },
]


def slugify(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s_-]+", "-", value)
    value = value.strip("-")
    if not value:
        value = f"book-{int(datetime.now().timestamp())}"
    return value

TASK_SEED = [
    {
        "code": "read_checkin",
        "name": "读书打卡",
        "description": "上传今日阅读进度，保持连续专注。",
        "coins_reward": 10,
    },
    {
        "code": "write_reflection",
        "name": "写读后感",
        "description": "记录不少于 100 字的思考。",
        "coins_reward": 15,
    },
    {
        "code": "share_comment",
        "name": "发布书评/评论",
        "description": "在任意书籍板块发表高质量评论。",
        "coins_reward": 8,
    },
]

PET_ACTIONS = {
    "feed": {
        "label": "喂食",
        "description": "提供营养餐，恢复体力",
        "cost": 10,
        "hunger_delta": -25,
        "happiness_delta": 6,
    },
    "play": {
        "label": "玩耍",
        "description": "互动小游戏，增进感情",
        "cost": 8,
        "hunger_delta": 5,
        "happiness_delta": 12,
    },
    "treat": {
        "label": "送礼物",
        "description": "购买新道具，惊喜不断",
        "cost": 15,
        "hunger_delta": 0,
        "happiness_delta": 18,
    },
}


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
    columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition};")


def seed_books(conn: sqlite3.Connection) -> None:
    for book in BOOK_SEED:
        conn.execute(
            """
            INSERT INTO books (slug, title, cover_url, author, publisher, grade)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                title = excluded.title,
                cover_url = excluded.cover_url,
                author = excluded.author,
                publisher = excluded.publisher,
                grade = excluded.grade
            """,
            (
                book["slug"],
                book["title"],
                book["cover_url"],
                book["author"],
                book["publisher"],
                book["grade"],
            ),
        )


def seed_tasks(conn: sqlite3.Connection) -> None:
    for task in TASK_SEED:
        conn.execute(
            """
            INSERT OR IGNORE INTO tasks (code, name, description, coins_reward)
            VALUES (?, ?, ?, ?)
            """,
            (task["code"], task["name"], task["description"], task["coins_reward"]),
        )


def seed_toys(conn: sqlite3.Connection) -> None:
    for toy in TOY_SEED:
        conn.execute(
            """
            INSERT INTO toys (slug, name, price, icon, description)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                name = excluded.name,
                price = excluded.price,
                icon = excluded.icon,
                description = excluded.description
            """,
            (
                toy["slug"],
                toy["name"],
                toy["price"],
                toy["icon"],
                toy["description"],
            ),
        )


def init_db() -> None:
    DB_PATH.touch(exist_ok=True)
    with get_db_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                coins INTEGER DEFAULT 0,
                avatar TEXT,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                cover_url TEXT,
                author TEXT,
                publisher TEXT,
                grade TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                book_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                coins_reward INTEGER DEFAULT 5
            );

            CREATE TABLE IF NOT EXISTS task_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                completion_date TEXT NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, task_id, completion_date),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL DEFAULT '小书兽',
                hunger INTEGER DEFAULT 50,
                happiness INTEGER DEFAULT 55,
                last_care_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS toys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                icon TEXT,
                description TEXT
            );

            CREATE TABLE IF NOT EXISTS user_toys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                toy_id INTEGER NOT NULL,
                pos_x REAL NOT NULL,
                pos_y REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (toy_id) REFERENCES toys(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS comment_replies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comment_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )
        ensure_column(conn, "users", "coins", "INTEGER DEFAULT 0")
        ensure_column(conn, "users", "avatar", "TEXT")
        ensure_column(conn, "users", "is_admin", "INTEGER DEFAULT 0")
        ensure_column(conn, "users", "language", "TEXT DEFAULT 'zh'")
        ensure_column(conn, "users", "last_username_change", "TIMESTAMP")
        ensure_column(conn, "books", "author", "TEXT")
        ensure_column(conn, "books", "publisher", "TEXT")
        ensure_column(conn, "books", "grade", "TEXT")
        ensure_column(conn, "comments", "category", "TEXT DEFAULT 'discussion'")
        seed_books(conn)
        seed_tasks(conn)
        seed_toys(conn)
        conn.commit()


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

init_db()


def is_logged_in() -> bool:
    return "user_id" in session


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    with get_db_connection() as conn:
        return conn.execute(
            "SELECT id, username, coins, is_admin FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()


def require_admin():
    user = current_user()
    if not user or not user["is_admin"]:
        abort(403)
    return user


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_tasks_status(user_id: int | None):
    with get_db_connection() as conn:
        tasks = conn.execute(
            "SELECT id, name, description, coins_reward FROM tasks ORDER BY id"
        ).fetchall()
        if not user_id:
            return [
                {
                    "task": task,
                    "completed": False,
                }
                for task in tasks
            ]
        completed_rows = conn.execute(
            """
            SELECT task_id FROM task_completions
            WHERE user_id = ? AND completion_date = ?
            """,
            (user_id, today_str()),
        ).fetchall()
    completed_ids = {row["task_id"] for row in completed_rows}
    return [
        {
            "task": task,
            "completed": task["id"] in completed_ids,
        }
        for task in tasks
    ]


def award_task_completion(user_id: int, task_code: str):
    with get_db_connection() as conn:
        task = conn.execute(
            "SELECT id, name, coins_reward FROM tasks WHERE code = ?",
            (task_code,),
        ).fetchone()
        if not task:
            return None

        today = today_str()
        try:
            conn.execute(
                """
                INSERT INTO task_completions (user_id, task_id, completion_date)
                VALUES (?, ?, ?)
                """,
                (user_id, task["id"], today),
            )
        except sqlite3.IntegrityError:
            return None

        conn.execute(
            "UPDATE users SET coins = coins + ? WHERE id = ?",
            (task["coins_reward"], user_id),
        )
        conn.commit()
        return task


def clamp(value: int, min_value: int = 0, max_value: int = 100) -> int:
    return max(min_value, min(max_value, value))


def normalize_category(value: str | None) -> str:
    value = (value or "").lower()
    return value if value in COMMENT_CATEGORIES else "discussion"


def group_comments(rows: list[sqlite3.Row]):
    grouped = {key: [] for key in COMMENT_CATEGORIES}
    for row in rows:
        grouped[normalize_category(row["category"] )].append(row)
    return grouped


def get_user_toys(user_id: int):
    with get_db_connection() as conn:
        return conn.execute(
            """
            SELECT user_toys.id, user_toys.pos_x, user_toys.pos_y, user_toys.created_at,
                   toys.name, toys.icon, toys.slug
            FROM user_toys
            JOIN toys ON toys.id = user_toys.toy_id
            WHERE user_toys.user_id = ?
            ORDER BY user_toys.created_at DESC
            """,
            (user_id,),
        ).fetchall()


def get_available_toys(user_id: int | None):
    with get_db_connection() as conn:
        toys = conn.execute(
            "SELECT id, slug, name, price, icon, description FROM toys ORDER BY price"
        ).fetchall()
        if not user_id:
            return toys
        owned_counts = conn.execute(
            "SELECT toy_id, COUNT(*) as cnt FROM user_toys WHERE user_id = ? GROUP BY toy_id",
            (user_id,),
        ).fetchall()
    owned_map = {row["toy_id"]: row["cnt"] for row in owned_counts}
    result = []
    for toy in toys:
        result.append({
            "id": toy["id"],
            "slug": toy["slug"],
            "name": toy["name"],
            "price": toy["price"],
            "icon": toy["icon"],
            "description": toy["description"],
            "owned": owned_map.get(toy["id"], 0),
        })
    return result


def get_all_user_toys(limit: int = 50):
    with get_db_connection() as conn:
        return conn.execute(
            """
            SELECT user_toys.id, user_toys.pos_x, user_toys.pos_y, user_toys.created_at,
                   users.username, users.id AS owner_id,
                   toys.name AS toy_name, toys.icon
            FROM user_toys
            JOIN users ON users.id = user_toys.user_id
            JOIN toys ON toys.id = user_toys.toy_id
            ORDER BY user_toys.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


def get_comment_replies(comment_ids: list[int]):
    if not comment_ids:
        return {}
    placeholders = ",".join(["?"] * len(comment_ids))
    with get_db_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT comment_replies.id, comment_replies.comment_id, comment_replies.content,
                   comment_replies.created_at, users.username
            FROM comment_replies
            JOIN users ON users.id = comment_replies.user_id
            WHERE comment_replies.comment_id IN ({placeholders})
            ORDER BY comment_replies.created_at ASC
            """,
            tuple(comment_ids),
        ).fetchall()
    grouped: dict[int, list[sqlite3.Row]] = {cid: [] for cid in comment_ids}
    for row in rows:
        grouped.setdefault(row["comment_id"], []).append(row)
    return grouped


def redirect_to(next_url: str | None, fallback: str):
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect(fallback)


@app.template_filter("friendly_date")
def friendly_date(value: str | None) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d")
    except ValueError:
        return value


@app.context_processor
def inject_globals():
    return {"category_labels": COMMENT_CATEGORIES}


@app.route("/")
def index():
    user = current_user()
    with get_db_connection() as conn:
        featured_books = conn.execute(
            """
            SELECT id, title, slug, cover_url, author, grade
            FROM books
            ORDER BY id
            LIMIT 4
            """
        ).fetchall()
        latest_comments = conn.execute(
            """
            SELECT comments.content, comments.created_at, comments.category,
                   users.username, books.title, books.slug
            FROM comments
            JOIN users ON users.id = comments.user_id
            JOIN books ON books.id = comments.book_id
            ORDER BY comments.created_at DESC
            LIMIT 5
            """
        ).fetchall()
    tasks_overview = get_tasks_status(user["id"]) if user else get_tasks_status(None)
    return render_template(
        "index.html",
        user=user,
        coins=user["coins"] if user else 0,
        tasks_overview=tasks_overview,
        featured_books=featured_books,
        latest_comments=latest_comments,
    )


@app.route("/books")
def books():
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, title, slug, cover_url, author, publisher, grade
            FROM books
            ORDER BY CASE grade
                WHEN '六年级' THEN 0
                WHEN '七年级' THEN 1
                WHEN '八年级' THEN 2
                ELSE 3 END, title
            """
        ).fetchall()

    grouped: dict[str, list[sqlite3.Row]] = {}
    for row in rows:
        grade = row["grade"] or "未分级"
        grouped.setdefault(grade, []).append(row)

    ordered_grades = [grade for grade in GRADE_ORDER if grade in grouped]
    ordered_grades.extend([grade for grade in grouped if grade not in ordered_grades])

    return render_template(
        "books.html",
        grouped_books=grouped,
        grade_order=ordered_grades,
    )


@app.route("/books/<slug>", methods=["GET", "POST"])
def book_detail(slug: str):
    with get_db_connection() as conn:
        book = conn.execute(
            """
            SELECT id, title, slug, cover_url, author, publisher, grade
            FROM books
            WHERE slug = ?
            """,
            (slug,),
        ).fetchone()
        if not book:
            abort(404)

        if request.method == "POST":
            if not is_logged_in():
                flash("请先登录再发表评论。", "error")
                return redirect(url_for("login"))

            content = request.form.get("content", "").strip()
            if not content:
                flash("评论内容不能为空。", "error")
                return redirect(url_for("book_detail", slug=slug))

            category = normalize_category(request.form.get("category"))
            conn.execute(
                """
                INSERT INTO comments (user_id, book_id, content, category)
                VALUES (?, ?, ?, ?)
                """,
                (session["user_id"], book["id"], content, category),
            )
            conn.commit()
            reward_notes = []
            user_id = session["user_id"]
            if category == "discussion":
                awarded = award_task_completion(user_id, "share_comment")
                if awarded:
                    reward_notes.append(
                        f"完成『讨论任务』，获得 {awarded['coins_reward']} 金币。"
                    )
            elif category == "reflection":
                if len(content) >= 50:
                    awarded = award_task_completion(user_id, "write_reflection")
                    if awarded:
                        reward_notes.append(
                            f"完成『读后感任务』，获得 {awarded['coins_reward']} 金币。"
                        )
                else:
                    flash("读后感需不少于 50 字才会计入任务奖励。", "info")

            message = "评论已发布，已同步至讨论板块。"
            if reward_notes:
                message += " " + " ".join(reward_notes)
            flash(message, "success")
            return redirect(url_for("book_detail", slug=slug))

        comments = conn.execute(
            """
            SELECT comments.id, comments.content, comments.created_at, comments.category, users.username
            FROM comments
            JOIN users ON users.id = comments.user_id
            WHERE comments.book_id = ?
            ORDER BY comments.created_at DESC
            """,
            (book["id"],),
        ).fetchall()

    grouped = group_comments(comments)
    replies_map = get_comment_replies([row["id"] for row in comments])
    return render_template(
        "book_detail.html",
        book=book,
        discussion_comments=grouped["discussion"],
        reflection_comments=grouped["reflection"],
        replies_map=replies_map,
    )


@app.route("/discussions")
def discussions():
    with get_db_connection() as conn:
        thread = conn.execute(
            """
            SELECT comments.id, comments.content, comments.created_at, comments.category,
                   users.username, books.title, books.slug
            FROM comments
            JOIN users ON users.id = comments.user_id
            JOIN books ON books.id = comments.book_id
            ORDER BY comments.created_at DESC
            """
        ).fetchall()
    grouped = group_comments(thread)
    replies_map = get_comment_replies([row["id"] for row in thread])
    return render_template(
        "discussions.html",
        discussion_comments=grouped["discussion"],
        reflection_comments=grouped["reflection"],
        replies_map=replies_map,
    )


@app.route("/admin")
def admin_dashboard():
    admin_user = require_admin()
    with get_db_connection() as conn:
        comments = conn.execute(
            """
            SELECT comments.id, comments.content, comments.category, comments.created_at,
                   users.username, books.title, books.slug
            FROM comments
            JOIN users ON users.id = comments.user_id
            JOIN books ON books.id = comments.book_id
            ORDER BY comments.created_at DESC
            LIMIT 50
            """
        ).fetchall()
        users = conn.execute(
            "SELECT id, username, is_admin, created_at, coins FROM users ORDER BY created_at DESC"
        ).fetchall()
        recent_books = conn.execute(
            "SELECT id, title, slug, grade FROM books ORDER BY created_at DESC LIMIT 12"
        ).fetchall()
        user_toys = get_all_user_toys()

    grouped_comments = group_comments(comments)
    all_comment_ids = [row["id"] for row in comments]
    admin_replies = get_comment_replies(all_comment_ids)
    return render_template(
        "admin.html",
        admin=admin_user,
        grade_options=GRADE_ORDER,
        admin_discussions=grouped_comments["discussion"],
        admin_reflections=grouped_comments["reflection"],
        admin_users=users,
        recent_books=recent_books,
        admin_user_toys=user_toys,
        admin_replies=admin_replies,
    )


@app.post("/admin/books/add")
def admin_add_book():
    require_admin()
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    publisher = request.form.get("publisher", "").strip()
    cover_url = request.form.get("cover_url", "").strip() or "https://placehold.co/320x180?text=Book"
    grade = request.form.get("grade", "").strip()
    slug_value = request.form.get("slug", "").strip() or slugify(title)

    if not title:
        flash("书名不能为空。", "error")
        return redirect(url_for("admin_dashboard"))

    if grade and grade not in GRADE_ORDER:
        flash("请选择有效的年级。", "error")
        return redirect(url_for("admin_dashboard"))

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO books (slug, title, cover_url, author, publisher, grade)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                title=excluded.title,
                cover_url=excluded.cover_url,
                author=excluded.author,
                publisher=excluded.publisher,
                grade=excluded.grade
            """,
            (slug_value, title, cover_url, author, publisher, grade or None),
        )
        conn.commit()

    flash("书籍信息已保存。", "success")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/books/<int:book_id>/delete")
def admin_delete_book(book_id: int):
    require_admin()
    with get_db_connection() as conn:
        deleted = conn.execute(
            "DELETE FROM books WHERE id = ?",
            (book_id,),
        )
        conn.commit()

    if deleted.rowcount:
        flash("书籍已删除。", "success")
    else:
        flash("未找到该书籍。", "error")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/comments/<int:comment_id>/delete")
def admin_delete_comment(comment_id: int):
    require_admin()
    with get_db_connection() as conn:
        deleted = conn.execute(
            "DELETE FROM comments WHERE id = ?",
            (comment_id,),
        )
        conn.commit()

    if deleted.rowcount:
        flash("评论已删除。", "success")
    else:
        flash("未找到要删除的评论。", "error")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/users/<int:user_id>/toggle-admin")
def admin_toggle_user(user_id: int):
    current_admin = require_admin()
    with get_db_connection() as conn:
        user = conn.execute(
            "SELECT id, username, is_admin FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not user:
            abort(404)

        if user["is_admin"]:
            admin_count = conn.execute(
                "SELECT COUNT(*) FROM users WHERE is_admin = 1"
            ).fetchone()[0]
            if admin_count <= 1:
                flash("至少需要保留一名管理员。", "error")
                return redirect(url_for("admin_dashboard"))

        new_value = 0 if user["is_admin"] else 1
        conn.execute(
            "UPDATE users SET is_admin = ? WHERE id = ?",
            (new_value, user_id),
        )
        conn.commit()

    if user_id == session.get("user_id"):
        session["is_admin"] = bool(new_value)

    action = "授予" if new_value else "移除"
    flash(f"已{action} {user['username']} 管理员权限。", "success")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/users/<int:user_id>/coins")
def admin_set_coins(user_id: int):
    require_admin()
    try:
        coins_value = int(request.form.get("coins", "0"))
    except ValueError:
        flash("请输入合法的金币数。", "error")
        return redirect(url_for("admin_dashboard"))

    coins_value = max(0, coins_value)
    with get_db_connection() as conn:
        updated = conn.execute(
            "UPDATE users SET coins = ? WHERE id = ?",
            (coins_value, user_id),
        )
        conn.commit()

    if updated.rowcount:
        flash("金币已更新。", "success")
    else:
        flash("未找到该用户。", "error")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/users/<int:user_id>/delete")
def admin_delete_user(user_id: int):
    current_admin = require_admin()
    if user_id == current_admin["id"]:
        flash("不能删除当前登录的管理员账号。", "error")
        return redirect(url_for("admin_dashboard"))

    with get_db_connection() as conn:
        user = conn.execute(
            "SELECT id, username, is_admin FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if not user:
            flash("未找到该用户。", "error")
            return redirect(url_for("admin_dashboard"))

        if user["is_admin"]:
            admin_count = conn.execute(
                "SELECT COUNT(*) FROM users WHERE is_admin = 1"
            ).fetchone()[0]
            if admin_count <= 1:
                flash("至少需要保留一名管理员。", "error")
                return redirect(url_for("admin_dashboard"))

        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

    flash("用户账户已删除。", "success")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/toys/<int:user_toy_id>/delete")
def admin_delete_user_toy(user_toy_id: int):
    require_admin()
    with get_db_connection() as conn:
        deleted = conn.execute(
            "DELETE FROM user_toys WHERE id = ?",
            (user_toy_id,),
        )
        conn.commit()

    if deleted.rowcount:
        flash("玩具已移除。", "success")
    else:
        flash("未找到该玩具记录。", "error")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/replies/<int:reply_id>/delete")
def admin_delete_reply(reply_id: int):
    require_admin()
    with get_db_connection() as conn:
        deleted = conn.execute(
            "DELETE FROM comment_replies WHERE id = ?",
            (reply_id,),
        )
        conn.commit()

    if deleted.rowcount:
        flash("回复已删除。", "success")
    else:
        flash("未找到该回复。", "error")
    return redirect(url_for("admin_dashboard"))


@app.route("/tasks")
def tasks():
    user = current_user()
    task_rows = get_tasks_status(user["id"]) if user else get_tasks_status(None)
    return render_template("tasks.html", user=user, task_rows=task_rows)


@app.post("/tasks/complete/<int:task_id>")
def complete_task(task_id: int):
    if not is_logged_in():
        flash("请先登录再完成任务。", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    with get_db_connection() as conn:
        task = conn.execute(
            "SELECT id, code, name, coins_reward FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        if not task:
            abort(404)

    if task["code"] in AUTO_COMMENT_TASKS:
        flash("该任务需要在书籍页面通过讨论或读后感自动完成。", "error")
        return redirect(url_for("tasks"))

    awarded = award_task_completion(user_id, task["code"])
    if awarded:
        flash(f"任务完成，获得 {awarded['coins_reward']} 金币！", "success")
    else:
        flash("今天已经完成过该任务啦，明天再来！", "info")
    return redirect(url_for("tasks"))


@app.route("/pet", methods=["GET", "POST"])
def pet():
    if not is_logged_in():
        flash("登录后才能照顾宠物。", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    with get_db_connection() as conn:
        user = conn.execute(
            "SELECT id, username, coins FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        pet_row = conn.execute(
            "SELECT * FROM pets WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if not pet_row:
            conn.execute(
                "INSERT INTO pets (user_id, name, hunger, happiness) VALUES (?, ?, 50, 60)",
                (user_id, f"{user['username']}的小兽"),
            )
            conn.commit()
            pet_row = conn.execute(
                "SELECT * FROM pets WHERE user_id = ?",
                (user_id,),
            ).fetchone()

        if request.method == "POST":
            action_key = request.form.get("action")
            action = PET_ACTIONS.get(action_key)
            if not action:
                flash("未知的互动方式。", "error")
                return redirect(url_for("pet"))

            if user["coins"] < action["cost"]:
                flash("金币不足，先去完成任务吧！", "error")
                return redirect(url_for("pet"))

            new_hunger = clamp(pet_row["hunger"] + action["hunger_delta"])
            new_happiness = clamp(pet_row["happiness"] + action["happiness_delta"])

            conn.execute(
                "UPDATE users SET coins = coins - ? WHERE id = ?",
                (action["cost"], user_id),
            )
            conn.execute(
                """
                UPDATE pets
                SET hunger = ?, happiness = ?, last_care_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (new_hunger, new_happiness, pet_row["id"]),
            )
            conn.commit()
            flash(f"{action['label']}完成！宠物状态提升。", "success")
            return redirect(url_for("pet"))

    satiety = clamp(100 - pet_row["hunger"])
    owned_toys = get_user_toys(user_id)
    toy_catalog = get_available_toys(user_id)
    return render_template(
        "pet.html",
        pet=pet_row,
        satiety=satiety,
        coins=user["coins"],
        actions=PET_ACTIONS,
        owned_toys=owned_toys,
        toy_catalog=toy_catalog,
    )


@app.post("/pet/buy/<slug>")
def pet_buy_toy(slug: str):
    if not is_logged_in():
        flash("请先登录。", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    with get_db_connection() as conn:
        toy = conn.execute(
            "SELECT id, name, price FROM toys WHERE slug = ?",
            (slug,),
        ).fetchone()
        user = conn.execute(
            "SELECT coins FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

        if not toy or not user:
            abort(404)

        if user["coins"] < toy["price"]:
            flash("金币不足，先去完成任务吧！", "error")
            return redirect(url_for("pet"))

        pos_x = random.uniform(5, 85)
        pos_y = random.uniform(45, 80)

        conn.execute(
            "UPDATE users SET coins = coins - ? WHERE id = ?",
            (toy["price"], user_id),
        )
        conn.execute(
            "INSERT INTO user_toys (user_id, toy_id, pos_x, pos_y) VALUES (?, ?, ?, ?)",
            (user_id, toy["id"], pos_x, pos_y),
        )
        conn.commit()

    flash(f"已购买 {toy['name']}，它会出现在草坪上！", "success")
    return redirect(url_for("pet"))


@app.post("/comments/<int:comment_id>/reply")
def reply_comment(comment_id: int):
    if not is_logged_in():
        flash("请先登录再回复。", "error")
        return redirect(url_for("login"))

    content = request.form.get("content", "").strip()
    if not content:
        flash("回复内容不能为空。", "error")
        return redirect(request.referrer or url_for("discussions"))

    with get_db_connection() as conn:
        comment = conn.execute(
            """
            SELECT comments.id, books.slug
            FROM comments
            JOIN books ON books.id = comments.book_id
            WHERE comments.id = ?
            """,
            (comment_id,),
        ).fetchone()
        if not comment:
            abort(404)

        conn.execute(
            "INSERT INTO comment_replies (comment_id, user_id, content) VALUES (?, ?, ?)",
            (comment_id, session["user_id"], content),
        )
        conn.commit()

    flash("回复已发布。", "success")
    next_url = request.form.get("next")
    fallback = url_for("book_detail", slug=comment["slug"])
    return redirect_to(next_url, fallback)


@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    if not is_logged_in():
        flash("请先登录。", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    with get_db_connection() as conn:
        user = conn.execute(
            """
            SELECT id, username, coins, is_admin, avatar, language, last_username_change
            FROM users WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
        pet = conn.execute(
            "SELECT name FROM pets WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    if request.method == "POST":
        action = request.form.get("action")
        with get_db_connection() as conn:
            if action == "pet_name":
                new_name = request.form.get("pet_name", "").strip()
                if not (1 <= len(new_name) <= 20):
                    flash("名称长度需在 1-20 个字符内。", "error")
                    return redirect(url_for("settings_page"))
                conn.execute(
                    "INSERT INTO pets (user_id, name) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET name=excluded.name",
                    (user_id, new_name),
                )
                conn.commit()
                flash("宠物昵称已更新！", "success")
            elif action == "avatar":
                avatar_url = request.form.get("avatar", "").strip()
                conn.execute(
                    "UPDATE users SET avatar = ? WHERE id = ?",
                    (avatar_url or None, user_id),
                )
                conn.commit()
                flash("头像链接已更新。", "success")
            elif action == "username":
                new_username = request.form.get("username", "").strip()
                if not (3 <= len(new_username) <= 20):
                    flash("用户名需在 3-20 个字符之间。", "error")
                    return redirect(url_for("settings_page"))
                if new_username == user["username"]:
                    flash("新用户名与当前相同。", "error")
                    return redirect(url_for("settings_page"))
                last_change_raw = user["last_username_change"]
                if last_change_raw:
                    try:
                        last_change = datetime.fromisoformat(last_change_raw)
                    except ValueError:
                        last_change = None
                else:
                    last_change = None
                if last_change and datetime.now() - last_change < timedelta(days=7):
                    flash("用户名每 7 天只能修改一次。", "error")
                    return redirect(url_for("settings_page"))
                exists = conn.execute(
                    "SELECT 1 FROM users WHERE username = ?",
                    (new_username,),
                ).fetchone()
                if exists:
                    flash("该用户名已被占用。", "error")
                    return redirect(url_for("settings_page"))
                conn.execute(
                    "UPDATE users SET username = ?, last_username_change = CURRENT_TIMESTAMP WHERE id = ?",
                    (new_username, user_id),
                )
                conn.commit()
                session["username"] = new_username
                flash("用户名已修改！", "success")
            else:
                flash("未知的设置操作。", "error")
        return redirect(url_for("settings_page"))

    pet_name = pet["name"] if pet else f"{user['username']}的小兽"
    return render_template(
        "settings.html",
        user=user,
        pet_name=pet_name,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("用户名和密码都不能为空。", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("密码不少于6个字符。", "error")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        try:
            with get_db_connection() as conn:
                existing_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                cursor = conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash),
                )
                if existing_count == 0:
                    conn.execute(
                        "UPDATE users SET is_admin = 1 WHERE id = ?",
                        (cursor.lastrowid,),
                    )
                conn.commit()
            flash("注册成功，请登录。", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("用户名已存在，请换一个。", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with get_db_connection() as conn:
            user = conn.execute(
                """
                SELECT id, username, password_hash, coins, is_admin
                FROM users WHERE username = ?
                """,
                (username,),
            ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = bool(user["is_admin"])
            flash("登录成功，开始记录你的阅读吧！", "success")
            return redirect(url_for("index"))

        flash("用户名或密码不正确。", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("你已退出登录。", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
