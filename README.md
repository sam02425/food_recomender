An intelligent, AI-powered food ordering kiosk system featuring multiple specialized agent components that work together to deliver personalized recommendations and streamline the ordering process. This system demonstrates advanced machine learning concepts through a multi-agent architecture designed to continuously improve through customer feedback.
🚀 Features
🤖 Multi-Agent AI System

Face Recognition Agent: Identify returning customers and analyze mood
Health Recommender Agent: Activity-based recommendations (study, gym, work, chilling)
Weather Recommender Agent: Context-aware suggestions based on weather and time of day
Entertainer Agent: Creative, personalized dish naming using customer context
Learner Agent: Reinforcement learning system that improves over time
Record Keeper Agent: Comprehensive data management and analytics
Social Agent: Social media sharing integration
Note Taker Agent: Order management and selection tracking

🎯 Intelligent Personalization

Customer History Integration: Analyzes previous orders for personalized suggestions
Context-Fusion AI: Combines weather, activity, mood, and preferences
Dynamic Learning: Each interaction improves future recommendations
Cross-Agent Coordination: Agents collaborate for cohesive suggestions

🍽️ Advanced Menu System

Dynamic pricing with smart veggie calculations
Nutritional reasoning for health-conscious choices
Weather-responsive menu filtering
Custom dish naming with creative AI

📱 Modern User Experience

Progressive multi-step ordering interface
Real-time recommendation highlighting
Interactive feedback system for continuous learning
Mobile-responsive design with Tailwind CSS
Comprehensive error handling and loading states

🏗️ System Architecture
mermaidgraph TD
    A[React Frontend] --> B[Flask API Server]
    B --> C[Agent Orchestrator]
    C --> D[Face Recognition Agent]
    C --> E[Health Recommender]
    C --> F[Weather Agent]
    C --> G[Entertainer Agent]
    C --> H[Learner Agent]
    C --> I[Record Keeper]
    C --> J[Social Agent]
    
    H --> K[(Learning Models)]
    I --> L[(Customer Data)]
    I --> M[(Order History)]
    
    F --> N[Weather API]
    D --> O[Face Recognition API]
    G --> P[LLM Service]
Agent Responsibilities
AgentPrimary FunctionKey Technologies🔍 Face RecognitionCustomer ID & mood analysisComputer vision, facial recognition💪 Health RecommenderActivity-based nutrition suggestionsML models, nutritional data🌤️ Weather AgentWeather-context recommendationsWeather APIs, contextual AI🎭 EntertainerCreative dish namingNLP, creative AI generation🧠 LearnerContinuous improvement via feedbackReinforcement learning, weight adjustment📊 Record KeeperData management & analyticsCSV processing, customer profiling📱 Social AgentSocial media integrationAPI integration, content generation
🛠️ Technology Stack
Backend

Python 3.8+: Core backend language
Flask: RESTful API server
CSV/JSON: Data persistence layer
Requests: External API integration
Logging: Comprehensive system logging

Frontend

React 18: Modern UI framework
TypeScript: Type-safe development
Tailwind CSS: Utility-first styling
React Router: Navigation management
Context API: State management

Testing & Quality

Jest: Unit testing framework
Cypress: End-to-end testing
ESLint: Code quality enforcement
GitHub Actions: CI/CD pipeline

Development Tools

PostCSS: CSS processing
Babel: JavaScript compilation
Hot Module Replacement: Development efficiency

📦 Installation & Setup
Prerequisites

Python 3.8 or higher
Node.js 16 or higher
npm or yarn package manager

Backend Setup
bash# Clone the repository
git clone https://github.com/sam02425/food_recomender.git
cd food_recomender

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
export LLM_API_KEY="your_llm_api_key"
export WEATHER_API_KEY="your_weather_api_key"

# Initialize data directories and default data
python setup.py
Frontend Setup
bash# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Install development dependencies
npm install --dev
Environment Configuration
Create a .env file in the root directory:
env# API Configuration
LLM_API_KEY=your_openai_or_llm_api_key
LLM_API_URL=https://api.openai.com/v1/chat/completions
WEATHER_API_KEY=your_weather_api_key

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Data Paths
DATA_DIR=./data
FACE_IMAGES_DIR=./data/face_images
🚀 Running the Application
Development Mode
bash# Terminal 1: Start the Flask API server
python api_server.py
# Server runs on http://localhost:5000

# Terminal 2: Start the React development server
cd frontend
npm start
# Frontend runs on http://localhost:3000
Production Mode
bash# Build the frontend
cd frontend
npm run build

# Start the main application
python main.py
Testing
bash# Run Python tests
python -m pytest tests/

# Run frontend unit tests
cd frontend
npm test

# Run end-to-end tests
npm run cypress:run
📋 Usage Guide
Basic Ordering Flow

Customer Identification

Enter phone number for returning customers
Optional: Face recognition for mood analysis
New customers can create profiles


Activity Selection

Choose current activity: Study, Gym, Work, or Chilling
System generates health-based recommendations


Menu Selection with AI Assistance

Protein Selection: Health-based suggestions with reasoning
Base Selection: Weather-informed recommendations
Creative Naming: AI-generated personalized dish names
Sauce & Vegetables: Comprehensive selection with pricing


Feedback & Learning

Accept, ignore, or customize each recommendation
System learns from feedback for future improvements


Order Review & Social Sharing

Review complete order with pricing
Optional social media sharing
Order completion with receipt generation



Example API Usage
python# Get health recommendations
import requests

response = requests.post('http://localhost:5000/api/health-recommendations', 
    json={
        'activity_level': 'gym',
        'customer_phone': '+1234567890'
    }
)

recommendations = response.json()
print(f"Recommended proteins: {recommendations['recommendations']['proteins']}")
🧠 Machine Learning Features
Reinforcement Learning System
The Learner Agent implements a sophisticated feedback processing system:
python# Weight adjustment based on feedback
if feedback == "accept":
    model["weights"][context] *= 1.05  # Increase preference
elif feedback == "custom":
    model["weights"][context] *= 1.1   # Strong preference signal
elif feedback == "ignore":
    model["weights"][context] *= 0.98  # Decrease preference
Personalization Algorithm

Customer Profiling: Individual preference matrices
Context Integration: Weather + activity + mood + history
Dynamic Adaptation: Real-time model updates
Cross-Agent Learning: Feedback affects multiple recommendation types

Data Science Features

A/B Testing Framework: Compare recommendation strategies
Analytics Dashboard: Customer behavior insights
Preference Mining: Extract patterns from order history
Predictive Modeling: Anticipate customer preferences

🔧 API Documentation
Core Endpoints
EndpointMethodDescription/api/start-orderPOSTInitialize new order session/api/health-recommendationsPOSTGet activity-based recommendations/api/weather-recommendationsPOSTGet weather-context suggestions/api/dish-namePOSTGenerate creative dish names/api/recommendation-feedbackPOSTProcess user feedback/api/add-itemPOSTAdd item to current order/api/complete-orderPOSTFinalize order and generate receipt/api/customer-ordersGETRetrieve customer order history/api/menu-dataGETGet current menu and pricing
Request/Response Examples
json// Health Recommendations Request
{
  "activity_level": "study",
  "customer_phone": "+1234567890"
}

// Health Recommendations Response
{
  "success": true,
  "recommendations": {
    "proteins": ["Egg", "Paneer/Indian Cheese"],
    "sauces": ["Mint Sauce", "Yogurt/Raita"],
    "reasoning": "Brain-boosting nutrients for sustained mental energy",
    "personalized": true
  }
}
🧪 Testing Strategy
Unit Tests

Agent functionality testing
API endpoint validation
Data processing verification
Error handling coverage

Integration Tests

Multi-agent coordination
End-to-end order flow
Database operations
External API interactions

Performance Tests

Recommendation generation speed
Concurrent user handling
Memory usage optimization
API response times

User Experience Tests

Accessibility compliance
Mobile responsiveness
Error state handling
Loading state management

📊 Data Management
Customer Data Schema
csvcustomer_id,name,phone_number,face_id,visit_count,last_visit,created_at
CUST123,John Doe,+1234567890,FACE456,5,2023-12-01T10:30:00,2023-10-15T09:00:00
Order Data Schema
csvorder_id,customer_id,timestamp,items,total_price,weather,activity,mood
ORD789,CUST123,2023-12-01T10:30:00,"[{""protein"":""Chicken""}]",12.99,sunny,gym,happy
Learning Data Schema
json{
  "models": {
    "health": {
      "activity_weights": {"gym": 1.05, "study": 0.98},
      "feedback_count": 150,
      "acceptance_rate": 78.5
    }
  },
  "customer_preferences": {
    "CUST123": {
      "preferred_proteins": {"Chicken": 5, "Egg": 3}
    }
  }
}
🤝 Contributing
We welcome contributions! Please follow these guidelines:
Development Workflow

Fork the repository
Create a feature branch: git checkout -b feature/amazing-feature
Make your changes with tests
Run the test suite: npm test && python -m pytest
Commit changes: git commit -m 'Add amazing feature'
Push to branch: git push origin feature/amazing-feature
Submit a Pull Request

Code Standards

Python: Follow PEP 8 style guidelines
JavaScript/React: ESLint configuration enforced
Commit Messages: Use conventional commit format
Documentation: Update README for new features
Testing: Maintain >80% code coverage

Areas for Contribution

🔍 New AI Agents: Dietary restriction agent, allergy management
🌐 API Integrations: Payment processing, inventory management
📱 Mobile Features: Native mobile app, push notifications
🧠 ML Improvements: Advanced recommendation algorithms
🎨 UI/UX: Accessibility improvements, animation enhancements
📊 Analytics: Advanced reporting and insights dashboard

🚀 Deployment
Docker Deployment
dockerfile# Coming soon: Docker configuration for easy deployment
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "api_server.py"]

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- The menu system is inspired by various fast-casual restaurant concepts
- Face recognition techniques based on established computer vision research
- Weather data provided by open weather APIs
