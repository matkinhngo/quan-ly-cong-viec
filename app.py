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
            return json.load(f)
    except:
        # Tạo user mặc định nếu file trống
        return [{"username": "admin", "password": "admin123", "role": "admin"}]

def load_tasks():
    try:
        with open('tasks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_tasks(tasks):
    with open('tasks.json', 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

# ----------------------
# Login
# ----------------------
def login(users):
    with st.sidebar.form("login_form"):
        st.title("🔐 Đăng nhập")
        username = st.text_input("👤 Tên đăng nhập")
        password = st.text_input("🔑 Mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng nhập")
        if submitted:
            user = next((u for u in users if u['username'] == username and u['password'] == password), None)
            if user:
                st.success(f"Xin chào, {username} ({user['role']})")
                return user
            else:
                st.error("❌ Sai tên đăng nhập hoặc mật khẩu")
    return None

# ----------------------
# Dashboard
# ----------------------
def dashboard(tasks, user):
    st.title("📊 Tổng Quan Công Việc")
    user_tasks = [t for t in tasks if user['role'] == 'admin' or t['group'] == user.get('group')]

    if not user_tasks:
        st.info("📭 Chưa có công việc nào.")
        return

    df = pd.DataFrame(user_tasks)
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df, names='status', title='Trạng thái công việc')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(df, x='assigned_to', color='status', title='Tiến độ theo nhân sự')
        st.plotly_chart(fig, use_container_width=True)

# ----------------------
# Task Management
# ----------------------
def task_manager(tasks, user):
    st.title("📋 Quản Lý Công Việc")

    # Filter tasks by role
    user_tasks = [t for t in tasks if user['role'] == 'admin' or t['group'] == user.get('group')]

    # Hiển thị bảng công việc
    if user_tasks:
        df = pd.DataFrame(user_tasks)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("📭 Không có công việc nào để hiển thị.")

    # Form tạo công việc
    if user['role'] in ['admin', 'quanly']:
        st.subheader("➕ Tạo Công Việc Mới")
        with st.form("new_task_form"):
            title = st.text_input("Tiêu đề")
            description = st.text_area("Mô tả")
            assigned_to = st.text_input("Giao cho (username)")
            deadline = st.date_input("Deadline", datetime.now())
            priority = st.selectbox("Độ ưu tiên", ["Cao", "Trung bình", "Thấp"])
            submitted = st.form_submit_button("Tạo")
            if submitted:
                if not title or not assigned_to:
                    st.warning("⚠️ Tiêu đề và Người được giao là bắt buộc.")
                else:
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

    # Sửa/Xóa công việc
    if user['role'] in ['admin', 'quanly'] and user_tasks:
        st.subheader("✏️ Sửa / 🗑 Xóa Công Việc")
        task_map = {f"{t['task_id']}: {t['title']}": t for t in user_tasks}
        selected_task_key = st.selectbox("Chọn công việc", list(task_map.keys()))
        task = task_map[selected_task_key]

        new_title = st.text_input("Tiêu đề mới", task['title'])
        new_description = st.text_area("Mô tả mới", task['description'])
        new_status = st.selectbox("Trạng thái", ["Todo", "Đang làm", "Hoàn thành"], index=["Todo", "Đang làm", "Hoàn thành"].index(task['status']))
        new_deadline = st.date_input("Deadline mới", pd.to_datetime(task['deadline']))

        if st.button("💾 Lưu thay đổi"):
            task['title'] = new_title
            task['description'] = new_description
            task['status'] = new_status
            task['deadline'] = str(new_deadline)
            save_tasks(tasks)
            st.success("✅ Công việc đã được cập nhật.")

        if st.button("🗑 Xóa công việc"):
            tasks.remove(task)
            save_tasks(tasks)
            st.success("🗑 Đã xóa công việc!")

# ----------------------
# Main App
# ----------------------
def main():
    st.set_page_config(page_title="Quản Lý Công Việc", layout="wide")
    users = load_users()
    tasks = load_tasks()
    user = login(users)

    if user:
        menu = ["🏠 Dashboard", "📋 Công Việc"]
        choice = st.sidebar.radio("📌 Menu", menu)

        if choice == "🏠 Dashboard":
            dashboard(tasks, user)
        elif choice == "📋 Công Việc":
            task_manager(tasks, user)

if __name__ == "__main__":
    main()
