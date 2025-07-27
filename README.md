# 🚗 Vehicle Lending Web App

A full-stack Django web application that allows users to borrow and lend vehicles. This project was originally created as part of a university course group project and is now hosted in this personal GitHub repository for long-term access and portfolio use.

[🌐 Live App on Heroku](https://vehicle-lending-app-a6db4618da8a.herokuapp.com/)  

---

**⚠️ Disclaimer**  
This project was developed as part of a university course. It is no longer monitored or actively maintained.  
Do not enter any real or **sensitive** personal information.  

---

## 🛠️ Features

- User authentication with role-based access (Admin, Librarian, Patron)
- Vehicle search, request, approval/denial workflows
- Image upload and storage via AWS S3
- Google OAuth login integration
- Dynamic dashboards for each user type
- Continuous Integration via Github Actions
- Heroku-hosted PostgreSQL database
- Google maps integration

---

## 👨‍💻 My Role

I served as both the **DevOps Engineer** and a **full-stack developer** on this project.

### 🔧 DevOps Responsibilities:
- Deployed and maintained the app on **Heroku**
- Configured **Heroku PostgreSQL** and managed production `.env` secrets
- Integrated **AWS S3** for image storage
- Implemented **Google OAuth** login
- **Set up GitHub Actions** for Continuous Integration to:
  - Run tests automatically on every push
  - Deploy to Heroku **only if all tests pass**
- Managed project structure and CI/CD pipeline

### 💻 Full-Stack Development Contributions:
- Built and maintained major backend features using **Django**
- Developed frontend templates using **Django templates & Bootstrap**
- Implemented borrowing logic, approval/rejection flows, and collection logic.
- Participated in debugging and refinement of business logic

---

## 🧪 Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, Bootstrap (Django templates)
- **Database:** Heroku PostgreSQL
- **Authentication:** Google OAuth
- **Storage:** AWS S3 via `django-storages`
- **Deployment:** Heroku (Free tier)
