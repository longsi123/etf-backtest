"""
ETF 动量轮动回测 —— 纯 Python 标准库实现，零第三方依赖。

策略：每隔 REBALANCE 个交易日，选出过去 LOOKBACK 天涨幅最强的 TOP_K 只 ETF，等权持有。
用法：python gen_sample.py   （第一步：生成模拟行情）
      python backtest.py     （第二步：跑回测）
"""
import csv
import os
from collections import defaultdict

LOOKBACK = 60            # 动量观察窗口（交易日）
TOP_K = 2                # 每期持有几只
REBALANCE = 20           # 每隔多少个交易日调仓一次
INIT_CASH = 100000.0     # 初始资金
PRICE_FILE = os.path.join("data", "prices.csv")
OUT_FILE = os.path.join("result", "nav.csv")

LINE = "-" * 54


def load_prices(path):
    """读 CSV，返回 {基金代码: [(日期, 收盘价), ...]}"""
    raw = defaultdict(list)
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            raw[row["code"]].append((row["date"], float(row["close"])))
    return {code: sorted(rows) for code, rows in raw.items()}


def align(hist):
    """把所有标的对齐到同一条时间轴上（缺失的日子用前一天的价格填充）"""
    master = sorted(set(day for rows in hist.values() for day, _ in rows))
    series = {}
    for code, rows in hist.items():
        price = dict(rows)
        filled, last = [], None
        for day in master:
            if day in price:
                last = price[day]
            filled.append(last)
        head = next((p for p in filled if p is not None), 0.0)
        series[code] = [p if p is not None else head for p in filled]
    return master, series


def momentum_of(series, i):
    """第 i 天的 LOOKBACK 日动量（涨幅）"""
    if i < LOOKBACK:
        return None
    return series[i] / series[i - LOOKBACK] - 1.0


def max_drawdown(curve):
    """最大回撤：从历史最高点回落到最低点的最大幅度"""
    peak, mdd = curve[0], 0.0
    for v in curve:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1.0)
    return mdd


def run_backtest():
    hist = load_prices(PRICE_FILE)
    master, series = align(hist)
    codes = sorted(hist.keys())

    cash, units = INIT_CASH, {}
    nav_curve, bench_curve, logs = [], [], []
    # 基准组合：一开始就等权买入所有标的，之后完全不动
    bench_units = {c: (INIT_CASH / len(codes)) / series[c][0] for c in codes}

    trades = 0
    for i, day in enumerate(master):
        # ---- 调仓日：挑出动量最强的 TOP_K，等权买入 ----
        if i >= LOOKBACK and i % REBALANCE == 0:
            scores = []
            for c in codes:
                m = momentum_of(series[c], i)
                if m is not None:
                    scores.append((m, c))
            if scores:
                scores.sort(reverse=True)
                target = [c for _, c in scores[:TOP_K]]
                value = cash + sum(u * series[c][i] for c, u in units.items())
                cash, units = 0.0, {}
                per = value / len(target)
                for c in target:
                    units[c] = per / series[c][i]
                trades += 1
                logs.append("%s  买入 %s" % (day, "、".join(target)))

        nav = cash + sum(u * series[c][i] for c, u in units.items())
        bench = sum(bench_units[c] * series[c][i] for c in codes)
        nav_curve.append(nav)
        bench_curve.append(bench)

    return master, nav_curve, bench_curve, codes, trades, logs


def save_nav(master, nav_curve, bench_curve):
    """把每日净值存成 CSV，方便用 Excel 画曲线"""
    os.makedirs("result", exist_ok=True)
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "strategy", "benchmark"])
        for day, nav, bench in zip(master, nav_curve, bench_curve):
            w.writerow([day, round(nav, 2), round(bench, 2)])


def report(master, nav_curve, bench_curve, codes, trades, logs):
    days = len(nav_curve)
    years = days / 252.0
    final = nav_curve[-1]
    ret = final / INIT_CASH - 1.0
    bench_ret = bench_curve[-1] / INIT_CASH - 1.0
    cagr = (final / INIT_CASH) ** (1.0 / years) - 1.0

    print("=" * 54)
    print("  策略：%d 日动量 / 持有前 %d 名 / 每 %d 日调仓" % (LOOKBACK, TOP_K, REBALANCE))
    print("  标的：%d 只   区间：%s ~ %s（%d 个交易日）"
          % (len(codes), master[0], master[-1], days))
    print(LINE)
    print("  期末资产       %14.0f 元" % final)
    print("  总收益率       %14.2f%%" % (ret * 100))
    print("  年化收益率     %14.2f%%" % (cagr * 100))
    print("  最大回撤       %14.2f%%" % (max_drawdown(nav_curve) * 100))
    print("  调仓次数       %14d 次" % trades)
    print(LINE)
    print("  买入持有基准   %14.2f%%" % (bench_ret * 100))
    print("  超额收益       %14.2f%%" % ((ret - bench_ret) * 100))
    print("=" * 54)
    print("  最近几次调仓：")
    for log in logs[-5:]:
        print("    " + log)
    print("  净值曲线已保存到 " + OUT_FILE)


def main():
    if not os.path.exists(PRICE_FILE):
        print("找不到 %s，请先运行：python gen_sample.py" % PRICE_FILE)
        return
    master, nav_curve, bench_curve, codes, trades, logs = run_backtest()
    save_nav(master, nav_curve, bench_curve)
    report(master, nav_curve, bench_curve, codes, trades, logs)


if __name__ == "__main__":
    main()
