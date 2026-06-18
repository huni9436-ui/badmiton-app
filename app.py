import streamlit as st
import csv
import os

# -------------------------------------------------
# 0. 기본 설정
# -------------------------------------------------
st.set_page_config(
    page_title="빡세민턴 경기운영판",
    layout="wide"
)

st.title("🏸 빡세민턴 경기운영판")

MEMBERS_FILE = "members.csv"


# -------------------------------------------------
# 0-1. 화면 압축 CSS + 팀 색상
# -------------------------------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 0.3rem !important;
    padding-bottom: 0.3rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
    max-width: 100% !important;
}

h1 {
    font-size: 1.35rem !important;
    margin-bottom: 0.2rem !important;
}

h2 {
    font-size: 1.05rem !important;
    margin-top: 0.2rem !important;
    margin-bottom: 0.2rem !important;
}

h3 {
    font-size: 0.9rem !important;
    margin-top: 0.15rem !important;
    margin-bottom: 0.15rem !important;
}

h4 {
    font-size: 0.78rem !important;
    margin-top: 0.1rem !important;
    margin-bottom: 0.1rem !important;
}

.stButton > button {
    padding: 0.18rem 0.25rem !important;
    font-size: 0.68rem !important;
    min-height: 1.45rem !important;
    line-height: 1.05rem !important;
    white-space: normal !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    padding: 0.25rem !important;
}

[data-testid="column"] {
    padding-left: 0.1rem !important;
    padding-right: 0.1rem !important;
}

[data-testid="stMetricValue"] {
    font-size: 0.95rem !important;
}

[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
}

p, div, span {
    font-size: 0.78rem;
}

hr {
    margin-top: 0.25rem !important;
    margin-bottom: 0.25rem !important;
}

div[data-testid="stExpander"] summary {
    font-size: 0.8rem !important;
    padding-top: 0.25rem !important;
    padding-bottom: 0.25rem !important;
}

/* 팀 색상 */
.team-blue-title {
    background: #dbeafe;
    border: 1px solid #3b82f6;
    color: #1d4ed8;
    font-weight: 900;
    text-align: center;
    border-radius: 8px;
    padding: 0.12rem;
    margin: 0.12rem 0;
}

.team-red-title {
    background: #fee2e2;
    border: 1px solid #ef4444;
    color: #b91c1c;
    font-weight: 900;
    text-align: center;
    border-radius: 8px;
    padding: 0.12rem;
    margin: 0.12rem 0;
}

.score-line {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 0.12rem;
    text-align: center;
    font-weight: 800;
    margin-bottom: 0.15rem;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
    }

    h1 {
        font-size: 1.05rem !important;
    }

    .stButton > button {
        font-size: 0.6rem !important;
        min-height: 1.35rem !important;
        padding: 0.12rem 0.18rem !important;
    }

    p, div, span {
        font-size: 0.68rem;
    }
}
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# 1. 기본 함수
# -------------------------------------------------
def level_to_score(level):
    score_map = {
        "A": 5,
        "B": 4,
        "C": 3,
        "D": 2,
        "초심": 1
    }
    return score_map[level]


def empty_match():
    return {
        "a1": None,
        "a2": None,
        "b1": None,
        "b2": None
    }


def age_short(age_group):
    return str(age_group).replace("대", "")


# -------------------------------------------------
# 2. 회원 CSV 저장 / 불러오기
# -------------------------------------------------
def ensure_members_file():
    if not os.path.exists(MEMBERS_FILE):
        with open(MEMBERS_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "name",
                    "gender",
                    "age_group",
                    "level",
                    "score",
                    "total_games"
                ]
            )
            writer.writeheader()


def load_members():
    ensure_members_file()

    members = []

    with open(MEMBERS_FILE, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row.get("name", "").strip() == "":
                continue

            members.append({
                "name": row["name"],
                "gender": row["gender"],
                "age_group": row["age_group"],
                "level": row["level"],
                "score": int(row["score"]),
                "total_games": int(row.get("total_games", 0))
            })

    return members


def save_members(members):
    with open(MEMBERS_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "name",
                "gender",
                "age_group",
                "level",
                "score",
                "total_games"
            ]
        )
        writer.writeheader()

        for member in members:
            writer.writerow({
                "name": member["name"],
                "gender": member["gender"],
                "age_group": member["age_group"],
                "level": member["level"],
                "score": member["score"],
                "total_games": member.get("total_games", 0)
            })


# -------------------------------------------------
# 3. 세션 상태 초기화
# -------------------------------------------------
ensure_members_file()

if "members" not in st.session_state:
    st.session_state.members = load_members()

if "today_players" not in st.session_state:
    st.session_state.today_players = []

if "selected_player" not in st.session_state:
    st.session_state.selected_player = None

if "active_courts" not in st.session_state:
    st.session_state.active_courts = [
        empty_match(),
        empty_match(),
        empty_match()
    ]

if "waiting_courts" not in st.session_state:
    st.session_state.waiting_courts = [
        empty_match(),
        empty_match(),
        empty_match()
    ]

if "completed_count" not in st.session_state:
    st.session_state.completed_count = 0


# -------------------------------------------------
# 4. 회원 / 오늘 참석자 함수
# -------------------------------------------------
def get_today_player(name):
    if name is None:
        return None

    for player in st.session_state.today_players:
        if player["name"] == name:
            return player

    return None


def add_member_to_today(member):
    today_names = [p["name"] for p in st.session_state.today_players]

    if member["name"] in today_names:
        st.warning(f"{member['name']}님은 이미 오늘 참석자입니다.")
        return

    today_player = {
        "name": member["name"],
        "gender": member["gender"],
        "age_group": member["age_group"],
        "level": member["level"],
        "score": member["score"],
        "today_games": 0,
        "total_games": member.get("total_games", 0)
    }

    st.session_state.today_players.append(today_player)


def add_new_member_and_today(name, gender, age_group, level):
    name = name.strip()

    if name == "":
        st.warning("이름을 입력해야 합니다.")
        return

    member_names = [m["name"] for m in st.session_state.members]

    if name in member_names:
        st.warning(f"{name}님은 이미 회원명부에 있습니다. 참석자 관리 화면에서 오늘 참석 추가를 눌러주세요.")
        return

    new_member = {
        "name": name,
        "gender": gender,
        "age_group": age_group,
        "level": level,
        "score": level_to_score(level),
        "total_games": 0
    }

    st.session_state.members.append(new_member)
    save_members(st.session_state.members)

    add_member_to_today(new_member)

    st.success(f"{name}님 신규 등록 및 오늘 참석 추가 완료!")


def player_info_text(player):
    return (
        f"{player['gender']} / {player['age_group']} / "
        f"{player['level']}급 / 오늘 {player['today_games']}경기 / "
        f"누적 {player['total_games']}경기"
    )


def member_info_text(member):
    return (
        f"{member['gender']} / {member['age_group']} / "
        f"{member['level']}급 / 누적 {member.get('total_games', 0)}경기"
    )


def short_player_label(name):
    player = get_today_player(name)

    if player is None:
        return "빈칸"

    return f"{player['name']}({player['level']}, {age_short(player['age_group'])})"


# -------------------------------------------------
# 5. 코트 배정 함수
# -------------------------------------------------
def all_assigned_names():
    names = set()

    for match in st.session_state.active_courts:
        for slot in ["a1", "a2", "b1", "b2"]:
            if match[slot] is not None:
                names.add(match[slot])

    for match in st.session_state.waiting_courts:
        for slot in ["a1", "a2", "b1", "b2"]:
            if match[slot] is not None:
                names.add(match[slot])

    return names


def remove_player_from_all_slots(player_name):
    if player_name is None:
        return

    for match in st.session_state.active_courts:
        for slot in ["a1", "a2", "b1", "b2"]:
            if match[slot] == player_name:
                match[slot] = None

    for match in st.session_state.waiting_courts:
        for slot in ["a1", "a2", "b1", "b2"]:
            if match[slot] == player_name:
                match[slot] = None


def remove_today_player(name):
    remove_player_from_all_slots(name)

    if st.session_state.selected_player == name:
        st.session_state.selected_player = None

    st.session_state.today_players = [
        p for p in st.session_state.today_players
        if p["name"] != name
    ]


def delete_member_from_members(name):
    # 오늘 참석자, 진행코트, 대기코트에서도 제거
    remove_today_player(name)

    # 전체 회원명부에서 제거
    st.session_state.members = [
        member for member in st.session_state.members
        if member["name"] != name
    ]

    # CSV 저장
    save_members(st.session_state.members)


def assign_selected_player(match_type, court_index, slot):
    selected = st.session_state.selected_player

    if selected is None:
        st.warning("먼저 선수를 선택해야 합니다.")
        return

    if get_today_player(selected) is None:
        st.warning("오늘 참석자에 없는 선수입니다.")
        return

    remove_player_from_all_slots(selected)

    if match_type == "active":
        st.session_state.active_courts[court_index][slot] = selected

    if match_type == "waiting":
        st.session_state.waiting_courts[court_index][slot] = selected


def clear_slot(match_type, court_index, slot):
    if match_type == "active":
        st.session_state.active_courts[court_index][slot] = None

    if match_type == "waiting":
        st.session_state.waiting_courts[court_index][slot] = None


def match_names(match):
    return [
        match["a1"],
        match["a2"],
        match["b1"],
        match["b2"]
    ]


def is_match_empty(match):
    return all(name is None for name in match_names(match))


def is_match_full(match):
    return all(name is not None for name in match_names(match))


def get_rest_players():
    assigned = all_assigned_names()

    return [
        player for player in st.session_state.today_players
        if player["name"] not in assigned
    ]


# -------------------------------------------------
# 6. 경기 종료 처리
# -------------------------------------------------
def increase_member_total_game(name):
    for member in st.session_state.members:
        if member["name"] == name:
            member["total_games"] = int(member.get("total_games", 0)) + 1
            break


def finish_active_court(court_index):
    current_match = st.session_state.active_courts[court_index]

    if is_match_empty(current_match):
        st.warning(f"{court_index + 1}코트에는 진행 중인 경기가 없습니다.")
        return

    if not is_match_full(current_match):
        st.warning(f"{court_index + 1}코트는 4명이 모두 배정되지 않았습니다.")
        return

    for name in match_names(current_match):
        player = get_today_player(name)

        if player is not None:
            player["today_games"] += 1
            player["total_games"] += 1
            increase_member_total_game(name)

    save_members(st.session_state.members)

    st.session_state.completed_count += 1

    st.session_state.active_courts[court_index] = st.session_state.waiting_courts[0]
    st.session_state.waiting_courts[0] = st.session_state.waiting_courts[1]
    st.session_state.waiting_courts[1] = st.session_state.waiting_courts[2]
    st.session_state.waiting_courts[2] = empty_match()


# -------------------------------------------------
# 7. 팀 점수 계산
# -------------------------------------------------
def team_score(name1, name2):
    score = 0

    for name in [name1, name2]:
        player = get_today_player(name)
        if player is not None:
            score += player["score"]

    return score


def match_score_gap(match):
    a_score = team_score(match["a1"], match["a2"])
    b_score = team_score(match["b1"], match["b2"])
    return abs(a_score - b_score), a_score, b_score


# -------------------------------------------------
# 8. 슬롯 버튼 / 경기 카드
# -------------------------------------------------
def slot_button(label, match_type, court_index, slot, team_color):
    if match_type == "active":
        current_name = st.session_state.active_courts[court_index][slot]
    else:
        current_name = st.session_state.waiting_courts[court_index][slot]

    if current_name is None:
        if team_color == "blue":
            button_label = f"🟦 {label}"
        else:
            button_label = f"🟥 {label}"
    else:
        if team_color == "blue":
            button_label = f"🟦 {short_player_label(current_name)}"
        else:
            button_label = f"🟥 {short_player_label(current_name)}"

    if st.button(button_label, key=f"{match_type}_{court_index}_{slot}_assign"):
        assign_selected_player(match_type, court_index, slot)
        st.rerun()


def render_match_card(title, match_type, court_index):
    if match_type == "active":
        match = st.session_state.active_courts[court_index]
    else:
        match = st.session_state.waiting_courts[court_index]

    with st.container(border=True):
        gap, a_score, b_score = match_score_gap(match)

        if is_match_full(match):
            st.markdown(
                f'<div class="score-line"><b>{title}</b> | A {a_score} : B {b_score}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="score-line"><b>{title}</b></div>',
                unsafe_allow_html=True
            )

        st.markdown(
            '<div class="team-blue-title">🟦 A팀</div>',
            unsafe_allow_html=True
        )

        a1, a2 = st.columns(2)

        with a1:
            slot_button("A1", match_type, court_index, "a1", "blue")

        with a2:
            slot_button("A2", match_type, court_index, "a2", "blue")

        st.markdown(
            '<div class="team-red-title">🟥 B팀</div>',
            unsafe_allow_html=True
        )

        b1, b2 = st.columns(2)

        with b1:
            slot_button("B1", match_type, court_index, "b1", "red")

        with b2:
            slot_button("B2", match_type, court_index, "b2", "red")

        if match_type == "active" and not is_match_empty(match):
            if st.button("경기 종료", key=f"finish_compact_{court_index}"):
                finish_active_court(court_index)
                st.rerun()


# -------------------------------------------------
# 9. 샘플 / 초기화 함수
# -------------------------------------------------
def add_sample_members():
    sample_members = []

    levels = ["A", "B", "C", "D", "초심"]
    genders = ["남", "여"]
    ages = ["20대", "30대", "40대", "50대", "60대"]

    for i in range(1, 31):
        level = levels[i % len(levels)]
        gender = genders[i % len(genders)]
        age_group = ages[i % len(ages)]

        sample_members.append({
            "name": f"회원{i}",
            "gender": gender,
            "age_group": age_group,
            "level": level,
            "score": level_to_score(level),
            "total_games": 0
        })

    st.session_state.members = sample_members
    save_members(st.session_state.members)

    st.session_state.today_players = []
    st.session_state.selected_player = None
    st.session_state.active_courts = [empty_match(), empty_match(), empty_match()]
    st.session_state.waiting_courts = [empty_match(), empty_match(), empty_match()]
    st.session_state.completed_count = 0


def add_all_members_to_today():
    st.session_state.today_players = []

    for member in st.session_state.members:
        add_member_to_today(member)

    st.session_state.selected_player = None
    st.session_state.active_courts = [empty_match(), empty_match(), empty_match()]
    st.session_state.waiting_courts = [empty_match(), empty_match(), empty_match()]
    st.session_state.completed_count = 0


def reset_today_operation():
    st.session_state.today_players = []
    st.session_state.selected_player = None
    st.session_state.active_courts = [empty_match(), empty_match(), empty_match()]
    st.session_state.waiting_courts = [empty_match(), empty_match(), empty_match()]
    st.session_state.completed_count = 0


# -------------------------------------------------
# 10. 사이드바 메뉴
# -------------------------------------------------
page = st.sidebar.radio(
    "메뉴",
    [
        "🏸 경기 운영판",
        "👥 참석자 관리",
        "➕ 신규 회원 등록"
    ]
)

st.sidebar.divider()
st.sidebar.metric("전체 회원", len(st.session_state.members))
st.sidebar.metric("오늘 참석", len(st.session_state.today_players))
st.sidebar.metric("완료 경기", st.session_state.completed_count)

if st.session_state.selected_player is not None:
    st.sidebar.success(f"선택: {st.session_state.selected_player}")
else:
    st.sidebar.info("선택된 선수 없음")


# -------------------------------------------------
# 11. 경기 운영판 화면
# -------------------------------------------------
if page == "🏸 경기 운영판":

    if st.session_state.selected_player is None:
        st.warning("선택된 선수 없음")
    else:
        selected = get_today_player(st.session_state.selected_player)

        if selected is not None:
            c1, c2 = st.columns([5, 1])

            with c1:
                st.success(
                    f"선택: {short_player_label(selected['name'])} / 오늘 {selected['today_games']}경기"
                )

            with c2:
                if st.button("해제"):
                    st.session_state.selected_player = None
                    st.rerun()

    st.subheader("🪑 휴식자 / 다음 배정 후보")

    rest_players = get_rest_players()

    if len(rest_players) == 0:
        st.write("현재 휴식자가 없습니다.")
    else:
        rest_cols = st.columns(6)

        for i, player in enumerate(rest_players):
            with rest_cols[i % 6]:
                if st.button(
                    short_player_label(player["name"]),
                    key=f"rest_select_top_{i}"
                ):
                    st.session_state.selected_player = player["name"]
                    st.rerun()

    st.divider()

    st.subheader("🔥 진행코트")

    active_cols = st.columns(3)

    for i in range(3):
        with active_cols[i]:
            render_match_card(f"{i + 1}코트", "active", i)

    st.subheader("⏳ 대기코트")

    waiting_cols = st.columns(3)

    for i in range(3):
        with waiting_cols[i]:
            render_match_card(f"대기{i + 1}", "waiting", i)

    st.divider()

    bottom1, bottom2, bottom3, bottom4 = st.columns(4)

    with bottom1:
        st.metric("참석", len(st.session_state.today_players))

    with bottom2:
        st.metric("배정", len(all_assigned_names()))

    with bottom3:
        st.metric("휴식", len(get_rest_players()))

    with bottom4:
        st.metric("완료", st.session_state.completed_count)


# -------------------------------------------------
# 12. 참석자 관리 화면
# -------------------------------------------------
elif page == "👥 참석자 관리":
    st.header("👥 참석자 관리")

    tab_member, tab_today = st.tabs(["기존 회원 불러오기", "오늘 참석자"])

    with tab_member:
        st.subheader("기존 회원 목록")

        search_text = st.text_input("회원 검색", placeholder="이름 검색")

        filtered_members = st.session_state.members

        if search_text.strip() != "":
            filtered_members = [
                m for m in st.session_state.members
                if search_text.strip() in m["name"]
            ]

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("전체 회원", len(st.session_state.members))

        with c2:
            st.metric("오늘 참석", len(st.session_state.today_players))

        with c3:
            st.metric("검색 결과", len(filtered_members))

        c_all1, c_all2 = st.columns(2)

        with c_all1:
            if st.button("전체 회원 오늘 참석 추가"):
                add_all_members_to_today()
                st.rerun()

        with c_all2:
            if st.button("회원명부 새로고침"):
                st.session_state.members = load_members()
                st.rerun()

        st.divider()

        if len(filtered_members) == 0:
            st.write("등록된 회원이 없습니다.")
        else:
            for member in filtered_members:
                already_today = member["name"] in [
                    p["name"] for p in st.session_state.today_players
                ]

                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])

                    with c1:
                        st.markdown(f"### {member['name']}")
                        st.write(member_info_text(member))

                        if already_today:
                            st.caption("오늘 참석자에 추가됨")

                    with c2:
                        if already_today:
                            st.button(
                                "추가됨",
                                key=f"already_{member['name']}",
                                disabled=True
                            )
                        else:
                            if st.button("오늘 참석", key=f"add_today_{member['name']}"):
                                add_member_to_today(member)
                                st.rerun()

                        if st.button("회원 삭제", key=f"delete_member_{member['name']}"):
                            delete_member_from_members(member["name"])
                            st.rerun()

    with tab_today:
        st.subheader("오늘 참석자")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("오늘 참석", len(st.session_state.today_players))

        with c2:
            st.metric("배정 인원", len(all_assigned_names()))

        with c3:
            st.metric("휴식 인원", len(get_rest_players()))

        with c4:
            st.metric("완료 경기", st.session_state.completed_count)

        st.divider()

        st.subheader("🎯 선택된 선수")

        if st.session_state.selected_player is None:
            st.info("선수를 선택하세요.")
        else:
            selected = get_today_player(st.session_state.selected_player)

            if selected is not None:
                st.success(f"{short_player_label(selected['name'])} 선택됨")

                if st.button("선택 해제", key="today_unselect"):
                    st.session_state.selected_player = None
                    st.rerun()
            else:
                st.session_state.selected_player = None
                st.rerun()

        st.divider()

        if len(st.session_state.today_players) == 0:
            st.write("오늘 참석자가 없습니다. 기존 회원 목록에서 참석자를 추가하세요.")
        else:
            for i, player in enumerate(st.session_state.today_players):
                is_assigned = player["name"] in all_assigned_names()
                is_selected = player["name"] == st.session_state.selected_player

                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])

                    with c1:
                        if is_selected:
                            st.markdown(f"### 🟢 {short_player_label(player['name'])}")
                        elif is_assigned:
                            st.markdown(f"### 🔵 {short_player_label(player['name'])}")
                        else:
                            st.markdown(f"### ⚪ {short_player_label(player['name'])}")

                        st.write(player_info_text(player))

                        if is_assigned:
                            st.caption("현재 코트 또는 대기코트에 배정됨")
                        else:
                            st.caption("휴식자 / 배정 가능")

                    with c2:
                        if st.button("선택", key=f"select_today_player_{i}"):
                            st.session_state.selected_player = player["name"]
                            st.rerun()

                        if st.button("오늘 제외", key=f"remove_today_player_{i}"):
                            remove_today_player(player["name"])
                            st.rerun()

        st.divider()

        if st.button("오늘 참석자 전체 초기화"):
            reset_today_operation()
            st.rerun()


# -------------------------------------------------
# 13. 신규 회원 등록 화면
# -------------------------------------------------
elif page == "➕ 신규 회원 등록":
    st.header("➕ 신규 회원 등록")

    st.info("처음 온 사람은 여기서 등록하면 전체 회원명부에 저장되고, 오늘 참석자로도 바로 추가됩니다.")

    with st.form("new_member_form"):
        new_name = st.text_input("이름")
        new_gender = st.radio("성별", ["남", "여"], horizontal=True)
        new_age = st.selectbox("연령대", ["20대", "30대", "40대", "50대", "60대"])
        new_level = st.selectbox("급수", ["A", "B", "C", "D", "초심"])

        submitted = st.form_submit_button("신규 등록 + 오늘 참석")

    if submitted:
        add_new_member_and_today(new_name, new_gender, new_age, new_level)
        st.rerun()

    st.divider()

    st.subheader("회원명부 관리")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("샘플 회원 30명 생성"):
            add_sample_members()
            st.rerun()

    with c2:
        if st.button("회원명부 새로고침"):
            st.session_state.members = load_members()
            st.rerun()

    st.warning(
        "샘플 회원 30명 생성 버튼은 기존 members.csv 내용을 샘플 회원으로 덮어씁니다. "
        "실제 회원을 입력한 뒤에는 누르지 않는 것이 좋습니다."
    )

    st.divider()

    st.subheader("현재 전체 회원")

    if len(st.session_state.members) == 0:
        st.write("등록된 회원이 없습니다.")
    else:
        for member in st.session_state.members:
            with st.container(border=True):
                st.markdown(f"### {member['name']}")
                st.write(member_info_text(member))