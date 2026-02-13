# 🚀 Quick Start Guide

Get CollabHub up and running in minutes!

## Prerequisites

- Node.js 20+ installed
- PostgreSQL 15+ installed and running
- npm or yarn package manager

## Step 1: Database Setup

1. Create a PostgreSQL database:
```sql
CREATE DATABASE collabhub;
```

2. Note your database connection details (you'll need them for the `.env` file)

## Step 2: Backend Setup

1. Navigate to backend directory:
```bash
cd collabhub/backend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
# Copy the example (or create manually)
# Update with your database credentials
DATABASE_URL="postgresql://username:password@localhost:5432/collabhub?schema=public"
JWT_SECRET="your-super-secret-jwt-key-change-in-production"
JWT_EXPIRES_IN="7d"
PORT=5000
NODE_ENV=development
CORS_ORIGIN="http://localhost:5173"
UPLOAD_DIR="./uploads"
```

4. Set up database:
```bash
# Generate Prisma Client
npx prisma generate

# Run migrations
npx prisma migrate dev --name init
```

5. Start backend server:
```bash
npm run dev
```

Backend should now be running on http://localhost:5000 ✅

## Step 3: Frontend Setup

1. Open a new terminal and navigate to frontend directory:
```bash
cd collabhub/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend should now be running on http://localhost:5173 ✅

## Step 4: Test the Application

1. Open http://localhost:5173 in your browser
2. Click "Create a new account" to register
3. Create your first project
4. Add tasks and start collaborating!

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running: `pg_isready` or check your PostgreSQL service
- Verify DATABASE_URL in `.env` matches your PostgreSQL credentials
- Check if the database `collabhub` exists

### Port Already in Use
- Backend: Change `PORT` in backend `.env` file
- Frontend: Modify `vite.config.ts` server port

### Prisma Migration Issues
- Reset database: `npx prisma migrate reset` (⚠️ deletes all data)
- Check Prisma schema syntax: `npx prisma validate`

### Module Not Found Errors
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

## Next Steps

- Read the full [README.md](./README.md) for detailed documentation
- Explore the API endpoints using the backend health check: http://localhost:5000/health
- Check out Prisma Studio: `cd backend && npx prisma studio`

Happy coding! 🎉
