"""Streamlit UI for the number guessing game."""

import random

import streamlit as st

from games.number_guess_logic import DIFFICULTIES, Difficulty, evaluate_guess, proximity_hint


STATE_PREFIX = "number_guess"


def _state_key(name: str) -> str:
    return f"{STATE_PREFIX}_{name}"


def _start_round(difficulty_name: str) -> None:
    config = DIFFICULTIES[difficulty_name]
    st.session_state[_state_key("difficulty")] = difficulty_name
    st.session_state[_state_key("target")] = random.randint(config.lower, config.upper)
    st.session_state[_state_key("attempts")] = 0
    st.session_state[_state_key("history")] = []
    st.session_state[_state_key("status")] = "playing"


def _ensure_round(difficulty_name: str) -> None:
    if (
        _state_key("target") not in st.session_state
        or st.session_state.get(_state_key("difficulty")) != difficulty_name
    ):
        _start_round(difficulty_name)


def _render_history() -> None:
    history: list[tuple[int, str]] = st.session_state[_state_key("history")]
    if not history:
        st.info("💡 小技巧：每次根据“大了”或“小了”缩小范围。")
        return

    labels = {
        "too_low": "太小了 ⬆️",
        "too_high": "太大了 ⬇️",
        "correct": "猜对了 ✅",
    }
    st.markdown("#### 猜过的数字")
    st.write("　".join(f"**{guess}**（{labels[result]}）" for guess, result in history))


def _render_result(config: Difficulty) -> None:
    status = st.session_state[_state_key("status")]
    history: list[tuple[int, str]] = st.session_state[_state_key("history")]
    target: int = st.session_state[_state_key("target")]

    if status == "won":
        attempts = st.session_state[_state_key("attempts")]
        st.success(f"🎉 猜对啦！答案就是 {target}，你一共猜了 {attempts} 次。")
        st.balloons()
    elif status == "lost":
        st.error(f"这一局的答案是 {target}。没关系，下一局一定会更接近！💪")
    elif history:
        guess, result = history[-1]
        direction = "数字太小，再猜大一点。⬆️" if result == "too_low" else "数字太大，再猜小一点。⬇️"
        st.warning(f"{direction} {proximity_hint(target, guess, config.upper - config.lower)}")


def render() -> None:
    """Render one playable round."""
    st.header("🔢 猜数字")
    st.write("我藏好了一个数字。根据提示找到它，看看你需要猜几次！")

    difficulty_name = st.selectbox(
        "选择难度",
        options=list(DIFFICULTIES),
        help="切换难度会自动开始新的一局。",
    )
    config = DIFFICULTIES[difficulty_name]
    st.caption(f"{config.description} · 共有 {config.max_attempts} 次机会")
    _ensure_round(difficulty_name)

    attempts: int = st.session_state[_state_key("attempts")]
    status: str = st.session_state[_state_key("status")]
    remaining = config.max_attempts - attempts

    left, right = st.columns(2)
    left.metric("已经猜了", f"{attempts} 次")
    right.metric("剩余机会", f"{remaining} 次")
    st.progress(attempts / config.max_attempts, text="本局进度")

    guess = st.number_input(
        f"输入 {config.lower} 到 {config.upper} 之间的整数",
        min_value=config.lower,
        max_value=config.upper,
        step=1,
        key=f"{STATE_PREFIX}_input_{difficulty_name}",
        disabled=status != "playing",
    )

    if st.button(
        "提交答案 🎯",
        type="primary",
        use_container_width=True,
        disabled=status != "playing",
    ):
        target: int = st.session_state[_state_key("target")]
        result = evaluate_guess(target, int(guess))
        st.session_state[_state_key("attempts")] += 1
        st.session_state[_state_key("history")].append((int(guess), result))

        if result == "correct":
            st.session_state[_state_key("status")] = "won"
        elif st.session_state[_state_key("attempts")] >= config.max_attempts:
            st.session_state[_state_key("status")] = "lost"
        st.rerun()

    _render_result(config)
    _render_history()

    if status != "playing" and st.button("再玩一局 🔄", use_container_width=True):
        _start_round(difficulty_name)
        st.rerun()
