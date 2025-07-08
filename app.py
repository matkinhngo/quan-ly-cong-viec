import streamlit as st
import json
import pandas as pd
import plotly.express as px
from datetime import datetime

# ----------------------
# Load & Save Data
# ----------------------
def load_users():
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
            if not users:
                raise ValueError("Empty users.json")
            return users
    except:
        # Khởi tạo user mặc định nếu file lỗi/trống
        default_users = [{"username": "admin", "password": "admin123", "role": "admin"}]
        save_users(default_users)
        return default_users

def load_tasks():
    try:
        with open('tasks.json', 'r', encoding='utf-8') as f:
            tasks = json.load(f)
            if not tasks:
                return []
            return tasks
    except:
        return []

def save_users(users):
    with open('users.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def save_tasks(tasks):
    with open('tasks.json', 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

# ----------------------
# Login
# ----------------------
def login(users):
    st.sidebar.title("🔐 Đăng nhập")
    username = st.sidebar.text_input("👤 Tên đăng nhập")
    password = st.sidebar.text_input("🔑 Mật khẩu", type="password")
    if st.sidebar.button("Đăng nhập"):
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            st.session_state['user'] = user
            st.success(f"Xin chào, {username} ({user['role']})")
            st.experimental_rerun()
        else:
            st.error("❌ Sai tên đăng nhập hoặc mật khẩu")
    return st.session_state.get('user')

# ----------------------
# Dashboard
# ----------------------
def dashboard(tasks, user):
    st.title("📊 Dashboard Tổng Quan")
    user_tasks = [t for t in tasks if user['role'] == 'admin' or t['group'] == user.get('group')]
    if not user_tasks:
        st.info("📭 Chưa có công việc nào.")
        return
    df = pd.DataFrame(user_tasks)
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df, names='status', title='Tỉ lệ trạng thái công việc')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(df, x='assigned_to', color='status', title='Tiến độ theo nhân sự')
        st.plotly_chart(fig, use_container_width=True)

# ----------------------
# Quản lý công việc
# ----------------------
def task_manager(tasks, user):
    st.title("📋 Quản Lý Công Việc")
    user_tasks = [t for t in tasks if user['role'] == 'admin' or t['group'] == user.get('group')]
    if user_tasks:
        df = pd.DataFrame(user_tasks)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("📭 Không có công việc nào.")

    if user['role'] in ['admin', 'quanly']:
        st.subheader("➕ Tạo Công Việc Mới")
        with st.form("new_task_form"):
            title = st.text_input("Tiêu đề")
            description = st.text_area("Mô tả")
            assigned_to = st.text_input("Giao cho (username)")
            deadline = st.date_input("Deadline", datetime.now())
            priority = st.selectbox("Độ ưu tiên", ["Cao", "Trung bình", "Thấp"])
            submitted = st.form_submit_button("Tạo")
            if submitted and title and assigned_to:
                new_task = {
                    "task_id": len(tasks) + 1,
                    "title": title,
                    "description": description,
                    "assigned_to": assigned_to,
                    "status": "Todo",
                    "deadline": str(deadline),
                    "priority": priority,
                    "group": user['group'] if user['role'] == 'quanly' else "Team A"
                }
                tasks.append(new_task)
                save_tasks(tasks)
                st.success("✅ Đã tạo công việc!")
                st.experimental_rerun()

# ----------------------
# Quản lý người dùng
# ----------------------
def user_manager(users, current_user):
    st.title("👥 Quản Lý Người Dùng")
    if current_user['role'] != 'admin':
        st.warning("⚠️ Bạn không có quyền truy cập.")
        return

    st.subheader("📄 Danh sách người dùng")
    df = pd.DataFrame(users)
    st.dataframe(df, use_container_width=True)

    st.subheader("➕ Thêm Người Dùng")
    with st.form("add_user_form"):
        username = st.text_input("Tên đăng nhập mới")
        password = st.text_input("Mật khẩu")
        role = st.selectbox("Quyền", ["admin", "quanly", "member"])
        group = st.text_input("Nhóm (cho quản lý và member)")
        submitted = st.form_submit_button("Thêm")
        if submitted and username and password:
            if any(u['username'] == username for u in users):
                st.error("❌ Tên đăng nhập đã tồn tại.")
            else:
                new_user = {"username": username, "password": password, "role": role}
                if role in ['quanly', 'member']:
                    new_user['group'] = group
                users.append(new_user)
                save_users(users)
                st.success("✅ Đã thêm người dùng mới.")
                st.experimental_rerun()

# ----------------------
# Main App
# ----------------------
def main():
    st.set_page_config(page_title="Quản Lý Công Việc", layout="wide")
    if 'user' not in st.session_state:
        st.session_state['user'] = None

    users = load_users()
    tasks = load_tasks()
    user = st.session_state['user'] or login(users)

    if user:
        menu = ["🏠 Trang Chủ", "📋 Công Việc", "👥 Người Dùng", "📊 Báo Cáo"]
        choice = st.sidebar.radio("📌 Menu", menu)

        if choice == "🏠 Trang Chủ":
            dashboard(tasks, user)
        elif choice == "📋 Công Việc":
            task_manager(tasks, user)
        elif choice == "👥 Người Dùng":
            user_manager(users, user)
        elif choice == "📊 Báo Cáo":
            dashboard(tasks, user)

if __name__ == "__main__":
    main()
