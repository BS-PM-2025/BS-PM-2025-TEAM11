# 📘 README: RequestFlow - Academic Request Management System

## 👥 Team Members:

* **Alaa Mkawi** 
* **Shahd Alnsasra** 
* **Lena Abu Abid** 
* **Bayan Abo Mdegam** 

---

## 📌 Project Overview

**RequestFlow** is an interactive web-based system for managing academic requests within higher education institutions. It addresses inefficiencies in the traditional request submission process by providing a structured, automated, and role-based platform that supports students, academic staff, and administrative personnel.

The system supports:

* Role-based dashboards (student, academic, secretary)
* AI-powered chatbot for guidance
* Smart routing of requests to appropriate roles
* Real-time status tracking and notifications
* Secure login, signup, and session management

---


## 🛠 Technologies Used

* **Backend**: Python (Django)
* **Frontend**: HTML, CSS, JavaScript
* **Database**: MySQL
* **Version Control**: GitHub
* **Project Management**: Jira
* **CI/CD & QA**: Jenkins, Pylint, pytest
* **IDE**: PyCharm

---

## ✅ Core Features

1. Role-Based Dashboards
2. Smart Request Routing
3. AI-Based Chatbot for FAQ Support
4. Request Status Tracking + Notifications
5. Signup, Login, Logout with Validation
6. Admin View of Categorized Requests
7. Request Filtering & View History

---


## 📌 Project Management Tools

* **Jira**: Sprint planning, task tracking
* **GitHub**: Version control, collaboration
* **Jenkins**: Continuous Integration, test automation


## 📣 System Setup & Run Instructions

### Prerequisites

* Python 3.12
* pip
* MySQL server
* Virtual environment

### Installation Steps

1. Clone the repository:

```bash
git clone https://github.com/BS-PM-2025/BS-PM-2025-TEAM11.git
cd RequestFlow
```

2. Create and activate virtual environment (optional):

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

* Set `DJANGO_SETTINGS_MODULE=RequestFlow.settings`
* Set up database credentials in `settings.py`

5. Apply migrations and create superuser:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. Run the development server:

```bash
python manage.py runserver
```

7. Access the system:
   Open your browser and go to `http://127.0.0.1:8000/`

---

Thank you for reviewing **RequestFlow**. For further documentation or credentials for demo login, please contact the development team.
