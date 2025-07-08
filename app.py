import streamlit as st
import json
import pandas as pd
import plotly.express as px
from datetime import datetime

# ----------------------
# Load & Save Functions
# ----------------------
def load_users():
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return [{"username": "admin", "password": "admin123", "role": "admin"}]

def load_tasks():
    try:
        with open('tasks.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_tasks(tasks):
    try:
        with open('tasks.json', 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
    except:
        st.error("❌ Lỗi lưu dữ liệu!")

# ----------------------
# Login Function
# ----------------------
def login(users):
    st.sidebar.title("🔐 Đăng nhập")
    username = st.sidebar.text_input("👤 Tên đăng nhập")
    password = st.sidebar.text_input("🔑 Mật khẩu", type="password")
    login_btn = st.sidebar.button("Đăng nhập")
    if login_btn:
        user = next((u for u in users if u['username'] == username and u['password'] == password), None)
        if user:
            st.sidebar.success(f"Xin chào, {username} ({user['role']})")
            return user
        else:
            st.sidebar.error("❌ Sai tên đăng nhập hoặc mật khẩu")
    return None

# ----------------------
# Dashboard Function
# ----------------------
def dashboard(tasks, user):
    st.title("📊 Dashboard Công Việc")
    group_tasks = [t for t in tasks if user['role'] == 'admin' or t['group'] == user.get('group')]

    if not group_tasks:
        st.info("📭 Không có công việc nào để hiển thị.")
        return

    df = pd.DataFrame(group_tasks)
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df, names='status', title='Tỉ lệ công việc theo trạng thái')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(df, x='assigned_to', color='status', title='Tiến độ theo người phụ trách')
        st.plotly_chart(fig, use_container_width=True)

# ----------------------
# Task Management (CRUD)
# ----------------------
def manage_tasks(tasks, user):
    st.title("📋 Danh sách công việc")
    group_tasks = [t for t in tasks if user['role'] == 'admin' or t['group'] == user.get('group')]

    if group_tasks:
        df = pd.DataFrame(group_tasks)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("📭 Không có công việc nào để hiển thị.")

    # -------- Tạo công việc mới --------
    if user['role'] in ['admin', 'quanly']:
        st.subheader("➕ Tạo công việc mới")
        with st.form("create_task"):
            title = st.text_input("Tiêu đề")
            description = st.text_area("Mô tả")
            assigned_to = st.text_input("Giao cho (username)")
            deadline = st.date_input("Deadline", datetime.now())
            priority = st.selectbox("Độ ưu tiên", ["Cao", "Vừa", "Thấp"])
            submitted = st.form_submit_button("Tạo")
            if submitted:
                if not title or not assigned_to:
                    st.warning("⚠️ Vui lòng nhập Tiêu đề và Người được giao!")
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

    # -------- Sửa / Xóa công việc --------
    if user['role'] in ['admin', 'quanly'] and group_tasks:
        st.subheader("✏️ Sửa hoặc 🗑 Xóa công việc")
        task_options = {f"{t['task_id']}: {t['title']}": t for t in group_tasks}
        selected_task = st.selectbox("Chọn công việc", list(task_options.keys()))
        task = task_options[selected_task]

        new_title = st.text_input("Tiêu đề mới", task['title'])
        new_description = st.text_area("Mô tả mới", task['description'])
        new_status = st.selectbox("Trạng thái", ["Todo", "Đang làm", "Hoàn thành"],
                                  index=["Todo", "Đang làm", "Hoàn thành"].index(task['status']))
        new_deadline = st.date_input("Deadline mới", pd.to_datetime(task['deadline']))

        if st.button("💾 Lưu thay đổi"):
            task['title'] = new_title
            task['description'] = new_description
            task['status'] = new_status
            task['deadline'] = str(new_deadline)
            save_tasks(tasks)
            st.success("✅ Đã cập nhật công việc!")

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
        menu = ["🏠 Dashboard", "📋 Danh sách công việc"]
        choice = st.sidebar.radio("📌 Menu", menu)
        if choice == "🏠 Dashboard":
            dashboard(tasks, user)
        elif choice == "📋 Danh sách công việc":
            manage_tasks(tasks, user)

if __name__ == "__main__":
    main()
