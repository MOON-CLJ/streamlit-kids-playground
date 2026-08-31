# 童趣游戏屋

一个可以不断加入新游戏的 Streamlit 儿童小游戏合集。目前包含：

- 🔢 猜数字：三个难度、方向提示、接近程度提示和尝试次数记录。
- 🐾 动物记忆翻牌：三个卡片数量、配对进度和分难度最佳成绩。
- 🧮 数学小勇士：10 以内加法、20 以内加减、九九乘法和连胜积分。

## 启动游戏

需要先安装 [uv](https://docs.astral.sh/uv/)。在项目目录运行：

```bash
uv sync
uv run streamlit run app.py
```

然后打开终端中显示的网页地址即可游玩。

## 运行测试

```bash
uv run python -m unittest discover -s tests -v
```

## 添加新游戏

1. 在 `games/` 中新建一个游戏模块，并提供 `render()` 函数。
2. 在 `app.py` 的 `GAMES` 中注册游戏名称和 `render()` 函数。
3. 把独立的游戏规则放在单独的逻辑模块中，方便测试。
