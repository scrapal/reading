from __future__ import annotations

import os
import random
import re
from datetime import datetime, timedelta
from pathlib import Path

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
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
from werkzeug.utils import secure_filename

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL")
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

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


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, subfolder: str = "") -> str | None:
    """Save uploaded file and return the URL path, or None if failed."""
    if not file or file.filename == "":
        return None

    if not allowed_file(file.filename):
        return None

    # Create upload directory if it doesn't exist
    upload_dir = UPLOAD_FOLDER / subfolder if subfolder else UPLOAD_FOLDER
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    filename = secure_filename(file.filename)
    timestamp = int(datetime.now().timestamp())
    name, ext = os.path.splitext(filename)
    unique_filename = f"{name}_{timestamp}{ext}"

    filepath = upload_dir / unique_filename
    file.save(str(filepath))

    # Return URL path
    if subfolder:
        return f"/static/uploads/{subfolder}/{unique_filename}"
    return f"/static/uploads/{unique_filename}"

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

PET_APPEARANCES = [
    {
        "id": "cat-orange",
        "name": "橙色小猫",
        "color": "#FF8C42",
        "svg": '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="55" r="30" fill="currentColor"/><path d="M25 35 L20 15 L35 30 Z" fill="currentColor"/><path d="M75 35 L80 15 L65 30 Z" fill="currentColor"/><circle cx="42" cy="50" r="3" fill="#000"/><circle cx="58" cy="50" r="3" fill="#000"/><path d="M45 60 Q50 65 55 60" stroke="#000" stroke-width="2" fill="none"/></svg>'
    },
    {
        "id": "cat-blue",
        "name": "蓝色小猫",
        "color": "#4A90E2",
        "svg": '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="55" r="30" fill="currentColor"/><path d="M25 35 L20 15 L35 30 Z" fill="currentColor"/><path d="M75 35 L80 15 L65 30 Z" fill="currentColor"/><circle cx="42" cy="50" r="3" fill="#000"/><circle cx="58" cy="50" r="3" fill="#000"/><path d="M45 60 Q50 65 55 60" stroke="#000" stroke-width="2" fill="none"/></svg>'
    },
    {
        "id": "dog-brown",
        "name": "棕色小狗",
        "color": "#A0826D",
        "svg": '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="55" r="30" fill="currentColor"/><ellipse cx="25" cy="50" rx="8" ry="15" fill="currentColor"/><ellipse cx="75" cy="50" rx="8" ry="15" fill="currentColor"/><circle cx="42" cy="50" r="3" fill="#000"/><circle cx="58" cy="50" r="3" fill="#000"/><ellipse cx="50" cy="58" rx="4" ry="5" fill="#000"/><path d="M50 63 L45 70" stroke="#000" stroke-width="2"/><path d="M50 63 L55 70" stroke="#000" stroke-width="2"/></svg>'
    },
    {
        "id": "dog-pink",
        "name": "粉色小狗",
        "color": "#FFB6C1",
        "svg": '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="55" r="30" fill="currentColor"/><ellipse cx="25" cy="50" rx="8" ry="15" fill="currentColor"/><ellipse cx="75" cy="50" rx="8" ry="15" fill="currentColor"/><circle cx="42" cy="50" r="3" fill="#000"/><circle cx="58" cy="50" r="3" fill="#000"/><ellipse cx="50" cy="58" rx="4" ry="5" fill="#000"/><path d="M50 63 L45 70" stroke="#000" stroke-width="2"/><path d="M50 63 L55 70" stroke="#000" stroke-width="2"/></svg>'
    },
    {
        "id": "rabbit-white",
        "name": "白色兔子",
        "color": "#F5F5F5",
        "svg": '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><ellipse cx="50" cy="60" rx="25" ry="28" fill="currentColor" stroke="#DDD" stroke-width="2"/><ellipse cx="38" cy="25" rx="8" ry="22" fill="currentColor" stroke="#DDD" stroke-width="2"/><ellipse cx="62" cy="25" rx="8" ry="22" fill="currentColor" stroke="#DDD" stroke-width="2"/><circle cx="42" cy="55" r="3" fill="#000"/><circle cx="58" cy="55" r="3" fill="#000"/><circle cx="50" cy="65" r="3" fill="#FFB6C1"/></svg>'
    },
    {
        "id": "rabbit-purple",
        "name": "紫色兔子",
        "color": "#9B59B6",
        "svg": '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><ellipse cx="50" cy="60" rx="25" ry="28" fill="currentColor"/><ellipse cx="38" cy="25" rx="8" ry="22" fill="currentColor"/><ellipse cx="62" cy="25" rx="8" ry="22" fill="currentColor"/><circle cx="42" cy="55" r="3" fill="#000"/><circle cx="58" cy="55" r="3" fill="#000"/><circle cx="50" cy="65" r="3" fill="#FFF"/></svg>'
    },
    {
        "id": "bear-brown",
        "name": "棕色小熊",
        "color": "#8B4513",
        "svg": '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="55" r="30" fill="currentColor"/><circle cx="30" cy="35" r="12" fill="currentColor"/><circle cx="70" cy="35" r="12" fill="currentColor"/><circle cx="42" cy="50" r="3" fill="#000"/><circle cx="58" cy="50" r="3" fill="#000"/><ellipse cx="50" cy="60" rx="5" ry="6" fill="#D2691E"/><path d="M45 66 Q50 70 55 66" stroke="#000" stroke-width="2" fill="none"/></svg>'
    },
    {
        "id": "bear-green",
        "name": "绿色小熊",
        "color": "#52C41A",
        "svg": '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="55" r="30" fill="currentColor"/><circle cx="30" cy="35" r="12" fill="currentColor"/><circle cx="70" cy="35" r="12" fill="currentColor"/><circle cx="42" cy="50" r="3" fill="#000"/><circle cx="58" cy="50" r="3" fill="#000"/><ellipse cx="50" cy="60" rx="5" ry="6" fill="#A8E6A1"/><path d="M45 66 Q50 70 55 66" stroke="#000" stroke-width="2" fill="none"/></svg>'
    },
    {
        "id": "penguin-black",
        "name": "企鹅宝宝",
        "color": "#2C3E50",
        "svg": '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><ellipse cx="50" cy="55" rx="28" ry="35" fill="currentColor"/><ellipse cx="50" cy="60" rx="20" ry="28" fill="#FFF"/><circle cx="42" cy="45" r="3" fill="#000"/><circle cx="58" cy="45" r="3" fill="#000"/><path d="M47 52 L53 52 L50 56 Z" fill="#FFA500"/><ellipse cx="25" cy="60" rx="6" ry="15" fill="currentColor"/><ellipse cx="75" cy="60" rx="6" ry="15" fill="currentColor"/></svg>'
    },
    {
        "id": "bird-yellow",
        "name": "黄色小鸟",
        "color": "#FFD700",
        "svg": '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="55" cy="50" r="25" fill="currentColor"/><circle cx="48" cy="45" r="3" fill="#000"/><circle cx="62" cy="45" r="3" fill="#000"/><path d="M52 52 L58 52 L55 56 Z" fill="#FF8C00"/><ellipse cx="25" cy="55" rx="18" ry="8" fill="currentColor" transform="rotate(-20 25 55)"/><ellipse cx="85" cy="55" rx="18" ry="8" fill="currentColor" transform="rotate(20 85 55)"/><path d="M55 75 L50 85 L52 75 L48 85 L55 75" fill="currentColor"/></svg>'
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


def get_db_connection():
    import time
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                DATABASE_URL,
                connect_timeout=30,
                keepalives=1,
                keepalives_idle=30,
                keepalives_interval=10,
                keepalives_count=5
            )
            conn.cursor_factory = psycopg2.extras.RealDictCursor
            return conn
        except psycopg2.OperationalError as e:
            if attempt < max_retries - 1:
                print(f"连接失败，{3-attempt} 秒后重试... (尝试 {attempt + 1}/{max_retries})")
                time.sleep(3)
            else:
                raise


def ensure_column(conn, table: str, column: str, definition: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
            """,
            (table, column),
        )
        if not cur.fetchone():
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def seed_books(conn) -> None:
    with conn.cursor() as cur:
        for book in BOOK_SEED:
            cur.execute(
                """
                INSERT INTO books (slug, title, cover_url, author, publisher, grade)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT(slug) DO UPDATE SET
                    title = EXCLUDED.title,
                    cover_url = EXCLUDED.cover_url,
                    author = EXCLUDED.author,
                    publisher = EXCLUDED.publisher,
                    grade = EXCLUDED.grade
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


def seed_tasks(conn) -> None:
    with conn.cursor() as cur:
        for task in TASK_SEED:
            cur.execute(
                """
                INSERT INTO tasks (code, name, description, coins_reward)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (code) DO NOTHING
                """,
                (task["code"], task["name"], task["description"], task["coins_reward"]),
            )


def seed_toys(conn) -> None:
    with conn.cursor() as cur:
        for toy in TOY_SEED:
            cur.execute(
                """
                INSERT INTO toys (slug, name, price, icon, description)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT(slug) DO UPDATE SET
                    name = EXCLUDED.name,
                    price = EXCLUDED.price,
                    icon = EXCLUDED.icon,
                    description = EXCLUDED.description
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
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    coins INTEGER DEFAULT 0,
                    avatar TEXT,
                    is_admin INTEGER DEFAULT 0,
                    language TEXT DEFAULT 'zh',
                    last_username_change TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    slug TEXT UNIQUE NOT NULL,
                    cover_url TEXT,
                    author TEXT,
                    publisher TEXT,
                    grade TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS comments (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'discussion',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    code TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    coins_reward INTEGER DEFAULT 5
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS task_completions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    task_id INTEGER NOT NULL,
                    completion_date TEXT NOT NULL,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (user_id, task_id, completion_date),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS pets (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL DEFAULT '小书兽',
                    hunger INTEGER DEFAULT 50,
                    happiness INTEGER DEFAULT 55,
                    last_care_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS toys (
                    id SERIAL PRIMARY KEY,
                    slug TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL,
                    icon TEXT,
                    description TEXT
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_toys (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    toy_id INTEGER NOT NULL,
                    pos_x REAL NOT NULL,
                    pos_y REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (toy_id) REFERENCES toys(id) ON DELETE CASCADE
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS comment_replies (
                    id SERIAL PRIMARY KEY,
                    comment_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS book_requests (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    author TEXT,
                    publisher TEXT,
                    grade TEXT,
                    cover_url TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at TIMESTAMP,
                    reviewed_by INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL
                )
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
        ensure_column(conn, "pets", "appearance", "TEXT DEFAULT 'cat-orange'")
        seed_books(conn)
        seed_tasks(conn)
        seed_toys(conn)
        conn.commit()
    finally:
        conn.close()


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
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, coins, is_admin FROM users WHERE id = %s",
                (user_id,),
            )
            return cur.fetchone()


def require_admin():
    user = current_user()
    if not user or not user["is_admin"]:
        abort(403)
    return user


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def get_tasks_status(user_id: int | None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, description, coins_reward FROM tasks ORDER BY id"
            )
            tasks = cur.fetchall()
            if not user_id:
                return [
                    {
                        "task": task,
                        "completed": False,
                    }
                    for task in tasks
                ]
            cur.execute(
                """
                SELECT task_id FROM task_completions
                WHERE user_id = %s AND completion_date = %s
                """,
                (user_id, today_str()),
            )
            completed_rows = cur.fetchall()
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
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, coins_reward FROM tasks WHERE code = %s",
                (task_code,),
            )
            task = cur.fetchone()
            if not task:
                return None

            today = today_str()
            try:
                cur.execute(
                    """
                    INSERT INTO task_completions (user_id, task_id, completion_date)
                    VALUES (%s, %s, %s)
                    """,
                    (user_id, task["id"], today),
                )
            except psycopg2.IntegrityError:
                return None

            cur.execute(
                "UPDATE users SET coins = coins + %s WHERE id = %s",
                (task["coins_reward"], user_id),
            )
        conn.commit()
        return task


def clamp(value: int, min_value: int = 0, max_value: int = 100) -> int:
    return max(min_value, min(max_value, value))


def normalize_category(value: str | None) -> str:
    value = (value or "").lower()
    return value if value in COMMENT_CATEGORIES else "discussion"


def group_comments(rows: list):
    grouped = {key: [] for key in COMMENT_CATEGORIES}
    for row in rows:
        grouped[normalize_category(row["category"] )].append(row)
    return grouped


def get_user_toys(user_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_toys.id, user_toys.pos_x, user_toys.pos_y, user_toys.created_at,
                       toys.name, toys.icon, toys.slug
                FROM user_toys
                JOIN toys ON toys.id = user_toys.toy_id
                WHERE user_toys.user_id = %s
                ORDER BY user_toys.created_at DESC
                """,
                (user_id,),
            )
            return cur.fetchall()


def get_available_toys(user_id: int | None):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, slug, name, price, icon, description FROM toys ORDER BY price"
            )
            toys = cur.fetchall()
            if not user_id:
                return toys
            cur.execute(
                "SELECT toy_id, COUNT(*) as cnt FROM user_toys WHERE user_id = %s GROUP BY toy_id",
                (user_id,),
            )
            owned_counts = cur.fetchall()
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
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_toys.id, user_toys.pos_x, user_toys.pos_y, user_toys.created_at,
                       users.username, users.id AS owner_id,
                       toys.name AS toy_name, toys.icon
                FROM user_toys
                JOIN users ON users.id = user_toys.user_id
                JOIN toys ON toys.id = user_toys.toy_id
                ORDER BY user_toys.created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            return cur.fetchall()


def get_comment_replies(comment_ids: list[int]):
    if not comment_ids:
        return {}
    placeholders = ",".join(["%s"] * len(comment_ids))
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT comment_replies.id, comment_replies.comment_id, comment_replies.user_id, comment_replies.content,
                       comment_replies.created_at, users.username
                FROM comment_replies
                JOIN users ON users.id = comment_replies.user_id
                WHERE comment_replies.comment_id IN ({placeholders})
                ORDER BY comment_replies.created_at ASC
                """,
                tuple(comment_ids),
            )
            rows = cur.fetchall()
    grouped: dict[int, list] = {cid: [] for cid in comment_ids}
    for row in rows:
        grouped.setdefault(row["comment_id"], []).append(row)
    return grouped


def redirect_to(next_url: str | None, fallback: str):
    if next_url and next_url.startswith("/"):
        return redirect(next_url)
    return redirect(fallback)


@app.template_filter("friendly_date")
def friendly_date(value) -> str:
    if not value:
        return ""
    try:
        # PostgreSQL returns datetime objects, SQLite returns strings
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        else:
            return datetime.fromisoformat(str(value)).strftime("%Y-%m-%d")
    except (ValueError, TypeError, AttributeError):
        return str(value) if value else ""


@app.context_processor
def inject_globals():
    return {"category_labels": COMMENT_CATEGORIES}


@app.route("/")
def index():
    user = current_user()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, slug, cover_url, author, grade
                FROM books
                ORDER BY id
                LIMIT 4
                """
            )
            featured_books = cur.fetchall()
            cur.execute(
                """
                SELECT comments.content, comments.created_at, comments.category,
                       users.username, books.title, books.slug
                FROM comments
                JOIN users ON users.id = comments.user_id
                JOIN books ON books.id = comments.book_id
                ORDER BY comments.created_at DESC
                LIMIT 5
                """
            )
            latest_comments = cur.fetchall()
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
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, slug, cover_url, author, publisher, grade
                FROM books
                ORDER BY CASE grade
                    WHEN '六年级' THEN 0
                    WHEN '七年级' THEN 1
                    WHEN '八年级' THEN 2
                    ELSE 3 END, title
                """
            )
            rows = cur.fetchall()

    grouped: dict[str, list] = {}
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
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, slug, cover_url, author, publisher, grade
                FROM books
                WHERE slug = %s
                """,
                (slug,),
            )
            book = cur.fetchone()
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
                cur.execute(
                    """
                    INSERT INTO comments (user_id, book_id, content, category)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (session["user_id"], book["id"], content, category),
                )
        conn.commit()
        if request.method == "POST":
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

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT comments.id, comments.user_id, comments.content, comments.created_at, comments.category, users.username
                FROM comments
                JOIN users ON users.id = comments.user_id
                WHERE comments.book_id = %s
                ORDER BY comments.created_at DESC
                """,
                (book["id"],),
            )
            comments = cur.fetchall()

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
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT comments.id, comments.user_id, comments.content, comments.created_at, comments.category,
                       users.username, books.title, books.slug
                FROM comments
                JOIN users ON users.id = comments.user_id
                JOIN books ON books.id = comments.book_id
                ORDER BY comments.created_at DESC
                """
            )
            thread = cur.fetchall()
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
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT comments.id, comments.content, comments.category, comments.created_at,
                       users.username, books.title, books.slug
                FROM comments
                JOIN users ON users.id = comments.user_id
                JOIN books ON books.id = comments.book_id
                ORDER BY comments.created_at DESC
                LIMIT 50
                """
            )
            comments = cur.fetchall()
            cur.execute(
                "SELECT id, username, is_admin, created_at, coins FROM users ORDER BY created_at DESC"
            )
            users = cur.fetchall()
            cur.execute(
                "SELECT id, title, slug, grade FROM books ORDER BY created_at DESC LIMIT 12"
            )
            recent_books = cur.fetchall()
            cur.execute(
                """
                SELECT book_requests.id, book_requests.title, book_requests.author,
                       book_requests.publisher, book_requests.grade, book_requests.cover_url,
                       book_requests.created_at, users.username
                FROM book_requests
                JOIN users ON users.id = book_requests.user_id
                WHERE book_requests.status = 'pending'
                ORDER BY book_requests.created_at DESC
                """
            )
            pending_requests = cur.fetchall()
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
            pending_requests=pending_requests,
        )


@app.post("/admin/books/add")
def admin_add_book():
    require_admin()
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    publisher = request.form.get("publisher", "").strip()
    grade = request.form.get("grade", "").strip()
    slug_value = request.form.get("slug", "").strip() or slugify(title)

    if not title:
        flash("书名不能为空。", "error")
        return redirect(url_for("admin_dashboard"))

    # Handle file upload
    cover_file = request.files.get("cover_file")
    if not cover_file or not cover_file.filename:
        flash("请上传封面图片。", "error")
        return redirect(url_for("admin_dashboard"))

    cover_url = save_uploaded_file(cover_file, "covers")
    if not cover_url:
        flash("封面文件格式不支持，请上传 PNG, JPG, GIF 或 WEBP 格式的图片。", "error")
        return redirect(url_for("admin_dashboard"))

    if grade and grade not in GRADE_ORDER:
        flash("请选择有效的年级。", "error")
        return redirect(url_for("admin_dashboard"))

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO books (slug, title, cover_url, author, publisher, grade)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT(slug) DO UPDATE SET
                    title=EXCLUDED.title,
                    cover_url=EXCLUDED.cover_url,
                    author=EXCLUDED.author,
                    publisher=EXCLUDED.publisher,
                    grade=EXCLUDED.grade
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
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM books WHERE id = %s",
                (book_id,),
            )
            deleted_count = cur.rowcount
        conn.commit()

    if deleted_count:
        flash("书籍已删除。", "success")
    else:
        flash("未找到该书籍。", "error")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/comments/<int:comment_id>/delete")
def admin_delete_comment(comment_id: int):
    require_admin()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM comments WHERE id = %s",
                (comment_id,),
            )
            deleted_count = cur.rowcount
        conn.commit()

    if deleted_count:
        flash("评论已删除。", "success")
    else:
        flash("未找到要删除的评论。", "error")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/users/<int:user_id>/toggle-admin")
def admin_toggle_user(user_id: int):
    current_admin = require_admin()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, is_admin FROM users WHERE id = %s",
                (user_id,),
            )
            user = cur.fetchone()
            if not user:
                abort(404)

            if user["is_admin"]:
                cur.execute(
                    "SELECT COUNT(*) as count FROM users WHERE is_admin = 1"
                )
                admin_count = cur.fetchone()['count']
                if admin_count <= 1:
                    flash("至少需要保留一名管理员。", "error")
                    return redirect(url_for("admin_dashboard"))

            new_value = 0 if user["is_admin"] else 1
            cur.execute(
                "UPDATE users SET is_admin = %s WHERE id = %s",
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
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET coins = %s WHERE id = %s",
                (coins_value, user_id),
            )
            updated_count = cur.rowcount
        conn.commit()

    if updated_count:
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
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, is_admin FROM users WHERE id = %s",
                (user_id,),
            )
            user = cur.fetchone()
            if not user:
                flash("未找到该用户。", "error")
                return redirect(url_for("admin_dashboard"))

            if user["is_admin"]:
                cur.execute(
                    "SELECT COUNT(*) as count FROM users WHERE is_admin = 1"
                )
                admin_count = cur.fetchone()['count']
                if admin_count <= 1:
                    flash("至少需要保留一名管理员。", "error")
                    return redirect(url_for("admin_dashboard"))

            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()

    flash("用户账户已删除。", "success")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/toys/<int:user_toy_id>/delete")
def admin_delete_user_toy(user_toy_id: int):
    require_admin()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM user_toys WHERE id = %s",
                (user_toy_id,),
            )
            deleted_count = cur.rowcount
        conn.commit()

    if deleted_count:
        flash("玩具已移除。", "success")
    else:
        flash("未找到该玩具记录。", "error")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/replies/<int:reply_id>/delete")
def admin_delete_reply(reply_id: int):
    require_admin()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM comment_replies WHERE id = %s",
                (reply_id,),
            )
            deleted_count = cur.rowcount
        conn.commit()

    if deleted_count:
        flash("回复已删除。", "success")
    else:
        flash("未找到该回复。", "error")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/book-requests/<int:request_id>/approve")
def admin_approve_request(request_id: int):
    admin = require_admin()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Get request details
            cur.execute(
                """
                SELECT title, author, publisher, grade, cover_url
                FROM book_requests
                WHERE id = %s AND status = 'pending'
                """,
                (request_id,),
            )
            req = cur.fetchone()

            if not req:
                flash("未找到该申请或已处理。", "error")
                return redirect(url_for("admin_dashboard"))

            # Generate slug
            slug_value = slugify(req["title"])

            # Add book to books table
            cur.execute(
                """
                INSERT INTO books (slug, title, author, publisher, grade, cover_url)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT(slug) DO UPDATE SET
                    title=EXCLUDED.title,
                    author=EXCLUDED.author,
                    publisher=EXCLUDED.publisher,
                    grade=EXCLUDED.grade,
                    cover_url=EXCLUDED.cover_url
                """,
                (slug_value, req["title"], req["author"], req["publisher"], req["grade"], req["cover_url"]),
            )

            # Update request status
            cur.execute(
                """
                UPDATE book_requests
                SET status = 'approved', reviewed_at = CURRENT_TIMESTAMP, reviewed_by = %s
                WHERE id = %s
                """,
                (admin["id"], request_id),
            )
        conn.commit()

    flash(f"书籍《{req['title']}》已通过审核并添加到书架。", "success")
    return redirect(url_for("admin_dashboard"))


@app.post("/admin/book-requests/<int:request_id>/reject")
def admin_reject_request(request_id: int):
    admin = require_admin()

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE book_requests
                SET status = 'rejected', reviewed_at = CURRENT_TIMESTAMP, reviewed_by = %s
                WHERE id = %s AND status = 'pending'
                """,
                (admin["id"], request_id),
            )
            updated_count = cur.rowcount
        conn.commit()

    if updated_count:
        flash("已拒绝该书籍申请。", "success")
    else:
        flash("未找到该申请或已处理。", "error")
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
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, code, name, coins_reward FROM tasks WHERE id = %s",
                (task_id,),
            )
            task = cur.fetchone()
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
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, coins FROM users WHERE id = %s",
                (user_id,),
            )
            user = cur.fetchone()
            cur.execute(
                "SELECT * FROM pets WHERE user_id = %s",
                (user_id,),
            )
            pet_row = cur.fetchone()
            if not pet_row:
                cur.execute(
                    "INSERT INTO pets (user_id, name, hunger, happiness) VALUES (%s, %s, 50, 60)",
                    (user_id, f"{user['username']}的小兽"),
                )
        conn.commit()
        if not pet_row:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM pets WHERE user_id = %s",
                    (user_id,),
                )
                pet_row = cur.fetchone()

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

            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET coins = coins - %s WHERE id = %s",
                    (action["cost"], user_id),
                )
                cur.execute(
                    """
                    UPDATE pets
                    SET hunger = %s, happiness = %s, last_care_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (new_hunger, new_happiness, pet_row["id"]),
                )
            conn.commit()
            flash(f"{action['label']}完成！宠物状态提升。", "success")
            return redirect(url_for("pet"))

        satiety = clamp(100 - pet_row["hunger"])
        owned_toys = get_user_toys(user_id)
        toy_catalog = get_available_toys(user_id)

        # Get pet appearance info
        pet_appearance = next((p for p in PET_APPEARANCES if p["id"] == pet_row.get("appearance", "cat-orange")), PET_APPEARANCES[0])

        return render_template(
            "pet.html",
            pet=pet_row,
            satiety=satiety,
            coins=user["coins"],
            actions=PET_ACTIONS,
            owned_toys=owned_toys,
            toy_catalog=toy_catalog,
            pet_appearance=pet_appearance,
        )


@app.post("/pet/buy/<slug>")
def pet_buy_toy(slug: str):
    if not is_logged_in():
        flash("请先登录。", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, price FROM toys WHERE slug = %s",
                (slug,),
            )
            toy = cur.fetchone()
            cur.execute(
                "SELECT coins FROM users WHERE id = %s",
                (user_id,),
            )
            user = cur.fetchone()

            if not toy or not user:
                abort(404)

            if user["coins"] < toy["price"]:
                flash("金币不足，先去完成任务吧！", "error")
                return redirect(url_for("pet"))

            pos_x = random.uniform(5, 85)
            pos_y = random.uniform(45, 80)

            cur.execute(
                "UPDATE users SET coins = coins - %s WHERE id = %s",
                (toy["price"], user_id),
            )
            cur.execute(
                "INSERT INTO user_toys (user_id, toy_id, pos_x, pos_y) VALUES (%s, %s, %s, %s)",
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
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT comments.id, books.slug
                FROM comments
                JOIN books ON books.id = comments.book_id
                WHERE comments.id = %s
                """,
                (comment_id,),
            )
            comment = cur.fetchone()
            if not comment:
                abort(404)

            cur.execute(
                "INSERT INTO comment_replies (comment_id, user_id, content) VALUES (%s, %s, %s)",
                (comment_id, session["user_id"], content),
            )
        conn.commit()

    flash("回复已发布。", "success")
    next_url = request.form.get("next")
    fallback = url_for("book_detail", slug=comment["slug"])
    return redirect_to(next_url, fallback)


@app.post("/comments/<int:comment_id>/delete")
def delete_comment_user(comment_id: int):
    if not is_logged_in():
        flash("请先登录再删除评论。", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT comments.id, comments.user_id, books.slug
                FROM comments
                JOIN books ON books.id = comments.book_id
                WHERE comments.id = %s
                """,
                (comment_id,),
            )
            comment = cur.fetchone()
            if not comment:
                abort(404)
            if comment["user_id"] != user_id:
                abort(403)
            cur.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        conn.commit()

    flash("评论已删除。", "success")
    next_url = request.form.get("next")
    fallback = url_for("book_detail", slug=comment["slug"])
    return redirect_to(next_url, fallback)


@app.post("/replies/<int:reply_id>/delete")
def delete_reply_user(reply_id: int):
    if not is_logged_in():
        flash("请先登录再删除回复。", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT comment_replies.id, comment_replies.user_id, books.slug
                FROM comment_replies
                JOIN comments ON comments.id = comment_replies.comment_id
                JOIN books ON books.id = comments.book_id
                WHERE comment_replies.id = %s
                """,
                (reply_id,),
            )
            reply = cur.fetchone()
            if not reply:
                abort(404)
            if reply["user_id"] != user_id:
                abort(403)
            cur.execute("DELETE FROM comment_replies WHERE id = %s", (reply_id,))
        conn.commit()

    flash("回复已删除。", "success")
    next_url = request.form.get("next")
    fallback = url_for("book_detail", slug=reply["slug"])
    return redirect_to(next_url, fallback)


@app.route("/settings", methods=["GET", "POST"])
def settings_page():
    if not is_logged_in():
        flash("请先登录。", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, coins, is_admin, avatar, language, last_username_change
                FROM users WHERE id = %s
                """,
                (user_id,),
            )
            user = cur.fetchone()
            cur.execute(
                "SELECT name FROM pets WHERE user_id = %s",
                (user_id,),
            )
            pet = cur.fetchone()

    if request.method == "POST":
        action = request.form.get("action")
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if action == "pet_name":
                    new_name = request.form.get("pet_name", "").strip()
                    if not (1 <= len(new_name) <= 20):
                        flash("名称长度需在 1-20 个字符内。", "error")
                        return redirect(url_for("settings_page"))
                    cur.execute(
                        "INSERT INTO pets (user_id, name) VALUES (%s, %s) ON CONFLICT(user_id) DO UPDATE SET name=EXCLUDED.name",
                        (user_id, new_name),
                    )
            conn.commit()
            if action == "pet_name":
                flash("宠物昵称已更新！", "success")
            elif action == "avatar":
                # Handle file upload
                avatar_file = request.files.get("avatar_file")

                if not avatar_file or not avatar_file.filename:
                    flash("请选择头像图片文件。", "error")
                    return redirect(url_for("settings_page"))

                avatar_url = save_uploaded_file(avatar_file, "avatars")
                if not avatar_url:
                    flash("头像文件格式不支持，请上传 PNG, JPG, GIF 或 WEBP 格式的图片。", "error")
                    return redirect(url_for("settings_page"))

                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE users SET avatar = %s WHERE id = %s",
                        (avatar_url, user_id),
                    )
                conn.commit()
                flash("头像已更新。", "success")
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
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT 1 FROM users WHERE username = %s",
                        (new_username,),
                    )
                    exists = cur.fetchone()
                    if exists:
                        flash("该用户名已被占用。", "error")
                        return redirect(url_for("settings_page"))
                    cur.execute(
                        "UPDATE users SET username = %s, last_username_change = CURRENT_TIMESTAMP WHERE id = %s",
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


@app.route("/request-book")
def request_book():
    if not is_logged_in():
        flash("请先登录。", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, title, author, publisher, grade, status, created_at
                FROM book_requests
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            my_requests = cur.fetchall()

    return render_template("request_book.html", my_requests=my_requests)


@app.post("/request-book/submit")
def submit_book_request():
    if not is_logged_in():
        flash("请先登录。", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    publisher = request.form.get("publisher", "").strip()
    grade = request.form.get("grade", "").strip()

    if not title:
        flash("书名不能为空。", "error")
        return redirect(url_for("request_book"))

    if not grade or grade not in GRADE_ORDER:
        flash("请选择有效的年级。", "error")
        return redirect(url_for("request_book"))

    # Handle file upload
    cover_file = request.files.get("cover_file")
    if not cover_file or not cover_file.filename:
        flash("请上传封面图片。", "error")
        return redirect(url_for("request_book"))

    cover_url = save_uploaded_file(cover_file, "covers")
    if not cover_url:
        flash("封面文件格式不支持，请上传 PNG, JPG, GIF 或 WEBP 格式的图片。", "error")
        return redirect(url_for("request_book"))

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO book_requests (user_id, title, author, publisher, grade, cover_url)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (user_id, title, author, publisher, grade, cover_url),
            )
        conn.commit()

    flash("书籍申请已提交，等待管理员审核。", "success")
    return redirect(url_for("request_book"))


@app.route("/choose-pet", methods=["GET", "POST"])
def choose_pet():
    if not is_logged_in():
        flash("请先登录。", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Check if user already has a pet
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM pets WHERE user_id = %s", (user_id,))
            existing_pet = cur.fetchone()

    if existing_pet:
        # User already has a pet, redirect to pet page
        return redirect(url_for("pet"))

    if request.method == "POST":
        appearance = request.form.get("appearance", "").strip()
        pet_name = request.form.get("pet_name", "").strip()

        if not appearance or appearance not in [p["id"] for p in PET_APPEARANCES]:
            flash("请选择有效的宠物造型。", "error")
            return redirect(url_for("choose_pet"))

        if not pet_name or not (1 <= len(pet_name) <= 20):
            flash("宠物名字需在 1-20 个字符之间。", "error")
            return redirect(url_for("choose_pet"))

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO pets (user_id, name, appearance, hunger, happiness) VALUES (%s, %s, %s, 50, 60)",
                    (user_id, pet_name, appearance),
                )
            conn.commit()

        flash("宠物创建成功！开始你的阅读之旅吧~", "success")
        return redirect(url_for("index"))

    return render_template("choose_pet.html", appearances=PET_APPEARANCES)


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
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) as count FROM users")
                    existing_count = cur.fetchone()['count']
                    cur.execute(
                        "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                        (username, password_hash),
                    )
                    new_user_id = cur.fetchone()['id']
                    if existing_count == 0:
                        cur.execute(
                            "UPDATE users SET is_admin = 1 WHERE id = %s",
                            (new_user_id,),
                        )
                conn.commit()

            # Auto-login after registration
            session["user_id"] = new_user_id
            session["username"] = username
            session["is_admin"] = (existing_count == 0)

            flash("注册成功！请选择你的宠物伙伴~", "success")
            return redirect(url_for("choose_pet"))
        except psycopg2.IntegrityError:
            flash("用户名已存在，请换一个。", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, username, password_hash, coins, is_admin
                    FROM users WHERE username = %s
                    """,
                    (username,),
                )
                user = cur.fetchone()

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
