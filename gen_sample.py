"""生成 5 只 ETF 的模拟日线行情（随机游走），保存到 data/prices.csv"""
import csv
import datetime as dt
import os
import random

random.seed(42)   # 固定随机种子，保证每次生成的数据一样，方便复现问题

ETFS = [
    ("510300", "沪深300ETF", 0.0004, 0.013),
    ("510500", "中证500ETF", 0.0003, 0.016),
    ("159915", "创业板ETF",  0.0005, 0.020),
    ("518880", "黄金ETF",    0.0002, 0.010),
    ("513100", "纳指ETF",    0.0006, 0.015),
]  # 每项是：(代码, 名称, 日均涨幅, 日波动率)

DAYS = 750        # 大约 3 年的交易日

# 生成交易日期（跳过周末）
dates, d = [], dt.date(2022, 1, 4)
while len(dates) < DAYS:
    if d.weekday() < 5:
        dates.append(d.isoformat())
    d += dt.timedelta(days=1)

os.makedirs("data", exist_ok=True)
rows = []
for code, name, mu, sigma in ETFS:
    price = 1.0
    for day in dates:
        price *= 1.0 + random.gauss(mu, sigma)   # 每天随机涨一点跌一点
        rows.append([day, code, name, round(price, 4)])

with open(os.path.join("data", "prices.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["date", "code", "name", "close"])
    w.writerows(rows)

print("已生成 data/prices.csv：%d 只 ETF x %d 天 = %d 行" % (len(ETFS), DAYS, len(rows)))
