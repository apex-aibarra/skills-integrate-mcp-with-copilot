# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Persistent data storage with MySQL database
- User authentication and profiles (planned)
- Admin dashboard and management (planned)

## Getting Started

### Prerequisites

- Python 3.8+
- MySQL Server
- Git

### Installation

1. Clone the repository and navigate to the project directory:

2. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Set up the database:

   **Option A: Automatic Setup**
   ```bash
   python setup_database.py
   ```

   **Option B: Manual Setup**
   - Create a MySQL database named `school_activities`
   - Update `.env` file with your database credentials if needed
   - The application will automatically create tables on first run

4. Run the application:

   ```
   python src/app.py
   ```

5. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister from an activity                                         |

## Data Model

The application uses a MySQL database with the following tables:

1. **Activities** - Activity information:
   - Name (unique identifier)
   - Description
   - Category (Academic, Sports, Arts)
   - Schedule
   - Maximum number of participants allowed
   - Contact email
   - Event date and times (planned)

2. **Users** - User accounts (planned):
   - Email (unique identifier)
   - Name
   - Password (hashed)
   - Role (student/admin)

3. **Registrations** - Activity signups:
   - Links users to activities
   - Registration timestamp

All data is now stored persistently in MySQL, so it survives server restarts.
