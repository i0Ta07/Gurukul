# 🌟 Gurukul

**Gurukul** is a modern, open-source web-based platform designed to streamline learning and assessment. Built using **Django**, Django Channels, WebSockets,NumPy, **Bootstrap 5**, and **JavaScript**, it enables educators to design interactive quizzes, manage virtual classes, and collaborate in real-time through integrated chat features.

---

## 📚 Table of Contents

* [Features](#features)
* [Technology Stack](#technology-stack)
* [Real-Time Chat (WebSockets)](#real-time-chat-websockets)
* [Installation &amp; Setup](#installation--setup)
* [Running the Application](#running-the-application)
* [Demo &amp; Comparison](#demo--comparison)
* [Contributing](#contributing)

---

## 🚀 Features

* ✅ **Quiz Management** – Build, assign, and auto-submit timed quizzes with real-time progress tracking, even across disconnects.
* 🧠 **Question Types** – Supports MCQs, true/false, and subjective answers; objective questions auto-graded.
* 🏫 **Class & User Roles** – Teachers create classes; students join via access codes; RBAC ensures secure role-based permissions.
* 📂 **Resource Sharing** – Upload and share notes, assignments, and digital library materials with public/private visibility.
* 📣 **Announcements & Assignments** – Post updates and assignments with time-based controls and basic proctoring.
* 📊 **Analytics** – Track student performance via raw and weighted scores with interactive visualizations.
* 📘 **Quiz Review & Insights** – Review wrong/missed answers and see success rates per question for targeted revision.
* 🔐 **Access-Controlled Content** – Private content protected by access codes; only authorized users can view.
* 💬 **Live Chat** – Real-time individual and group chats via WebSockets; admins manage groups and roles.
* 🌑 **Modern UI** – Responsive, mobile-first interface with Bootstrap 5 and dark mode support.
* 🛡️ **Basic Proctoring** – Monitor quiz integrity using JavaScript-based checks during exams(Exit Fullscreen, Reloads).

---

## 🧰 Technology Stack

* **Backend**: Django, Django Channels (ASGI), Python
* **Frontend**: HTML5, CSS3, Bootstrap 5, Vanilla JavaScript
* **WebSockets**: Daphne server via ASGI
* **Database**: Oracle RDBMS (`django.db.backends.oracle`)

## 💬 Real-Time Chat (WebSockets)

* Implemented with **Django Channels** and **ASGI**.
* `ChatConsumer` handles WebSocket lifecycle.

## ⚡ Zero-Reloads Quiz (WebSockets)

* Built with **Django Channels** and **ASGI** for real-time updates.
* Preserves user progress, answers, and remaining time across disconnects or page reloads using  **session-based state management** .

---

## 🛠 Installation & Setup

1. **Clone the repo**:

   ```bash
   git clone https://github.com/i0Ta07/Gurukul.git
   cd Gurukul
   ```
2. **Set up virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
4. **Update DB settings** in `Gurukul/settings.py`
5. **Apply migrations and create superuser**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

---

## ▶️ Running the Application

* **Start Django server**:

  ```bash
  python manage.py runserver
  ```
* **Start Daphne WebSocket server**:

  ```bash
  daphne -b 0.0.0.0 -p 8001 Gurukul.asgi:application
  ```

Visit: `http://localhost:8000/`
WebSocket: Port `8001`

---

## 🎥 Demo & Comparison

📹 **Project Walkthrough & Google Classroom Comparison**
Watch the full demonstration here: [Google Drive Video](https://drive.google.com/drive/folders/1Vxray1KSyuxuMMmAZlM44bU89c7zpDlf?usp=sharing)

| Feature                                  | Gurukul                                                        | Google Classroom                   |
| ---------------------------------------- | -------------------------------------------------------------- | ---------------------------------- |
| **Quiz Flexibility**               | Timed, auto-submission, MCQ/TF/Subjective types                | Limited quiz options               |
| **Grading**                        | Auto + manual descriptive grading                              | Only auto for MCQs                 |
| **Material Sharing**               | Notes/books with public/private access                         | Files only, no control over access |
| **Class Creation**                 | Teachers create + manage schedules, topics                     | Limited schedule/tracking features |
| **Chat System**                    | Built-in chat (WebSockets), groups, admin roles                | No integrated messaging            |
| **Analytics**                      | Raw + weighted marks with time insight                         | Basic score listing                |
| **Access Security**                | Private content unlockable via access codes                    | No per-resource access control     |
| **Theming**                        | Dark UI, Bootstrap 5, mobile-first                             | No theme customization             |
| **Shuffled Questions and options** | Each user have different set of shuffled questions and options | No shuffle  options                |

👉 **We highly encourage you to explore the working demonstration video** to truly grasp Gurukul’s capabilities in action.
Because **true art cannot be captured or written—it must be experienced.**

---

## 🤝 Contributing

We welcome contributions to improve Gurukul! Submit issues or PRs for:

* New features or analytics
* Improved UI/UX or dark/light theme toggles
* Code refactoring or test coverage
* AI integrations to create quizzes

---
