# Developer Documentation

## Architecture Overview

The Food Recommendation System uses a multi-agent architecture where each agent is responsible for a specific aspect of the recommendation process. The system is built using a modern tech stack with Next.js frontend and FastAPI backend.

### System Components

1. **Frontend (Next.js + TypeScript)**
   - React components for UI
   - Agent implementations in TypeScript
   - Context providers for state management
   - Material-UI for styling

2. **Backend (FastAPI + Python)**
   - RESTful API endpoints
   - Database models and migrations
   - Agent business logic
   - Integration with external services

## Agent System

### Agent Types

1. **Face Agent**
   - Purpose: Analyzes user's facial expressions
   - Key Features:
     - Real-time mood analysis
     - Emotion history tracking
   - API Endpoints:
     - `/api/face/analyze`
     - `/api/face/history`

2. **Health Agent**
   - Purpose: Tracks user's health metrics
   - Key Features:
     - Heart rate monitoring
     - Stress level tracking
     - Sleep quality assessment
   - API Endpoints:
     - `/api/health/metrics`
     - `/api/health/update`

3. **Weather Agent**
   - Purpose: Monitors weather conditions
   - Key Features:
     - Current weather data
     - Weather history
     - Location-based updates
   - API Endpoints:
     - `/api/weather/current`
     - `/api/weather/history`

4. **Learner Agent**
   - Purpose: Manages user preferences and recommendations
   - Key Features:
     - Preference learning
     - Recommendation generation
     - Feedback processing
   - API Endpoints:
     - `/api/learner/preferences`
     - `/api/learner/recommendations`
     - `/api/learner/feedback`

5. **Record Agent**
   - Purpose: Tracks user interactions and orders
   - Key Features:
     - Order history
     - User interaction logs
     - Analytics data
   - API Endpoints:
     - `/api/record/order`
     - `/api/record/history`

6. **Entertainer Agent**
   - Purpose: Manages gamification elements
   - Key Features:
     - Achievement tracking
     - Points system
     - Level progression
   - API Endpoints:
     - `/api/game/state`
     - `/api/game/update`

### Agent Manager

The `AgentManager` class is responsible for:
- Initializing all agents
- Managing agent lifecycle
- Providing access to specific agents
- Handling agent cleanup

```typescript
// Example usage
const agentManager = new AgentManagerImpl(userId);
await agentManager.initialize();

// Get specific agent
const faceAgent = agentManager.getAgent<FaceAgent>('face');
const mood = await faceAgent.analyzeMood(imageBlob);
```

## Implementation Guidelines

### Adding a New Agent

1. **Define Interface**
```typescript
// frontend/src/agents/types.ts
export interface NewAgent extends BaseAgent {
  // Define agent-specific methods
  newMethod(): Promise<Result>;
}
```

2. **Implement Agent**
```typescript
// frontend/src/agents/newAgent.ts
class NewAgentImpl implements NewAgent {
  // Implement interface methods
}
```

3. **Add to AgentManager**
```typescript
// frontend/src/agents/agentManager.ts
this.agents.set('new', new NewAgentImpl(this.userId));
```

### Error Handling

All agents should:
- Use try-catch blocks for error handling
- Log errors appropriately
- Throw meaningful error messages
- Handle API failures gracefully

### Testing

1. **Unit Tests**
```typescript
// frontend/src/agents/__tests__/newAgent.test.ts
describe('NewAgent', () => {
  it('should handle specific scenario', async () => {
    // Test implementation
  });
});
```

2. **Integration Tests**
```typescript
// frontend/src/agents/__tests__/agentManager.test.ts
describe('AgentManager', () => {
  it('should initialize all agents', async () => {
    // Test implementation
  });
});
```

## State Management

### Experiment Context

The `ExperimentContext` manages:
- User session data
- Experiment state
- Agent interactions
- Data collection

```typescript
// Example usage
const { experimentData, addMoodData } = useExperiment();
addMoodData('happy', 'pre-order');
```

## API Integration

### Backend Communication

All agents communicate with the backend using:
- RESTful API endpoints
- JSON for data exchange
- FormData for file uploads
- Error handling middleware

### Authentication

- JWT-based authentication
- User-specific endpoints
- Secure API communication

## Performance Considerations

1. **Caching**
   - Use Redis for caching
   - Implement client-side caching
   - Cache expensive computations

2. **Optimization**
   - Lazy load components
   - Optimize image processing
   - Use WebWorkers for heavy computations

## Security Guidelines

1. **Data Protection**
   - Encrypt sensitive data
   - Secure API endpoints
   - Validate user input

2. **Best Practices**
   - Use environment variables
   - Implement rate limiting
   - Follow OWASP guidelines

## Deployment

### Frontend
```bash
npm run build
npm run start
```

### Backend
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Monitoring and Logging

1. **Frontend**
   - Error tracking
   - Performance monitoring
   - User analytics

2. **Backend**
   - Request logging
   - Error tracking
   - Performance metrics

## Troubleshooting

Common issues and solutions:
1. Agent initialization failures
2. API communication errors
3. Performance bottlenecks
4. State management issues

## Future Improvements

1. **Planned Features**
   - Machine learning integration
   - Advanced analytics
   - Mobile app support

2. **Technical Debt**
   - Code refactoring
   - Performance optimization
   - Documentation updates