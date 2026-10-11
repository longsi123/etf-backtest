# ETF 动量轮动回测器

「动量策略」：每隔一段时间，买最近涨得最猛的那几只。

本项目用**纯 Python 标准库**（不依赖 pandas / numpy）实现回测，并和「一开始满仓不动」做对比。

## 怎么运行

确保装了 Python 3，然后在这个文件夹里打开命令行：

```bash
# 第一步：生成模拟行情数据
python gen_sample.py

# 第二步：跑回测
python backtest.py
```

Windows 上如果 `python` 提示不是内部或外部命令，改用 `py`：

```bash
py gen_sample.py
py backtest.py
```

## 输出什么

- 期末资产、总收益率、年化收益率、最大回撤、调仓次数
- 「买入持有」基准收益，及策略的超额收益
- `result/nav.csv`：每日净值曲线，可以用 Excel 打开画图

## 换成真实数据

把 `data/prices.csv` 换成你自己的 ETF 历史行情即可，列名保持不变：

```
date,code,name,close
2022-01-04,510300,沪深300ETF,4.1230
```

注意：`gen_sample.py` 生成的是**随机数据**，跑出来的收益率没有参考价值。

## 可调参数

在 `backtest.py` 顶部：

| 参数 | 含义 | 默认 |
|---|---|---|
| `LOOKBACK` | 动量观察窗口（交易日） | 60 |
| `TOP_K` | 每期持有几只 | 2 |
| `REBALANCE` | 每隔几天调仓 | 20 |
| `INIT_CASH` | 初始资金 | 100000 |
