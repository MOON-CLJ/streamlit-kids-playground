"""Streamlit UI for Jungle chess (Dou Shou Qi)."""

from typing import Literal

import streamlit as st

from games.jungle_chess_logic import (
    COLUMNS,
    DENS,
    PIECE_EMOJIS,
    PIECE_NAMES,
    ROWS,
    TRAPS,
    WATER,
    Board,
    Move,
    Player,
    Position,
    apply_move,
    choose_computer_move,
    get_winner,
    initial_board,
    legal_destinations,
    legal_moves,
    opponent,
)


GameMode = Literal["computer", "two_players"]
STATE_PREFIX = "jungle_chess"
MODE_LABELS: dict[str, GameMode] = {
    "🤖 人机对战": "computer",
    "👨‍👩‍👧 本地双人": "two_players",
}
PLAYER_LABELS: dict[Player, str] = {"red": "红方", "blue": "蓝方"}
PLAYER_MARKERS: dict[Player, str] = {"red": "🔴", "blue": "🔵"}


def _state_key(name: str) -> str:
    return f"{STATE_PREFIX}_{name}"


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
        div[class*="st-key-jungle_cell_"] button {
            min-height: 4.5rem !important;
            padding: 0.2rem !important;
            border-width: 2px !important;
            border-radius: 0.75rem !important;
        }
        div[class*="st-key-jungle_cell_"] button p {
            font-size: 1.75rem !important;
            line-height: 1 !important;
            white-space: nowrap !important;
        }
        div[class*="st-key-jungle_cell_water_"] button {
            background: rgba(46, 145, 229, 0.28) !important;
        }
        div[class*="st-key-jungle_cell_trap_"] button {
            background: rgba(255, 75, 75, 0.16) !important;
        }
        div[class*="st-key-jungle_cell_den_"] button {
            background: rgba(255, 189, 69, 0.28) !important;
        }
        div[class*="st-key-jungle_cell_"][class*="_selected_"] button {
            border: 4px solid #ffbd45 !important;
        }
        div[class*="st-key-jungle_cell_"][class*="_target_"] button {
            border: 4px solid #21c354 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _start_game(mode: GameMode) -> None:
    st.session_state[_state_key("mode")] = mode
    st.session_state[_state_key("board")] = initial_board()
    st.session_state[_state_key("turn")] = "blue"
    st.session_state[_state_key("selected")] = None
    st.session_state[_state_key("winner")] = None
    st.session_state[_state_key("move_count")] = 0
    st.session_state[_state_key("captured")] = {"red": [], "blue": []}
    st.session_state[_state_key("history")] = []
    st.session_state[_state_key("hint")] = "蓝方先手，请选择一只动物。"
    st.session_state[_state_key("game_id")] = (
        st.session_state.get(_state_key("game_id"), 0) + 1
    )


def _ensure_game(mode: GameMode) -> None:
    if (
        _state_key("board") not in st.session_state
        or st.session_state.get(_state_key("mode")) != mode
    ):
        _start_game(mode)


def _terrain(position: Position) -> str:
    if position in WATER:
        return "water"
    if position in DENS.values():
        return "den"
    if any(position in traps for traps in TRAPS.values()):
        return "trap"
    return "land"


def _empty_label(position: Position) -> str:
    return {
        "water": "〰️",
        "den": "🏰",
        "trap": "🕳️",
        "land": "·",
    }[_terrain(position)]


def _coordinate(position: Position) -> str:
    row, column = position
    return f"{chr(ord('A') + column)}{row + 1}"


def _actor_name(player: Player, mode: GameMode) -> str:
    if mode == "computer":
        return "电脑" if player == "red" else "你"
    return PLAYER_LABELS[player]


def _describe_move(
    board: Board,
    move: Move,
    mode: GameMode,
) -> str:
    piece = board[move.source]
    captured = board.get(move.destination)
    description = (
        f"{_actor_name(piece.owner, mode)}："
        f"{PIECE_EMOJIS[piece.kind]}{PIECE_NAMES[piece.kind]} "
        f"{_coordinate(move.source)} → {_coordinate(move.destination)}"
    )
    if captured is not None:
        description += f"，吃掉{PIECE_EMOJIS[captured.kind]}{PIECE_NAMES[captured.kind]}"
    return description


def _commit_move(move: Move, mode: GameMode) -> None:
    board: Board = st.session_state[_state_key("board")]
    piece = board[move.source]
    captured = board.get(move.destination)
    description = _describe_move(board, move, mode)
    new_board = apply_move(board, move)
    next_player = opponent(piece.owner)

    if captured is not None:
        captured_by: dict[Player, list[str]] = {
            player: list(items)
            for player, items in st.session_state[_state_key("captured")].items()
        }
        captured_by[piece.owner].append(PIECE_EMOJIS[captured.kind])
        st.session_state[_state_key("captured")] = captured_by

    history: list[str] = list(st.session_state[_state_key("history")])
    history.append(description)
    st.session_state[_state_key("history")] = history[-6:]
    st.session_state[_state_key("board")] = new_board
    st.session_state[_state_key("selected")] = None
    st.session_state[_state_key("move_count")] += 1
    st.session_state[_state_key("turn")] = next_player
    st.session_state[_state_key("winner")] = get_winner(new_board, next_player)
    st.session_state[_state_key("hint")] = description


def _play_computer_turn(mode: GameMode) -> None:
    board: Board = st.session_state[_state_key("board")]
    move = choose_computer_move(board, "red")
    if move is None:
        st.session_state[_state_key("winner")] = "blue"
        return
    _commit_move(move, mode)


def _handle_cell_click(position: Position, mode: GameMode) -> None:
    if st.session_state[_state_key("winner")] is not None:
        return

    turn: Player = st.session_state[_state_key("turn")]
    if mode == "computer" and turn == "red":
        return

    board: Board = st.session_state[_state_key("board")]
    selected: Position | None = st.session_state[_state_key("selected")]
    piece = board.get(position)

    if selected is not None and position in legal_destinations(board, selected):
        move = next(
            move
            for move in legal_moves(board, turn)
            if move.source == selected and move.destination == position
        )
        _commit_move(move, mode)
        if (
            mode == "computer"
            and st.session_state[_state_key("winner")] is None
            and st.session_state[_state_key("turn")] == "red"
        ):
            _play_computer_turn(mode)
        return

    if piece is not None and piece.owner == turn:
        st.session_state[_state_key("selected")] = position
        destinations = len(legal_destinations(board, position))
        st.session_state[_state_key("hint")] = (
            f"已选择 {PLAYER_MARKERS[turn]}{PIECE_EMOJIS[piece.kind]}"
            f"{PIECE_NAMES[piece.kind]}，有 {destinations} 个可走位置。"
        )
    elif selected is not None:
        st.session_state[_state_key("hint")] = "这里不能走，请选择绿色边框的位置。"
    else:
        st.session_state[_state_key("hint")] = f"请先选择{PLAYER_LABELS[turn]}的动物。"


def _render_board(mode: GameMode) -> None:
    board: Board = st.session_state[_state_key("board")]
    selected: Position | None = st.session_state[_state_key("selected")]
    targets = legal_destinations(board, selected) if selected is not None else set()
    game_id: int = st.session_state[_state_key("game_id")]
    winner: Player | None = st.session_state[_state_key("winner")]

    st.caption("红方在上，蓝方在下；黄色边框是选中棋子，绿色边框是可走位置。")
    for row in range(ROWS):
        columns = st.columns(COLUMNS, gap="small")
        for column, container in enumerate(columns):
            position = (row, column)
            piece = board.get(position)
            if piece is None:
                label = _empty_label(position)
                help_text = {
                    "water": "河流：只有老鼠可以进入，狮虎可以跳过",
                    "den": "兽穴：进入对方兽穴即可获胜",
                    "trap": "陷阱：对方棋子进入后会失去战斗力",
                    "land": "空地",
                }[_terrain(position)]
            else:
                label = f"{PLAYER_MARKERS[piece.owner]}{PIECE_EMOJIS[piece.kind]}"
                help_text = (
                    f"{PLAYER_LABELS[piece.owner]}{PIECE_NAMES[piece.kind]}"
                )

            visual_state = "normal"
            if position == selected:
                visual_state = "selected"
            elif position in targets:
                visual_state = "target"

            key = (
                f"jungle_cell_{_terrain(position)}_{visual_state}_"
                f"{row}_{column}_{game_id}"
            )
            with container:
                if st.button(
                    label,
                    key=key,
                    help=help_text,
                    use_container_width=True,
                    disabled=winner is not None,
                ):
                    _handle_cell_click(position, mode)
                    st.rerun()


def _render_rules() -> None:
    with st.expander("📖 查看游戏规则"):
        st.markdown(
            """
- 双方轮流移动，每次向上、下、左、右走一格，先进入对方兽穴者获胜。
- 强弱顺序：象 ＞ 狮 ＞ 虎 ＞ 豹 ＞ 狼 ＞ 狗 ＞ 猫 ＞ 鼠；通常只能吃同级或更弱的动物。
- 老鼠可以吃大象，大象不能吃老鼠；老鼠是唯一能进入河流的动物。
- 河里的老鼠不能吃岸上的动物，岸上的动物也不能吃河里的老鼠。
- 狮子和老虎可以跳过河流，但河中有任何老鼠时不能跳。
- 对方动物进入你的陷阱后，任何一只动物都能吃掉它；不能进入自己的兽穴。
            """
        )


def render() -> None:
    """Render a playable Jungle chess game."""
    _apply_styles()
    st.header("♟️ 斗兽棋")
    st.write("指挥八只动物，穿过河流和陷阱，占领对方兽穴！")

    mode_label = st.selectbox(
        "选择玩法",
        options=list(MODE_LABELS),
        key=f"{STATE_PREFIX}_mode_picker",
        help="切换玩法会自动开始新的一局。",
    )
    mode = MODE_LABELS[mode_label]
    _ensure_game(mode)

    turn: Player = st.session_state[_state_key("turn")]
    winner: Player | None = st.session_state[_state_key("winner")]
    move_count: int = st.session_state[_state_key("move_count")]
    captured: dict[Player, list[str]] = st.session_state[_state_key("captured")]

    if winner is None:
        turn_text = (
            "轮到你（蓝方）"
            if mode == "computer" and turn == "blue"
            else f"轮到{PLAYER_LABELS[turn]}"
        )
    elif mode == "computer":
        turn_text = "你获胜了！" if winner == "blue" else "电脑获胜"
    else:
        turn_text = f"{PLAYER_LABELS[winner]}获胜！"

    st.caption("当前状态")
    st.subheader(turn_text)

    first, second = st.columns(2)
    first.metric("移动次数", f"{move_count} 步")
    second.metric(
        "吃掉棋子",
        f"🔵{len(captured['blue'])} · 🔴{len(captured['red'])}",
    )

    if winner is not None:
        if mode == "computer" and winner == "blue":
            st.success("🎉 太棒了！你成功占领了电脑的兽穴！")
        elif mode == "computer":
            st.warning("电脑先占领了兽穴。再来一局，你一定能赢！")
        else:
            st.success(f"🎉 {PLAYER_LABELS[winner]}获胜！")
        st.balloons()
    else:
        st.info(st.session_state[_state_key("hint")])

    _render_board(mode)

    history: list[str] = st.session_state[_state_key("history")]
    if history:
        st.markdown("#### 最近行动")
        for item in reversed(history[-3:]):
            st.caption(item)

    eaten = "".join(captured["blue"] + captured["red"])
    if eaten:
        st.caption(f"本局被吃掉的动物：{eaten}")

    if st.button("重新开局 🔄", type="primary", use_container_width=True):
        _start_game(mode)
        st.rerun()

    _render_rules()
