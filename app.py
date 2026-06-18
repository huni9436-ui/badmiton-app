import streamlit as st
import csv
import os

# -------------------------------------------------
# 0. 기본 설정
# -------------------------------------------------
st.set_page_config(
    page_title="민턴매칭",
    layout="wide"
)

st.title("🏸 민턴매칭 - 회원저장형 수동 클릭 배정 운영판")

MEMBERS_FILE = "members.csv"


# -------------------------------------------------
# 1. 급수 점수 변환
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


# -------------------------------------------------
# 2. members.csv 준비 / 불러오기 / 저장
# -------------------------------------------------
def ensure_members_file():
    if not os.path.exists(MEMBERS_FILE):
        with open(MEMBERS_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["name", "gender", "age_group", "level", "score", "total_games"]
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
            fieldnames=["name", "gender", "age_group", "level", "score", "total_games"]
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
# 3. 빈 경기 생성
# -------------------------------------------------
def empty_match():
    return {
        "a1": None,
        "a2": None,
        "b1": None,
        "b2": None
    }


# -------------------------------------------------
# 4. 세션 상태 초기화
# -------------------------------------------------
ensure_members_file()

if "members" not in st.session_state:
    st.session_state.members = load_members()

if "today_players" not in st.session_state:
    st.session_state.today_players = []

if "selected_player" not in st.session_state:
    st.session_state.selected_player = None

if "active_courts" not in st.session_state:
    st.session_state.active_courts = [empty_match(), empty_match(), empty_match()]

if "waiting_courts" not in st.session_state:
    st.session_state.waiting_courts = [empty_match(), empty_match(), empty_match()]

if "completed_count" not in st.session_state:
    st.session_state.completed_count = 0


# -------------------------------------------------
# 5. 회원 / 오늘 참석자 관련 함수
# -------------------------------------------------
def get_member(name):
    if name is None:
        return None

    for member in st.session_state.members:
        if member["name"] == name:
            return member

    return None


def get_today_player(name):
    if name is None:
        return None

    for player in st.session_state.today_players:
        if player["name"] == name:
            return player

    return None


def add_member_to_today(member):
    existing_names = [p["name"] for p in st.session_state.today_players]

    if member["name"] in existing_names:
        st.warning(f"{member['name']}님은 이미 오늘 참석자에 있습니다.")
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

    existing_member_names = [m["name"] for m in st.session_state.members]

    if name in existing_member_names:
        st.warning(f"{name}님은 이미 전체 회원명부에 있습니다. 기존 회원 목록에서 오늘 참석 추가를 눌러주세요.")
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


def remove_today_player(name):
    remove_player_from_all_slots(name)

    if st.session_state.selected_player == name:
        st.session_state.selected_player = None

    st.session_state.today_players = [
        p for p in st.session_state.today_players
        if p["name"] != name
    ]


def player_info_text(player):
    return (
        f"{player['gender']} / {player['age_group']} / "
        f"{player['level']}급 / 오늘 {player['today_games']}경기 / 누적 {player['total_games']}경기"
    )


def short_player_label(name):
    player = get_today_player(name)

    if player is None:
        return "빈칸"

    return f"{player['name']} ({player['level']} / 오늘 {player['today_games']}경기)"


# -------------------------------------------------
# 6. 배정 관련 함수
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


def assign_selected_player(match_type, court_index, slot):
    selected = st.session_state.selected_player

    if selected is None:
        st.warning("먼저 왼쪽에서 선수를 선택해야 합니다.")
        return

    # 오늘 참석자에 있는 사람만 배정 가능
    if get_today_player(selected) is None:
        st.warning("오늘 참석자에 없는 선수입니다.")
        return

    # 이미 다른 칸에 있으면 기존 위치에서 제거
    remove_player_from_all_slots(selected)

    if match_type == "active":
        st.session_state.active_courts[court_index][slot] = selected
    elif match_type == "waiting":
        st.session_state.waiting_courts[court_index][slot] = selected


def clear_slot(match_type, court_index, slot):
    if match_type == "active":
        st.session_state.active_courts[court_index][slot] = None
    elif match_type == "waiting":
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
# 7. 경기 종료 처리
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
        st.warning(f"{court_index + 1}코트는 4명이 모두 배정되지 않았습니다. 그래도 종료 처리하려면 빈칸을 채워주세요.")
        return

    # 현재 코트 선수 경기수 +1
    for name in match_names(current_match):
        player = get_today_player(name)

        if player is not None:
            player["today_games"] += 1
            player["total_games"] += 1
            increase_member_total_game(name)

    save_members(st.session_state.members)

    st.session_state.completed_count += 1

    # 대기 1번을 해당 진행코트로 이동
    st.session_state.active_courts[court_index] = st.session_state.waiting_courts[0]

    # 대기 경기 앞으로 당기기
    st.session_state.waiting_courts[0] = st.session_state.waiting_courts[1]
    st.session_state.waiting_courts[1] = st.session_state.waiting_courts[2]
    st.session_state.waiting_courts[2] = empty_match()


# -------------------------------------------------
# 8. 팀 점수 계산
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
# 9. 슬롯 버튼 표시
# -------------------------------------------------
def slot_button(label, match_type, court_index, slot):
    if match_type == "active":
        current_name = st.session_state.active_courts[court_index][slot]
    else:
        current_name = st.session_state.waiting_courts[court_index][slot]

    if current_name is None:
        button_label = f"➕ {label}\n빈칸"
    else:
        button_label = f"✅ {label}\n{short_player_label(current_name)}"

    if st.button(button_label, key=f"{match_type}_{court_index}_{slot}_assign"):
        assign_selected_player(match_type, court_index, slot)
        st.rerun()

    if current_name is not None:
        if st.button("비우기", key=f"{match_type}_{court_index}_{slot}_clear"):
            clear_slot(match_type, court_index, slot)
            st.rerun()


# -------------------------------------------------
# 10. 경기 카드 표시
# -------------------------------------------------
def render_match_card(title, match_type, court_index):
    if match_type == "active":
        match = st.session_state.active_courts[court_index]
    else:
        match = st.session_state.waiting_courts[court_index]

    with st.container(border=True):
        st.subheader(title)

        gap, a_score, b_score = match_score_gap(match)

        if is_match_empty(match):
            st.caption("아직 배정된 선수가 없습니다.")
        elif is_match_full(match):
            st.caption(f"A팀 점수 {a_score} : B팀 점수 {b_score} / 실력차 {gap}")
        else:
            st.caption("일부 선수만 배정된 상태입니다.")

        st.markdown("#### 🟦 A팀")
        a_col1, a_col2 = st.columns(2)

        with a_col1:
            slot_button("A1", match_type, court_index, "a1")

        with a_col2:
            slot_button("A2", match_type, court_index, "a2")

        st.markdown("#### 🟥 B팀")
        b_col1, b_col2 = st.columns(2)

        with b_col1:
            slot_button("B1", match_type, court_index, "b1")

        with b_col2:
            slot_button("B2", match_type, court_index, "b2")


# -------------------------------------------------
# 11. 샘플 회원 넣기
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


# -------------------------------------------------
# 12. 전체 화면 구성
# -------------------------------------------------
left, right = st.columns([1, 2])


# -------------------------------------------------
# 13. 왼쪽: 회원명부 / 오늘 참석자
# -------------------------------------------------
with left:
    st.header("👥 회원 / 참석자 관리")

    tab_member, tab_today = st.tabs(["기존 회원 불러오기", "오늘 참석자"])

    # ---------------------------------------------
    # 기존 회원 불러오기
    # ---------------------------------------------
    with tab_member:
        st.subheader("기존 회원 목록")

        search_text = st.text_input("회원 검색", placeholder="이름 검색")

        filtered_members = st.session_state.members

        if search_text.strip() != "":
            filtered_members = [
                m for m in st.session_state.members
                if search_text.strip() in m["name"]
            ]

        st.write(f"전체 회원: {len(st.session_state.members)}명")

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
            for i, member in enumerate(filtered_members):
                already_today = member["name"] in [p["name"] for p in st.session_state.today_players]

                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])

                    with c1:
                        st.markdown(f"### {member['name']}")
                        st.write(
                            f"{member['gender']} / {member['age_group']} / "
                            f"{member['level']}급 / 누적 {member.get('total_games', 0)}경기"
                        )

                        if already_today:
                            st.caption("오늘 참석자에 추가됨")

                    with c2:
                        if already_today:
                            st.button("추가됨", key=f"already_{member['name']}", disabled=True)
                        else:
                            if st.button("오늘 참석", key=f"add_today_{member['name']}"):
                                add_member_to_today(member)
                                st.rerun()

        st.divider()

        st.subheader("신규 회원 등록")

        with st.form("new_member_form"):
            new_name = st.text_input("이름", key="new_member_name")
            new_gender = st.radio("성별", ["남", "여"], horizontal=True, key="new_member_gender")
            new_age = st.selectbox("연령대", ["20대", "30대", "40대", "50대", "60대"], key="new_member_age")
            new_level = st.selectbox("급수", ["A", "B", "C", "D", "초심"], key="new_member_level")

            new_submitted = st.form_submit_button("신규 등록 + 오늘 참석")

        if new_submitted:
            add_new_member_and_today(new_name, new_gender, new_age, new_level)
            st.rerun()

        st.divider()

        if st.button("샘플 회원 30명 생성"):
            add_sample_members()
            st.rerun()

    # ---------------------------------------------
    # 오늘 참석자
    # ---------------------------------------------
    with tab_today:
        st.subheader("오늘 참석자")

        c1, c2 = st.columns(2)

        with c1:
            st.metric("오늘 참석자", len(st.session_state.today_players))

        with c2:
            st.metric("완료 경기", st.session_state.completed_count)

        assigned_count = len(all_assigned_names())
        rest_count = len(get_rest_players())

        c3, c4 = st.columns(2)

        with c3:
            st.metric("배정 인원", assigned_count)

        with c4:
            st.metric("휴식 인원", rest_count)

        st.divider()

        st.subheader("🎯 선택된 선수")

        if st.session_state.selected_player is None:
            st.info("선수를 선택하세요.")
        else:
            selected = get_today_player(st.session_state.selected_player)

            if selected is not None:
                st.success(
                    f"{selected['name']} 선택됨\n\n"
                    f"{player_info_text(selected)}"
                )

                if st.button("선택 해제"):
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
                    line1, line2 = st.columns([3, 1])

                    with line1:
                        if is_selected:
                            st.markdown(f"### 🟢 {player['name']}")
                        elif is_assigned:
                            st.markdown(f"### 🔵 {player['name']}")
                        else:
                            st.markdown(f"### ⚪ {player['name']}")

                        st.write(player_info_text(player))

                        if is_assigned:
                            st.caption("현재 코트 또는 대기코트에 배정됨")
                        else:
                            st.caption("휴식자 / 배정 가능")

                    with line2:
                        if st.button("선택", key=f"select_today_player_{i}"):
                            st.session_state.selected_player = player["name"]
                            st.rerun()

                        if st.button("오늘 제외", key=f"remove_today_player_{i}"):
                            remove_today_player(player["name"])
                            st.rerun()

        st.divider()

        if st.button("오늘 참석자 전체 초기화"):
            st.session_state.today_players = []
            st.session_state.selected_player = None
            st.session_state.active_courts = [empty_match(), empty_match(), empty_match()]
            st.session_state.waiting_courts = [empty_match(), empty_match(), empty_match()]
            st.session_state.completed_count = 0
            st.rerun()


# -------------------------------------------------
# 14. 오른쪽: 경기 운영판
# -------------------------------------------------
with right:
    st.header("🏸 경기 운영판")

    st.info(
        "사용 방법: 왼쪽 '오늘 참석자' 탭에서 선수를 선택한 뒤, "
        "진행코트 또는 대기코트의 빈칸을 클릭하면 배정됩니다."
    )

    st.divider()

    st.header("🔥 진행코트 3개")

    active_cols = st.columns(3)

    for i in range(3):
        with active_cols[i]:
            render_match_card(f"{i + 1}코트", "active", i)

            if not is_match_empty(st.session_state.active_courts[i]):
                if st.button(
                    f"{i + 1}코트 경기 종료 → 대기 1번 투입",
                    key=f"finish_active_{i}"
                ):
                    finish_active_court(i)
                    st.rerun()

    st.divider()

    st.header("⏳ 대기코트 3개")

    waiting_cols = st.columns(3)

    for i in range(3):
        with waiting_cols[i]:
            render_match_card(f"대기 {i + 1}번 경기", "waiting", i)

    st.divider()

    st.header("🪑 휴식자 / 다음 배정 후보")

    rest_players = get_rest_players()

    if len(rest_players) == 0:
        st.write("현재 휴식자가 없습니다.")
    else:
        rest_cols = st.columns(4)

        for i, player in enumerate(rest_players):
            with rest_cols[i % 4]:
                with st.container(border=True):
                    st.markdown(f"### {player['name']}")
                    st.write(player_info_text(player))

                    if st.button("이 선수 선택", key=f"rest_select_{i}"):
                        st.session_state.selected_player = player["name"]
                        st.rerun()