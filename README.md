# 🧠 AI-Powered Counselling and Mental Health Portal

## ✍️ Description
This project is a web-based mental health platform designed to provide emotional support and basic counselling help using both human counselors and an AI chatbot. Built with Django and enhanced with an AI assistant, the portal offers secure, anonymous mental health support for users in need.

---

## 🚀 Features
- 🔐 Secure User Registration & Login (Django Auth)
- 👨‍⚕️ Role-based dashboards for users and counselors
- 🗓️ Book 1-on-1 counselling sessions
- 🤖 AI-powered chatbot (OpenAI API) for emotional support
- 📚 Resource center with mental health articles
- 📝 Feedback collection and session history
- 🛠️ Admin panel to manage users and sessions

---

## 🔧 Tech Stack
- **Backend**: Django, Python, SQLite/PostgreSQL
- **Frontend**: HTML, CSS, Bootstrap (or React if you used it)
- **AI Integration**: OpenAI GPT API (for chatbot)
- **Other Tools**: Django REST Framework, Cloudinary (optional for media), Git/GitHub

---

## 🔗 How to Run Locally
### 1. Clone the Repo
```bash
git clone https://github.com/your-username/mental-health-portal.git
cd mental-health-portal

 Create a Virtual Environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

Install Dependencies
pip install -r requirements.txt

Run Migrations and Start Server
python manage.py migrate
python manage.py runserver
