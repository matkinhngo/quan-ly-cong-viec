import streamlit as st
import json
import pandas as pd
import plotly.express as px

# ----------------------
# Load & Save Functions
# ----------------------
def load_users():
    with open('users.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_tasks():
    with open('tasks.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tasks(tasks):
    with open('tasks.json', 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

# ----------------------
# Login Function
# ----------------------
def login(users):
    st.sidebar.title("🔐 Đăng nhập")
    username = st.sidebar.text_input("👤 Tên đăng nhập")
    password = st.sidebar.text_input("🔑 Mật khẩu", type="password")
    if st.sidebar.button("Đăng nhập"):
        for user in users:
            if user['username'] == username and user['password'] == password:
                st.sidebar.success(f"Xin chào, {username} ({user['role']})")
                return user
        st.sidebar.error("❌ Sai tên đăng nhập hoặc mật khẩu")
    return None

# ----------------------
# Dashboard Function
# ----------------------
def dashboard(tasks, user):
    st.title("📊 Dashboard Công Việc")
    if user['role'] == 'admin':
        df = pd.DataFrame(tasks)
    else:
        df = pd.DataFrame([t for t in tasks if t['group'] == user['group']])

    if df.empty:
        st.info("📭 Không có công việc nào")
    else:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(df, names='status', title='Tỉ lệ công việc theo trạng thái')
            st.plotly_chart(fig)
        with col2:
            fig = px.bar(df, x='assigned_to', color='status', title='Tiến độ theo người phụ trách')
            st.plotly_chart(fig)

# ----------------------
# Task Management (CRUD)
# ----------------------
def manage_tasks(tasks, user):
    st.title("📋 Danh sách công việc")
    if user['role'] == 'admin':
        view_tasks = tasks
    else:
        view_tasks = [t for t in tasks if t['group'] == user['group']]
    
    df = pd.DataFrame(view_tasks)

    if df.empty:
        st.warning("📭 Nhóm bạn chưa có công việc nào!")
    else:
        st.dataframe(df, use_container_width=True)

    # -------- Tạo công việc mới --------
    if user['role'] in ['admin', 'quanly']:
        st.subheader("➕ Tạo công việc mới")
        with st.form("create_task"):
            title = st.text_input("Tiêu đề")
            description = st.text_area("Mô tả")
            assigned_to = st.text_input("Giao cho (username)")
            deadline = st.date_input("Deadline")
            priority = st.selectbox("Độ ưu tiên", ["Cao", "Vừa", "Thấp"])
            submitted = st.form_submit_button("Tạo")
            if submitted:
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
    if user['role'] in ['admin', 'quanly']:
        st.subheader("✏️ Sửa hoặc 🗑 Xóa công việc")
        task_ids = [t['task_id'] for t in view_tasks]
        selected_task_id = st.selectbox("Chọn Task ID", task_ids)
        selected_task = next((t for t in tasks if t['task_id'] == selected_task_id), None)

        if selected_task:
            new_title = st.text_input("Tiêu đề mới", selected_task['title'])
            new_description = st.text_area("Mô tả mới", selected_task['description'])
            new_status = st.selectbox("Trạng thái", ["Todo", "Đang làm", "Hoàn thành"], index=["Todo", "Đang làm", "Hoàn thành"].index(selected_task['status']))
            new_deadline = st.date_input("Deadline mới", pd.to_datetime(selected_task['deadline']))
            if st.button("💾 Lưu thay đổi"):
                selected_task['title'] = new_title
                selected_task['description'] = new_description
                selected_task['status'] = new_status
                selected_task['deadline'] = str(new_deadline)
                save_tasks(tasks)
                st.success("✅ Đã cập nhật công việc!")

            if st.button("🗑 Xóa công việc"):
                tasks.remove(selected_task)
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
