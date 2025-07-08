import streamlit as st
import json

# Load users
def load_users():
    with open('users.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Load tasks
def load_tasks():
    with open('tasks.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Save tasks
def save_tasks(tasks):
    with open('tasks.json', 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

# Login
def login(users):
    st.title("🔐 Đăng nhập hệ thống")
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    if st.button("Đăng nhập"):
        for user in users:
            if user['username'] == username and user['password'] == password:
                st.success(f"Xin chào, {username} ({user['role']})")
                return user
        st.error("❌ Sai tên đăng nhập hoặc mật khẩu")
    return None

# Hiển thị công việc
def show_tasks(user, tasks):
    st.header("📋 Danh sách công việc")
    if user['role'] == 'admin':
        st.subheader("👑 Toàn bộ hệ thống")
        for task in tasks:
            st.write(task)
    elif user['role'] == 'quanly':
        st.subheader(f"👨‍💼 Nhóm: {user['group']}")
        for task in tasks:
            if task['group'] == user['group']:
                st.write(task)
    elif user['role'] == 'member':
        st.subheader("👤 Công việc nhóm")
        for task in tasks:
            if task['group'] == user['group']:
                st.write(task)

# Main app
def main():
    users = load_users()
    tasks = load_tasks()
    user = login(users)
    if user:
        show_tasks(user, tasks)

if __name__ == "__main__":
    main()
