"""Streamlit UI for the Math Warrior game."""

import streamlit as st

from games.math_warrior_logic import (
    DIFFICULTIES,
    Difficulty,
    Question,
    check_answer,
    generate_question,
    points_for_correct,
)


STATE_PREFIX = "math_warrior"


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
        .math-question-card {
            margin: 1rem 0;
            padding: 1.5rem;
            border: 3px solid #ffbd45;
            border-radius: 1.25rem;
            background: rgba(255, 189, 69, 0.12);
            text-align: center;
            font-size: 4rem;
            font-weight: 800;
            line-height: 1.2;
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
    st.session_state[_state_key("question")] = generate_question(config)
    st.session_state[_state_key("answered")] = 0
    st.session_state[_state_key("correct")] = 0
    st.session_state[_state_key("score")] = 0
    st.session_state[_state_key("streak")] = 0
    st.session_state[_state_key("best_streak")] = 0
    st.session_state[_state_key("status")] = "answering"
    st.session_state[_state_key("last_correct")] = None
    st.session_state[_state_key("round")] = (
        st.session_state.get(_state_key("round"), 0) + 1
    )
    if _state_key("best_scores") not in st.session_state:
        st.session_state[_state_key("best_scores")] = {}


def _ensure_round(difficulty_name: str) -> None:
    if (
        _state_key("question") not in st.session_state
        or st.session_state.get(_state_key("difficulty")) != difficulty_name
    ):
        _start_round(difficulty_name)


def _submit_answer(answer: int) -> None:
    question: Question = st.session_state[_state_key("question")]
    is_correct = check_answer(question, answer)
    st.session_state[_state_key("answered")] += 1
    st.session_state[_state_key("last_correct")] = is_correct
    st.session_state[_state_key("status")] = "feedback"

    if is_correct:
        streak = st.session_state[_state_key("streak")] + 1
        st.session_state[_state_key("streak")] = streak
        st.session_state[_state_key("best_streak")] = max(
            st.session_state[_state_key("best_streak")],
            streak,
        )
        st.session_state[_state_key("correct")] += 1
        st.session_state[_state_key("score")] += points_for_correct(streak)
    else:
        st.session_state[_state_key("streak")] = 0


def _finish_round(difficulty_name: str) -> None:
    score: int = st.session_state[_state_key("score")]
    best_scores: dict[str, int] = dict(
        st.session_state[_state_key("best_scores")]
    )
    previous_best = best_scores.get(difficulty_name)
    if previous_best is None or score > previous_best:
        best_scores[difficulty_name] = score
        st.session_state[_state_key("best_scores")] = best_scores
    st.session_state[_state_key("status")] = "finished"


def _advance(config: Difficulty, difficulty_name: str) -> None:
    if st.session_state[_state_key("answered")] >= config.question_count:
        _finish_round(difficulty_name)
    else:
        st.session_state[_state_key("question")] = generate_question(config)
        st.session_state[_state_key("status")] = "answering"
        st.session_state[_state_key("last_correct")] = None


def _render_feedback(config: Difficulty, difficulty_name: str) -> None:
    question: Question = st.session_state[_state_key("question")]
    is_correct: bool = st.session_state[_state_key("last_correct")]
    answered: int = st.session_state[_state_key("answered")]

    if is_correct:
        streak: int = st.session_state[_state_key("streak")]
        earned = points_for_correct(streak)
        st.success(f"答对啦！获得 {earned} 分 ⭐")
    else:
        st.error(f"这题的答案是：{question.explanation}。记住它，下次就会啦！")

    button_label = "查看闯关成绩 🏆" if answered >= config.question_count else "下一题 ➡️"
    if st.button(button_label, type="primary", use_container_width=True):
        _advance(config, difficulty_name)
        st.rerun()


def _render_summary(config: Difficulty, difficulty_name: str) -> None:
    correct: int = st.session_state[_state_key("correct")]
    score: int = st.session_state[_state_key("score")]
    best_streak: int = st.session_state[_state_key("best_streak")]
    best_scores: dict[str, int] = st.session_state[_state_key("best_scores")]
    accuracy = correct / config.question_count

    if accuracy >= 0.8:
        title = "🥇 金牌小勇士"
        message = "太厉害了，你已经掌握得很棒！"
    elif accuracy >= 0.6:
        title = "🥈 银牌小勇士"
        message = "表现不错，再挑战一次就能冲击金牌！"
    else:
        title = "🌱 成长小勇士"
        message = "每答一道题都在进步，继续加油！"

    st.success(f"{title}：{message}")
    st.markdown(f"### {'⭐' * correct or '继续收集星星吧！'}")
    first, second, third = st.columns(3)
    first.metric("答对题目", f"{correct}/{config.question_count}")
    second.metric("本局得分", f"{score} 分")
    third.metric("最高连胜", f"{best_streak} 题")
    st.caption(f"这个难度的最佳成绩：{best_scores[difficulty_name]} 分")
    st.balloons()

    if st.button("再闯一次 🔄", type="primary", use_container_width=True):
        _start_round(difficulty_name)
        st.rerun()


def render() -> None:
    """Render one Math Warrior challenge."""
    _apply_styles()
    st.header("🧮 数学小勇士")
    st.write("答题收集星星，连续答对还能获得更多分数！")

    difficulty_name = st.selectbox(
        "选择难度",
        options=list(DIFFICULTIES),
        key=f"{STATE_PREFIX}_difficulty_picker",
        help="切换难度会自动开始新的挑战。",
    )
    config = DIFFICULTIES[difficulty_name]
    st.caption(config.description)
    _ensure_round(difficulty_name)

    status: str = st.session_state[_state_key("status")]
    if status == "finished":
        _render_summary(config, difficulty_name)
        return

    answered: int = st.session_state[_state_key("answered")]
    score: int = st.session_state[_state_key("score")]
    streak: int = st.session_state[_state_key("streak")]
    question: Question = st.session_state[_state_key("question")]
    current_question = (
        answered
        if status == "feedback"
        else min(answered + 1, config.question_count)
    )

    first, second, third = st.columns(3)
    first.metric("当前题目", f"{current_question}/{config.question_count}")
    second.metric("勇士积分", f"{score} 分")
    third.metric("连续答对", f"{streak} 题")
    st.progress(
        answered / config.question_count,
        text=f"已经完成 {answered} 道题",
    )
    st.markdown(
        f'<div class="math-question-card">{question.prompt}</div>',
        unsafe_allow_html=True,
    )

    if status == "answering":
        round_number: int = st.session_state[_state_key("round")]
        with st.form(
            key=f"{STATE_PREFIX}_form_{round_number}_{answered}",
            clear_on_submit=False,
        ):
            answer = st.number_input(
                "你的答案",
                min_value=0,
                max_value=100,
                step=1,
            )
            submitted = st.form_submit_button(
                "提交答案 ⚔️",
                type="primary",
                use_container_width=True,
            )
        if submitted:
            _submit_answer(int(answer))
            st.rerun()
    else:
        _render_feedback(config, difficulty_name)
