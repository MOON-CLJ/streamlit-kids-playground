"""Entry point for the Streamlit Kids Playground."""

from collections.abc import Callable

import streamlit as st

from games.number_guess import render as render_number_guess


st.set_page_config(
    page_title="童趣游戏屋",
    page_icon="🎪",
    layout="centered",
)


GAMES: dict[str, Callable[[], None]] = {
    "🔢 猜数字": render_number_guess,
}


def main() -> None:
    """Render the playground and the selected game."""
    st.title("🎪 童趣游戏屋")
    st.caption("动动脑筋，轻松玩耍，每次进步一点点！")

    with st.sidebar:
        st.header("选择游戏")
        selected_game = st.radio(
            "今天想玩什么？",
            options=list(GAMES),
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown("### 给家长的小提示")
        st.write("每局只需几分钟。可以让孩子先说出理由，再提交答案。")
        st.caption("更多小游戏可以继续添加到 games/ 目录。")

    GAMES[selected_game]()


if __name__ == "__main__":
    main()
