# /README.md
# 🍛 Agents Protin: AI-Powered Food Ordering System

Agents Protin is an intelligent, AI-powered food ordering kiosk system featuring multiple specialized agent components that work together to deliver personalized recommendations and streamline the ordering process.

## 🚀 Features

- **Face Recognition**: Identify returning customers and analyze mood
- **Health Recommendations**: Based on activity level (study, active/gym, work, chilling)
- **Weather Recommendations**: Tailored to current weather and time of day
- **Entertaining Dish Names**: Generate personalized, creative dish names
- **Social Sharing**: Let customers share their creations on social media
- **Reinforcement Learning**: System improves over time based on feedback
- **Customer Data Management**: Track preferences for better recommendations
- **Interactive UI**: Highlight recommendations for easy selection

## 📋 System Overview

The system uses a multi-agent architecture with specialized components:

1. **Face Recognition Agent**: Identifies customers and analyzes their mood
2. **Note Taker Agent**: Manages order selections (proteins, sauces, bases, veggies)
3. **Health Recommender Agent**: Suggests items based on activity level
4. **Weather Recommender Agent**: Suggests items based on weather and time of day
5. **Entertainer Agent**: Creates personalized dish names
6. **Learner Agent**: Improves recommendations through reinforcement learning
7. **Record Keeper Agent**: Stores and retrieves customer data and preferences
8. **Social Agent**: Facilitates sharing on social media platforms

## 🌮 Menu Options

### Proteins
- Chicken
- Egg
- Paneer/Indian Cheese
- Soya
- Potato
- Pepperoni

### Sauces
- Curry Special
- Malai Masala
- Curry Masala
- Marinara
- Yogurt/Raita
- Red Spicy Sauce
- Mint Sauce
- Green Spicy Sauce

### Bases
- **Biryani**: Rice
- **Sandwich & Subs**: Sourdough, Ciabatta, White Bread, Hoagie Bun
- **Wrap**: Naan, Pita

### Veggies
- Grilled Onion
- Bell Pepper
- Tomato
- Cilantro
- Avocado ($3)
- Pineapple
- Spinach
- Jalapeño
- Banana Pepper
- Fried Onions
- Corn
- Cabbage
- Ghee
- Mango Chutney

*Note: First 5 veggies are included, each additional veggie costs $1, Avocado costs $3*

## 🔧 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agents-protin.git
   cd agents-protin
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up data directories:
   ```bash
   mkdir -p data/face_images data/social_media data/receipts
   ```

4. Run the application:
   ```bash
   python main.py
   ```

## 📁 Project Structure

```
agents-protin/
│
├── main.py                   # Main application entry point
├── config.yaml               # Configuration settings
├── requirements.txt          # Dependencies
│
├── agents/                   # Agent components
│   ├── face_recognition_agent.py
│   ├── note_taker_agent.py
│   ├── health_recommender_agent.py
│   ├── weather_recommender_agent.py
│   ├── entertainer_agent.py
│   ├── learner_agent.py
│   ├── record_keeper_agent.py
│   └── social_agent.py
│
├── ui/                       # User interface components
│   ├── kiosk_app.py
│   └── streamlit_components/
│
├── components/               # Reusable UI components
│   └── recommendation_highlight.py
│
├── data/                     # Data storage
│   ├── customers.csv
│   ├── orders.csv
│   ├── feedback.csv
│   ├── menu_items.csv
│   ├── social_data.json
│   ├── face_images/
│   ├── social_media/
│   └── receipts/
│
└── tests/                    # Unit and integration tests
    ├── test_face_recognition_agent.py
    ├── test_health_recommender_agent.py
    ├── test_social_agent.py
    └── ...
```

## 🧠 Recommendation System

The system provides three types of personalized recommendations:

1. **Health-Based**: Based on activity level (study, active/gym, work, chilling)
2. **Weather-Based**: Tailored to current weather and time of day
3. **Personalized**: Based on customer order history and preferences

Recommendations are displayed with highlighted options for easy selection:
- Recommended options are highlighted in green
- Selected options are highlighted in blue
- Other options appear slightly dimmed

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
