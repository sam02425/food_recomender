# Quick Start Guide

This guide will help you get started with the Food Recommendation System quickly.

## Prerequisites

- Node.js 18+
- Python 3.9+
- PostgreSQL
- Redis
- Git

## Setup Steps

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/food_recommender.git
cd food_recommender
```

2. **Frontend Setup**
```bash
cd frontend
npm install
```

3. **Backend Setup**
```bash
cd ../backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Environment Setup**

Create `.env.local` in the frontend directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Create `.env` in the backend directory:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/food_recommender
REDIS_URL=redis://localhost:6379
```

5. **Start Development Servers**

Terminal 1 (Frontend):
```bash
cd frontend
npm run dev
```

Terminal 2 (Backend):
```bash
cd backend
uvicorn main:app --reload
```

## Basic Usage

1. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

2. **Test the Face Agent**
```typescript
const agentManager = new AgentManagerImpl('test-user');
await agentManager.initialize();

const faceAgent = agentManager.getAgent<FaceAgent>('face');
const mood = await faceAgent.analyzeMood(imageBlob);
```

3. **Get Recommendations**
```typescript
const learnerAgent = agentManager.getAgent<LearnerAgent>('learner');
const recommendations = await learnerAgent.getRecommendations();
```

## Common Tasks

### Adding a New Feature

1. Create a new agent interface in `frontend/src/agents/types.ts`
2. Implement the agent in `frontend/src/agents/`
3. Add the agent to `AgentManager`
4. Create corresponding backend endpoints
5. Add tests

### Running Tests

Frontend:
```bash
cd frontend
npm test
```

Backend:
```bash
cd backend
pytest
```

### Debugging

1. **Frontend**
   - Use React Developer Tools
   - Check browser console
   - Use Next.js debugging tools

2. **Backend**
   - Use FastAPI debug mode
   - Check server logs
   - Use Python debugger

## Useful Commands

```bash
# Frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run test         # Run tests
npm run lint         # Run linter

# Backend
uvicorn main:app --reload  # Start development server
pytest                     # Run tests
black .                    # Format code
flake8                     # Run linter
```

## Next Steps

1. Read the full [Developer Documentation](DEVELOPER.md)
2. Explore the codebase structure
3. Set up your development environment
4. Start contributing!

## Getting Help

- Check the [Developer Documentation](DEVELOPER.md)
- Review the [API Documentation](http://localhost:8000/docs)
- Open an issue on GitHub
- Contact the development team