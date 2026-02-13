# 🚀 CollabHub - Team Collaboration Platform

A full-stack TypeScript and Node.js application for team collaboration, featuring real-time updates, project management, task tracking, and more.

## ✨ Features

- **User Authentication** - Secure JWT-based authentication with password hashing
- **Project Management** - Create and manage team projects with customizable colors
- **Task Tracking** - Kanban-style task board with status tracking (Todo, In Progress, Review, Done)
- **Real-time Updates** - WebSocket support for live collaboration
- **Comments & Discussions** - Add comments to tasks for team communication
- **Role-based Access** - Project owners, admins, and members with different permissions
- **Modern UI** - Beautiful, responsive interface built with React and Tailwind CSS
- **Type-safe** - Full TypeScript implementation across frontend and backend

## 🛠 Tech Stack

### Backend
- **Node.js** + **Express** - RESTful API server
- **TypeScript** - Type-safe development
- **PostgreSQL** - Relational database
- **Prisma** - Modern ORM for database management
- **Socket.IO** - Real-time WebSocket communication
- **JWT** - Secure authentication tokens
- **bcryptjs** - Password hashing
- **Zod** - Schema validation

### Frontend
- **React 18** - Modern UI library
- **TypeScript** - Type-safe frontend code
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **Zustand** - State management
- **React Hook Form** - Form handling
- **Tailwind CSS** - Utility-first CSS framework
- **Socket.IO Client** - Real-time updates
- **Axios** - HTTP client
- **Lucide React** - Beautiful icons

## 📋 Prerequisites

- Node.js 20+ and npm
- PostgreSQL 15+
- Docker and Docker Compose (optional, for containerized setup)

## 🚀 Getting Started

### Option 1: Docker Compose (Recommended)

1. Clone the repository:
```bash
cd collabhub
```

2. Start all services:
```bash
docker-compose up -d
```

3. The application will be available at:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000
   - Database: localhost:5432

### Option 2: Manual Setup

#### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (copy from `.env.example`):
```bash
DATABASE_URL="postgresql://user:password@localhost:5432/collabhub?schema=public"
JWT_SECRET="your-super-secret-jwt-key-change-in-production"
JWT_EXPIRES_IN="7d"
PORT=5000
NODE_ENV=development
CORS_ORIGIN="http://localhost:5173"
UPLOAD_DIR="./uploads"
```

4. Set up the database:
```bash
# Generate Prisma Client
npx prisma generate

# Run migrations
npx prisma migrate dev

# (Optional) Open Prisma Studio to view database
npx prisma studio
```

5. Start the backend server:
```bash
npm run dev
```

The backend will run on http://localhost:5000

#### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will run on http://localhost:5173

## 📁 Project Structure

```
collabhub/
├── backend/
│   ├── src/
│   │   ├── config/          # Database configuration
│   │   ├── middleware/      # Express middleware (auth, error handling)
│   │   ├── routes/          # API route handlers
│   │   ├── socket/          # WebSocket setup
│   │   ├── utils/           # Utility functions (JWT, validation)
│   │   └── index.ts         # Entry point
│   ├── prisma/
│   │   └── schema.prisma    # Database schema
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API and Socket services
│   │   ├── store/          # Zustand state management
│   │   ├── App.tsx         # Main app component
│   │   └── main.tsx        # Entry point
│   └── package.json
└── docker-compose.yml
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Users
- `GET /api/users/me` - Get current user
- `GET /api/users/:id` - Get user by ID

### Projects
- `GET /api/projects` - Get all user's projects
- `GET /api/projects/:id` - Get project details
- `POST /api/projects` - Create new project
- `PUT /api/projects/:id` - Update project
- `DELETE /api/projects/:id` - Delete project
- `POST /api/projects/:id/members` - Add member to project
- `DELETE /api/projects/:id/members/:memberId` - Remove member

### Tasks
- `GET /api/tasks` - Get tasks (with filters)
- `GET /api/tasks/:id` - Get task details
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task

### Comments
- `POST /api/comments` - Add comment to task
- `PUT /api/comments/:id` - Update comment
- `DELETE /api/comments/:id` - Delete comment

### Notifications
- `GET /api/notifications` - Get user notifications
- `PUT /api/notifications/:id/read` - Mark notification as read
- `PUT /api/notifications/read-all` - Mark all as read

## 🧪 Development

### Backend Scripts
```bash
npm run dev      # Start development server with hot reload
npm run build    # Build for production
npm start        # Start production server
npm run db:generate  # Generate Prisma Client
npm run db:migrate   # Run database migrations
npm run db:studio    # Open Prisma Studio
```

### Frontend Scripts
```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild containers
docker-compose up -d --build

# Access database
docker-compose exec postgres psql -U collabhub -d collabhub
```

## 🔒 Environment Variables

### Backend (.env)
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Secret key for JWT tokens
- `JWT_EXPIRES_IN` - Token expiration time
- `PORT` - Server port (default: 5000)
- `NODE_ENV` - Environment (development/production)
- `CORS_ORIGIN` - Allowed CORS origin
- `UPLOAD_DIR` - Directory for file uploads

## 📝 Database Schema

The application uses Prisma ORM with PostgreSQL. Key models include:
- **User** - User accounts
- **Project** - Team projects
- **ProjectMember** - Project membership with roles
- **Task** - Project tasks
- **Comment** - Task comments
- **TaskAttachment** - File attachments
- **Notification** - User notifications

## 🎯 Future Enhancements

- [ ] File upload functionality
- [ ] Advanced search and filtering
- [ ] Email notifications
- [ ] Activity feed
- [ ] Project templates
- [ ] Time tracking
- [ ] Analytics dashboard
- [ ] Mobile app

## 📄 License

MIT License - feel free to use this project for your portfolio!

## 🤝 Contributing

This is a portfolio project, but suggestions and improvements are welcome!

---

Built with ❤️ using TypeScript, Node.js, React, and modern web technologies.
