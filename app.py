from __future__ import annotations

import os
import sqlite3
from datetime import datetime
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
        "cover_url": "https://img3.doubanio.com/view/subject/l/public/s29113352.jpg",
    },
    {
        "slug": "sushi-qiren",
        "title": "俗世奇人",
        "author": "冯骥才",
        "publisher": "人民文学出版社",
        "grade": "六年级",
        "cover_url": "https://img3.doubanio.com/view/subject/l/public/s27275682.jpg",
    },
    {
        "slug": "tong-nian",
        "title": "童年",
        "author": "[俄] 高尔基",
        "publisher": "人民文学出版社",
        "grade": "六年级",
        "cover_url": "https://img3.doubanio.com/view/subject/l/public/s2263997.jpg",
    },
    {
        "slug": "tangmu-suoya-lixianji",
        "title": "汤姆·索亚历险记",
        "author": "[美] 马克·吐温",
        "publisher": "人民文学出版社",
        "grade": "六年级",
        "cover_url": "https://img2.doubanio.com/view/subject/l/public/s1537841.jpg",
    },
    {
        "slug": "renjian-zui-mei-shi-qinghuan",
        "title": "人间最美是清欢",
        "author": "林清玄",
        "publisher": "北京十月文艺出版社",
        "grade": "六年级",
        "cover_url": "https://img1.doubanio.com/view/subject/l/public/s28512879.jpg",
    },
    {
        "slug": "changan-ke",
        "title": "长安客",
        "author": "北冥鱼",
        "publisher": "天津人民出版社",
        "grade": "六年级",
        "cover_url": "https://img1.doubanio.com/view/subject/l/public/s33657908.jpg",
    },
    {
        "slug": "caofangzi",
        "title": "草房子",
        "author": "曹文轩",
        "publisher": "中国少年儿童出版社",
        "grade": "六年级",
        "cover_url": "https://img1.doubanio.com/view/subject/l/public/s2652540.jpg",
    },
    {
        "slug": "lubinxun-piaoliuji",
        "title": "鲁滨逊漂流记",
        "author": "[英] 丹尼尔·笛福",
        "publisher": "人民文学出版社",
        "grade": "六年级",
        "cover_url": "https://img3.doubanio.com/view/subject/l/public/s33876762.jpg",
    },
    {
        "slug": "chaohua-xishi",
        "title": "朝花夕拾",
        "author": "鲁迅",
        "publisher": "人民文学出版社",
        "grade": "七年级",
        "cover_url": "https://img1.doubanio.com/view/subject/l/public/s34099290.jpg",
    },
    {
        "slug": "feiniao-ji",
        "title": "飞鸟集",
        "author": "[印] 泰戈尔",
        "publisher": "译林出版社",
        "grade": "七年级",
        "cover_url": "https://img3.doubanio.com/view/subject/l/public/s1044902.jpg",
    },
    {
        "slug": "maocheng-ji",
        "title": "猫城记",
        "author": "老舍",
        "publisher": "作家出版社",
        "grade": "七年级",
        "cover_url": "https://img1.doubanio.com/view/subject/l/public/s29264220.jpg",
    },
    {
        "slug": "xiyou-ji",
        "title": "西游记",
        "author": "吴承恩",
        "publisher": "人民文学出版社",
        "grade": "七年级",
        "cover_url": "https://img9.doubanio.com/view/subject/l/public/s1627374.jpg",
    },
    {
        "slug": "qianqiu-renwu",
        "title": "千秋人物",
        "author": "梁衡",
        "publisher": "北京联合出版公司",
        "grade": "七年级",
        "cover_url": "https://img9.doubanio.com/view/subject/l/public/s28565656.jpg",
    },
    {
        "slug": "kangzhen-shici",
        "title": "康震讲诗词经典",
        "author": "康震",
        "publisher": "中华书局",
        "grade": "七年级",
        "cover_url": "https://img9.doubanio.com/view/subject/l/public/s29808536.jpg",
    },
    {
        "slug": "wanwu-youqing",
        "title": "万物有情",
        "author": "李汉荣",
        "publisher": "北京联合出版公司",
        "grade": "七年级",
        "cover_url": "https://img1.doubanio.com/view/subject/l/public/s33306548.jpg",
    },
    {
        "slug": "haidiliangwanli",
        "title": "海底两万里",
        "author": "[法] 儒勒·凡尔纳",
        "publisher": "人民文学出版社",
        "grade": "七年级",
        "cover_url": "https://img9.doubanio.com/view/subject/l/public/s1817666.jpg",
    },
    {
        "slug": "zhuzhiqing-sanwenji",
        "title": "朱自清散文集",
        "author": "朱自清",
        "publisher": "商务印书馆",
        "grade": "八年级",
        "cover_url": "https://img3.doubanio.com/view/subject/l/public/s10042853.jpg",
    },
    {
        "slug": "hongxing-zhaoyao-zhongguo",
        "title": "红星照耀中国",
        "author": "[美] 埃德加·斯诺",
        "publisher": "人民教育出版社",
        "grade": "八年级",
        "cover_url": "https://img2.doubanio.com/view/subject/l/public/s29109031.jpg",
    },
    {
        "slug": "jiangxun-shuo-songci",
        "title": "蒋勋说宋词",
        "author": "蒋勋",
        "publisher": "中信出版社",
        "grade": "八年级",
        "cover_url": "https://img1.doubanio.com/view/subject/l/public/s27526958.jpg",
    },
    {
        "slug": "hongyan",
        "title": "红岩",
        "author": "罗广斌 / 杨益言",
        "publisher": "中国青年出版社",
        "grade": "八年级",
        "cover_url": "https://img9.doubanio.com/view/subject/l/public/s21406804.jpg",
    },
    {
        "slug": "fulei-jiashu",
        "title": "傅雷家书",
        "author": "傅雷",
        "publisher": "生活·读书·新知三联书店",
        "grade": "八年级",
        "cover_url": "https://img9.doubanio.com/view/subject/l/public/s1216085.jpg",
    },
    {
        "slug": "gangtie-shi-zenyang-lianchengde",
        "title": "钢铁是怎样炼成的",
        "author": "[苏] 尼·奥斯特洛夫斯基",
        "publisher": "人民文学出版社",
        "grade": "八年级",
        "cover_url": "https://img1.doubanio.com/view/subject/l/public/s2241708.jpg",
    },
    {
        "slug": "leiyu",
        "title": "雷雨",
        "author": "曹禺",
        "publisher": "北京十月文艺出版社",
        "grade": "八年级",
        "cover_url": "https://img3.doubanio.com/view/subject/l/public/s34263503.jpg",
    },
    {
        "slug": "shashibiya-xi-beijuji",
        "title": "莎士比亚喜/悲剧集",
        "author": "[英] 威廉·莎士比亚",
        "publisher": "中央编译出版社",
        "grade": "八年级",
        "cover_url": "https://img3.doubanio.com/view/subject/l/public/s29567432.jpg",
    },
]

GRADE_ORDER = ["六年级", "七年级", "八年级"]

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
    valid_slugs = {book["slug"] for book in BOOK_SEED}
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

    if valid_slugs:
        placeholders = ",".join(["?"] * len(valid_slugs))
        conn.execute(
            f"DELETE FROM books WHERE slug NOT IN ({placeholders})",
            tuple(valid_slugs),
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
            """
        )
        ensure_column(conn, "users", "coins", "INTEGER DEFAULT 0")
        ensure_column(conn, "users", "avatar", "TEXT")
        ensure_column(conn, "books", "author", "TEXT")
        ensure_column(conn, "books", "publisher", "TEXT")
        ensure_column(conn, "books", "grade", "TEXT")
        seed_books(conn)
        seed_tasks(conn)
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
        return conn.execute("SELECT id, username, coins FROM users WHERE id = ?", (user_id,)).fetchone()


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


def clamp(value: int, min_value: int = 0, max_value: int = 100) -> int:
    return max(min_value, min(max_value, value))


@app.template_filter("friendly_date")
def friendly_date(value: str | None) -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value).strftime("%Y-%m-%d")
    except ValueError:
        return value


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
            SELECT comments.content, comments.created_at, users.username, books.title, books.slug
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

            conn.execute(
                "INSERT INTO comments (user_id, book_id, content) VALUES (?, ?, ?)",
                (session["user_id"], book["id"], content),
            )
            conn.commit()
            flash("评论已发布，已同步至讨论板块。", "success")
            return redirect(url_for("book_detail", slug=slug))

        comments = conn.execute(
            """
            SELECT comments.content, comments.created_at, users.username
            FROM comments
            JOIN users ON users.id = comments.user_id
            WHERE comments.book_id = ?
            ORDER BY comments.created_at DESC
            """,
            (book["id"],),
        ).fetchall()

    return render_template("book_detail.html", book=book, comments=comments)


@app.route("/discussions")
def discussions():
    with get_db_connection() as conn:
        thread = conn.execute(
            """
            SELECT comments.content, comments.created_at, users.username, books.title, books.slug
            FROM comments
            JOIN users ON users.id = comments.user_id
            JOIN books ON books.id = comments.book_id
            ORDER BY comments.created_at DESC
            """
        ).fetchall()
    return render_template("discussions.html", comments=thread)


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
    today = today_str()
    with get_db_connection() as conn:
        task = conn.execute(
            "SELECT id, name, coins_reward FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        if not task:
            abort(404)

        try:
            conn.execute(
                "INSERT INTO task_completions (user_id, task_id, completion_date) VALUES (?, ?, ?)",
                (user_id, task_id, today),
            )
        except sqlite3.IntegrityError:
            flash("今天已经完成过该任务啦，明天再来！", "info")
            return redirect(url_for("tasks"))

        conn.execute(
            "UPDATE users SET coins = coins + ? WHERE id = ?",
            (task["coins_reward"], user_id),
        )
        conn.commit()

    flash(f"任务完成，获得 {task['coins_reward']} 金币！", "success")
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
    return render_template(
        "pet.html",
        pet=pet_row,
        satiety=satiety,
        coins=user["coins"],
        actions=PET_ACTIONS,
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
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash),
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
                "SELECT id, username, password_hash, coins FROM users WHERE username = ?",
                (username,),
            ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
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
