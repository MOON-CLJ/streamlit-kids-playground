"""Streamlit UI for the animal memory matching game."""

import streamlit as st

from games.memory_match_logic import (
    DIFFICULTIES,
    Difficulty,
    build_deck,
    cards_match,
)


STATE_PREFIX = "memory_match"


def _apply_card_styles() -> None:
    st.markdown(
        """
        <style>
        div[data-testid="stColumn"] div[data-testid="stButton"] button {
            min-height: 7rem !important;
            border-radius: 1.25rem;
        }

        div[data-testid="stColumn"] div[data-testid="stButton"] button p {
            font-size: 3.75rem !important;
            line-height: 1 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _state_key(name: str) -> str:
    return f"{STATE_PREFIX}_{name}"


def _start_round(difficulty_name: str) -> None:
    config = DIFFICULTIES[difficulty_name]
    st.session_state[_state_key("difficulty")] = difficulty_name
    st.session_state[_state_key("deck")] = build_deck(config.pair_count)
    st.session_state[_state_key("selected")] = []
    st.session_state[_state_key("matched")] = set()
    st.session_state[_state_key("moves")] = 0
    st.session_state[_state_key("pending_hide")] = False
    st.session_state[_state_key("status")] = "playing"
    st.session_state[_state_key("message")] = "ready"
    st.session_state[_state_key("round")] = (
        st.session_state.get(_state_key("round"), 0) + 1
    )
    if _state_key("best_scores") not in st.session_state:
        st.session_state[_state_key("best_scores")] = {}


def _ensure_round(difficulty_name: str) -> None:
    if (
        _state_key("deck") not in st.session_state
        or st.session_state.get(_state_key("difficulty")) != difficulty_name
    ):
        _start_round(difficulty_name)


def _record_win(difficulty_name: str) -> None:
    moves: int = st.session_state[_state_key("moves")]
    best_scores: dict[str, int] = dict(
        st.session_state[_state_key("best_scores")]
    )
    previous_best = best_scores.get(difficulty_name)
    if previous_best is None or moves < previous_best:
        best_scores[difficulty_name] = moves
        st.session_state[_state_key("best_scores")] = best_scores


def _select_card(index: int, difficulty_name: str) -> None:
    if st.session_state[_state_key("status")] != "playing":
        return

    deck: list[str] = st.session_state[_state_key("deck")]
    matched: set[int] = set(st.session_state[_state_key("matched")])
    selected: list[int] = list(st.session_state[_state_key("selected")])

    if index in matched:
        return

    if st.session_state[_state_key("pending_hide")]:
        selected = []
        st.session_state[_state_key("pending_hide")] = False

    if index in selected:
        return

    selected.append(index)
    st.session_state[_state_key("selected")] = selected
    st.session_state[_state_key("message")] = "first_card"

    if len(selected) < 2:
        return

    st.session_state[_state_key("moves")] += 1
    first_index, second_index = selected

    if cards_match(deck, first_index, second_index):
        matched.update(selected)
        st.session_state[_state_key("matched")] = matched
        st.session_state[_state_key("selected")] = []
        st.session_state[_state_key("message")] = "match"

        if len(matched) == len(deck):
            st.session_state[_state_key("status")] = "won"
            _record_win(difficulty_name)
    else:
        st.session_state[_state_key("pending_hide")] = True
        st.session_state[_state_key("message")] = "mismatch"


def _render_status() -> None:
    status: str = st.session_state[_state_key("status")]
    message: str = st.session_state[_state_key("message")]
    moves: int = st.session_state[_state_key("moves")]

    if status == "won":
        st.success(f"🎉 全部配对成功！你用了 {moves} 次翻牌。")
        st.balloons()
    elif message == "mismatch":
        st.warning("这两只动物不一样。记住它们的位置，再点一张牌继续！")
    elif message == "match":
        st.success("配对成功！太棒了！✨")
    elif message == "first_card":
        st.info("记住这只动物，再翻一张牌吧。")
    else:
        st.info("先翻开任意一张卡片，寻找相同的动物。")


def _render_board(config: Difficulty, difficulty_name: str) -> None:
    deck: list[str] = st.session_state[_state_key("deck")]
    selected: list[int] = st.session_state[_state_key("selected")]
    matched: set[int] = st.session_state[_state_key("matched")]
    pending_hide: bool = st.session_state[_state_key("pending_hide")]
    round_number: int = st.session_state[_state_key("round")]

    for row_start in range(0, len(deck), config.columns):
        columns = st.columns(config.columns)
        for offset, column in enumerate(columns):
            index = row_start + offset
            is_visible = index in selected or index in matched
            is_disabled = index in matched or (
                index in selected and not pending_hide
            )
            label = deck[index] if is_visible else "❓"

            with column:
                if st.button(
                    label,
                    key=f"{STATE_PREFIX}_{round_number}_{index}",
                    help="已经配对" if index in matched else "点击翻开卡片",
                    use_container_width=True,
                    disabled=is_disabled,
                ):
                    _select_card(index, difficulty_name)
                    st.rerun()


def render() -> None:
    """Render one playable memory matching round."""
    _apply_card_styles()
    st.header("🐾 动物记忆翻牌")
    st.write("翻开两张卡片，找出所有相同的动物。看看你的记忆力有多棒！")

    difficulty_name = st.selectbox(
        "选择难度",
        options=list(DIFFICULTIES),
        key=f"{STATE_PREFIX}_difficulty_picker",
        help="切换难度会自动开始新的一局。",
    )
    config = DIFFICULTIES[difficulty_name]
    st.caption(config.description)
    _ensure_round(difficulty_name)

    matched: set[int] = st.session_state[_state_key("matched")]
    moves: int = st.session_state[_state_key("moves")]
    best_scores: dict[str, int] = st.session_state[_state_key("best_scores")]
    matched_pairs = len(matched) // 2
    best_score = best_scores.get(difficulty_name)

    first, second, third = st.columns(3)
    first.metric("翻牌次数", f"{moves} 次")
    second.metric("成功配对", f"{matched_pairs}/{config.pair_count}")
    third.metric("最佳成绩", f"{best_score} 次" if best_score else "—")
    st.progress(
        matched_pairs / config.pair_count,
        text=f"已经找到 {matched_pairs} 对动物",
    )

    _render_status()
    _render_board(config, difficulty_name)

    if st.button("重新洗牌 🔄", use_container_width=True):
        _start_round(difficulty_name)
        st.rerun()
