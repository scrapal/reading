#!/usr/bin/env python3
"""测试火苗计算逻辑"""

from datetime import datetime, timedelta, date

def calculate_streak(last_checkin_date, current_streak: int, is_boarder: bool = False) -> int:
    """Calculate streak count based on last check-in date.

    Args:
        last_checkin_date: Last check-in date (DATE type)
        current_streak: Current streak count
        is_boarder: Whether user is a boarder (no reset on weekdays)

    Returns:
        New streak count (0 if broken, current+1 if continued)
    """
    if not last_checkin_date:
        return 1  # First check-in

    try:
        if isinstance(last_checkin_date, datetime):
            last_date = last_checkin_date.date()
        elif isinstance(last_checkin_date, str):
            last_date = datetime.strptime(last_checkin_date, '%Y-%m-%d').date()
        else:
            last_date = last_checkin_date
    except (ValueError, TypeError, AttributeError):
        return 1  # Invalid date, start fresh

    today = date.today()

    # Same day, no change
    if last_date == today:
        return current_streak

    # Calculate days difference
    days_diff = (today - last_date).days

    # Consecutive day (yesterday)
    if days_diff == 1:
        return current_streak + 1

    # More than 1 day gap - check if should reset
    if days_diff > 1:
        # If boarder, check if all skipped days were weekdays
        if is_boarder:
            should_reset = False
            # Check each day between last_date and today
            for i in range(1, days_diff):
                check_date = last_date + timedelta(days=i)
                weekday = check_date.weekday()  # 0=Monday, 6=Sunday
                # If any skipped day was weekend, reset streak
                if weekday >= 5:  # Saturday or Sunday
                    should_reset = True
                    break

            if not should_reset:
                # All skipped days were weekdays, continue streak
                return current_streak + 1

        # Non-boarder or boarder with weekend gap - reset
        return 0

    return current_streak


# 测试场景
print("=== 火苗系统测试 ===\n")

# 测试1: 首次打卡
print("测试1: 首次打卡")
result = calculate_streak(None, 0, False)
print(f"  结果: {result} (预期: 1)")
assert result == 1, "首次打卡应该返回1"
print("  ✅ 通过\n")

# 测试2: 连续打卡（昨天打卡过）
print("测试2: 连续打卡")
yesterday = date.today() - timedelta(days=1)
result = calculate_streak(yesterday, 5, False)
print(f"  结果: {result} (预期: 6)")
assert result == 6, "连续打卡应该+1"
print("  ✅ 通过\n")

# 测试3: 同一天重复打卡
print("测试3: 同一天重复打卡")
today = date.today()
result = calculate_streak(today, 10, False)
print(f"  结果: {result} (预期: 10)")
assert result == 10, "同一天打卡应该保持不变"
print("  ✅ 通过\n")

# 测试4: 断签（2天没打卡）- 走读生
print("测试4: 断签 - 走读生")
two_days_ago = date.today() - timedelta(days=2)
result = calculate_streak(two_days_ago, 7, False)
print(f"  结果: {result} (预期: 0)")
assert result == 0, "走读生断签应该归零"
print("  ✅ 通过\n")

# 测试5: 周一到周五工作日未打卡 - 住宿生（不应该归零）
print("测试5: 工作日未打卡 - 住宿生")
# 找到上周五
today_weekday = date.today().weekday()
if today_weekday == 0:  # 如果今天是周一
    last_friday = date.today() - timedelta(days=3)
elif today_weekday == 1:  # 如果今天是周二
    last_friday = date.today() - timedelta(days=4)
elif today_weekday == 2:  # 如果今天是周三
    last_friday = date.today() - timedelta(days=5)
elif today_weekday == 3:  # 如果今天是周四
    last_friday = date.today() - timedelta(days=6)
elif today_weekday == 4:  # 如果今天是周五
    last_friday = date.today() - timedelta(days=7)
else:  # 周末，测试从周一开始
    # 模拟从周一到周三的工作日
    monday = date.today() - timedelta(days=2)
    result = calculate_streak(monday, 5, True)
    print(f"  从周一到今天（工作日），住宿生未打卡")
    print(f"  结果: {result} (预期: 6)")
    assert result == 6, "住宿生工作日未打卡不应该归零"
    print("  ✅ 通过\n")

# 测试6: 周末断签 - 住宿生（应该归零）
print("测试6: 周末断签 - 住宿生")
# 如果今天是周一，上周六是2天前
if date.today().weekday() == 0:  # 周一
    last_friday = date.today() - timedelta(days=3)
    result = calculate_streak(last_friday, 10, True)
    print(f"  从上周五到今天（跨周末），住宿生未打卡")
    print(f"  结果: {result} (预期: 0)")
    assert result == 0, "住宿生周末断签应该归零"
    print("  ✅ 通过\n")
else:
    print("  (跳过此测试，今天不是周一)\n")

print("=== 所有测试通过！ ===")
