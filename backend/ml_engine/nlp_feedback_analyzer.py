"""
NLP Feedback Analyzer for Food Recommendation System
Processes user feedback using transformer models and extracts actionable insights
"""

import logging
import numpy as np
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import joblib

# NLP Dependencies
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPFeedbackAnalyzer:
    """Advanced NLP analysis for user feedback in food recommendation context"""

    def __init__(self, model_path: str = "models/nlp_feedback.joblib"):
        self.model_path = model_path

        # Initialize sentiment analyzers
        self._initialize_sentiment_models()

        # Food-specific vocabularies
        self._initialize_food_vocabularies()

        # Aspect extraction patterns
        self._initialize_aspect_patterns()

        # Load or initialize model state
        try:
            self.load_models()
        except FileNotFoundError:
            logger.info("No existing NLP models found. Initializing new models.")
            self._initialize_default_state()

    def _initialize_sentiment_models(self):
        """Initialize various sentiment analysis models"""
        try:
            # Try to initialize transformer model, but don't fail if it doesn't work
            try:
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="distilbert-base-uncased-finetuned-sst-2-english"
                )
            except:
                # If transformer fails, use None and rely on VADER/TextBlob
                logger.info("Transformer model not available, using VADER and TextBlob")
                self.sentiment_pipeline = None

            # VADER sentiment analyzer (good for social media text)
            self.vader_analyzer = SentimentIntensityAnalyzer()

            logger.info("Sentiment analysis models initialized successfully")

        except Exception as e:
            logger.warning(f"Error initializing sentiment models: {e}")
            # Fallback to just TextBlob
            self.sentiment_pipeline = None
            try:
                self.vader_analyzer = SentimentIntensityAnalyzer()
            except:
                self.vader_analyzer = None

    def _initialize_food_vocabularies(self):
        """Initialize food-specific vocabulary for better analysis"""

        # Positive food descriptors
        self.positive_food_words = {
            'taste': ['delicious', 'tasty', 'flavorful', 'savory', 'rich', 'perfect', 'amazing', 'excellent', 'wonderful', 'fantastic'],
            'texture': ['crispy', 'tender', 'juicy', 'smooth', 'creamy', 'fresh', 'soft', 'perfect'],
            'temperature': ['hot', 'warm', 'steaming', 'fresh'],
            'portion': ['filling', 'generous', 'perfect', 'satisfying', 'enough'],
            'overall': ['love', 'favorite', 'best', 'perfect', 'amazing', 'awesome', 'great', 'good']
        }

        # Negative food descriptors
        self.negative_food_words = {
            'taste': ['bland', 'tasteless', 'salty', 'bitter', 'sour', 'awful', 'terrible', 'disgusting', 'bad'],
            'texture': ['dry', 'soggy', 'tough', 'chewy', 'mushy', 'hard', 'stale'],
            'temperature': ['cold', 'lukewarm', 'frozen', 'burnt'],
            'portion': ['small', 'tiny', 'insufficient', 'little', 'not enough'],
            'overall': ['hate', 'worst', 'terrible', 'awful', 'bad', 'disappointing', 'poor']
        }

        # Food component keywords
        self.food_components = {
            'protein': ['chicken', 'paneer', 'egg', 'tofu', 'soya', 'meat', 'protein'],
            'base': ['rice', 'naan', 'salad', 'bowl', 'wrap', 'base'],
            'sauce': ['curry', 'masala', 'raita', 'yogurt', 'spicy', 'sauce', 'gravy'],
            'vegetables': ['vegetables', 'veggies', 'greens', 'salad', 'tomato', 'onion'],
            'garnishes': ['garnish', 'toppings', 'herbs', 'coriander', 'mint']
        }

    def _initialize_aspect_patterns(self):
        """Initialize regex patterns for aspect-based sentiment analysis"""

        self.aspect_patterns = {
            'taste': [
                r'taste[s]?\s+(was|is|were)\s+(\w+)',
                r'flavor[s]?\s+(was|is|were)\s+(\w+)',
                r'(\w+)\s+taste',
                r'(\w+)\s+flavor'
            ],
            'portion': [
                r'portion[s]?\s+(was|is|were)\s+(\w+)',
                r'size[s]?\s+(was|is|were)\s+(\w+)',
                r'(\w+)\s+portion',
                r'(\w+)\s+size'
            ],
            'temperature': [
                r'temperature\s+(was|is|were)\s+(\w+)',
                r'(hot|cold|warm|lukewarm)',
                r'(\w+)\s+temperature'
            ],
            'texture': [
                r'texture\s+(was|is|were)\s+(\w+)',
                r'(crispy|soggy|tender|tough|soft|hard)',
                r'(\w+)\s+texture'
            ],
            'service': [
                r'service\s+(was|is|were)\s+(\w+)',
                r'delivery\s+(was|is|were)\s+(\w+)',
                r'(\w+)\s+service'
            ]
        }

    def _initialize_default_state(self):
        """Initialize default model state"""
        self.feedback_history = []
        self.sentiment_cache = {}
        self.aspect_trends = {}

    def analyze_feedback(self, feedback_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive analysis of user feedback"""

        if not feedback_text or not isinstance(feedback_text, str):
            return self._get_neutral_analysis()

        try:
            # Clean and preprocess text
            cleaned_text = self._preprocess_text(feedback_text)

            # Sentiment analysis using multiple methods
            sentiment_scores = self._analyze_sentiment(cleaned_text)

            # Aspect-based sentiment analysis
            aspect_sentiments = self._analyze_aspects(cleaned_text)

            # Extract food-specific insights
            food_insights = self._extract_food_insights(cleaned_text)

            # Generate preference adjustments
            preference_adjustments = self._generate_preference_adjustments(
                sentiment_scores, aspect_sentiments, food_insights, context
            )

            # Create comprehensive analysis result
            analysis = {
                'overall_sentiment': sentiment_scores,
                'aspect_sentiments': aspect_sentiments,
                'food_insights': food_insights,
                'preference_adjustments': preference_adjustments,
                'confidence': self._calculate_confidence(sentiment_scores, aspect_sentiments),
                'key_phrases': self._extract_key_phrases(cleaned_text),
                'suggestions': self._generate_suggestions(aspect_sentiments, food_insights),
                'timestamp': datetime.now().isoformat()
            }

            # Store for future learning
            self._store_analysis(feedback_text, analysis, context)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing feedback: {e}")
            return self._get_neutral_analysis()

    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess feedback text"""
        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Handle common contractions
        contractions = {
            "wasn't": "was not",
            "isn't": "is not",
            "didn't": "did not",
            "doesn't": "does not",
            "don't": "do not",
            "won't": "will not",
            "can't": "cannot",
            "couldn't": "could not",
            "shouldn't": "should not"
        }

        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)

        return text

    def _analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using multiple methods"""
        sentiments = {}

        try:
            # RoBERTa transformer model (if available)
            if self.sentiment_pipeline:
                result = self.sentiment_pipeline(text)[0]
                label = result['label'].lower()
                score = result['score']

                # Convert to standardized scale (-1 to 1)
                if 'positive' in label:
                    sentiments['roberta'] = score
                elif 'negative' in label:
                    sentiments['roberta'] = -score
                else:  # neutral
                    sentiments['roberta'] = 0.0
        except Exception as e:
            logger.warning(f"Error with RoBERTa sentiment analysis: {e}")

        # VADER sentiment
        try:
            vader_scores = self.vader_analyzer.polarity_scores(text)
            sentiments['vader'] = vader_scores['compound']
        except Exception as e:
            logger.warning(f"Error with VADER sentiment analysis: {e}")

        # TextBlob sentiment
        try:
            blob = TextBlob(text)
            sentiments['textblob'] = blob.sentiment.polarity
        except Exception as e:
            logger.warning(f"Error with TextBlob sentiment analysis: {e}")

        # Calculate weighted average
        if sentiments:
            weights = {'roberta': 0.5, 'vader': 0.3, 'textblob': 0.2}
            weighted_sentiment = sum(
                sentiments.get(method, 0) * weight
                for method, weight in weights.items()
                if method in sentiments
            ) / sum(weight for method, weight in weights.items() if method in sentiments)

            sentiments['weighted_average'] = weighted_sentiment
        else:
            sentiments['weighted_average'] = 0.0

        return sentiments

    def _analyze_aspects(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Perform aspect-based sentiment analysis"""
        aspects = {}

        for aspect, patterns in self.aspect_patterns.items():
            aspect_sentiment = self._extract_aspect_sentiment(text, aspect, patterns)
            if aspect_sentiment:
                aspects[aspect] = aspect_sentiment

        return aspects

    def _extract_aspect_sentiment(self, text: str, aspect: str, patterns: List[str]) -> Dict[str, Any]:
        """Extract sentiment for a specific aspect"""
        aspect_mentions = []

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                aspect_mentions.append(match.group())

        if not aspect_mentions:
            return None

        # Analyze sentiment of aspect mentions
        aspect_text = ' '.join(aspect_mentions)
        aspect_sentiment = self._analyze_sentiment(aspect_text)

        # Check for aspect-specific positive/negative words
        positive_count = sum(
            1 for word in self.positive_food_words.get(aspect, [])
            if word in text
        )
        negative_count = sum(
            1 for word in self.negative_food_words.get(aspect, [])
            if word in text
        )

        return {
            'sentiment_score': aspect_sentiment.get('weighted_average', 0.0),
            'mentions': aspect_mentions,
            'positive_indicators': positive_count,
            'negative_indicators': negative_count,
            'confidence': min(len(aspect_mentions) * 0.3 + 0.1, 1.0)
        }

    def _extract_food_insights(self, text: str) -> Dict[str, Any]:
        """Extract food-specific insights from feedback"""
        insights = {
            'mentioned_components': {},
            'preference_indicators': {},
            'improvement_suggestions': []
        }

        # Check which food components are mentioned
        for component, keywords in self.food_components.items():
            mentioned_keywords = [kw for kw in keywords if kw in text]
            if mentioned_keywords:
                insights['mentioned_components'][component] = mentioned_keywords

        # Extract preference indicators
        for category, pos_words in self.positive_food_words.items():
            positive_mentions = [word for word in pos_words if word in text]
            negative_mentions = [word for word in self.negative_food_words.get(category, []) if word in text]

            if positive_mentions or negative_mentions:
                insights['preference_indicators'][category] = {
                    'positive': positive_mentions,
                    'negative': negative_mentions,
                    'score': len(positive_mentions) - len(negative_mentions)
                }

        # Extract improvement suggestions
        if 'more' in text:
            more_patterns = re.findall(r'more\s+(\w+)', text)
            insights['improvement_suggestions'].extend(
                [f"increase_{item}" for item in more_patterns]
            )

        if 'less' in text:
            less_patterns = re.findall(r'less\s+(\w+)', text)
            insights['improvement_suggestions'].extend(
                [f"decrease_{item}" for item in less_patterns]
            )

        return insights

    def _generate_preference_adjustments(
        self,
        sentiment_scores: Dict[str, float],
        aspect_sentiments: Dict[str, Dict[str, Any]],
        food_insights: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, float]:
        """Generate specific preference adjustments based on analysis"""

        adjustments = {}

        # Overall sentiment adjustment
        overall_sentiment = sentiment_scores.get('weighted_average', 0.0)

        # Component-specific adjustments
        if context and 'selections' in context:
            selections = context['selections']

            # Adjust based on overall sentiment
            for component, selection in selections.items():
                base_adjustment = overall_sentiment * 0.3  # Base adjustment from overall sentiment

                # Aspect-specific adjustments
                if component in aspect_sentiments:
                    aspect_score = aspect_sentiments[component]['sentiment_score']
                    base_adjustment += aspect_score * 0.5

                # Food insight adjustments
                preference_indicators = food_insights.get('preference_indicators', {})
                if component in preference_indicators:
                    indicator_score = preference_indicators[component]['score']
                    base_adjustment += indicator_score * 0.2

                adjustments[f"{component}_{selection}"] = base_adjustment

        # Improvement-based adjustments
        for suggestion in food_insights.get('improvement_suggestions', []):
            if suggestion.startswith('increase_'):
                component = suggestion.replace('increase_', '')
                adjustments[f"increase_{component}"] = 0.3
            elif suggestion.startswith('decrease_'):
                component = suggestion.replace('decrease_', '')
                adjustments[f"decrease_{component}"] = -0.3

        return adjustments

    def _calculate_confidence(
        self,
        sentiment_scores: Dict[str, float],
        aspect_sentiments: Dict[str, Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for the analysis"""

        confidence_factors = []

        # Sentiment consensus (how similar are different sentiment methods)
        if len(sentiment_scores) > 1:
            sentiment_values = list(sentiment_scores.values())
            sentiment_std = np.std(sentiment_values)
            consensus_confidence = max(0, 1 - sentiment_std)
            confidence_factors.append(consensus_confidence)

        # Aspect coverage (more aspects = higher confidence)
        aspect_confidence = min(len(aspect_sentiments) * 0.2, 0.8)
        confidence_factors.append(aspect_confidence)

        # Base confidence from having multiple indicators
        base_confidence = 0.5
        confidence_factors.append(base_confidence)

        return np.mean(confidence_factors) if confidence_factors else 0.5

    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from feedback"""
        try:
            # Tokenize and remove stopwords
            stop_words = set(stopwords.words('english'))
            words = word_tokenize(text)
            filtered_words = [w for w in words if w.lower() not in stop_words and len(w) > 2]

            # Extract phrases around food-related keywords
            key_phrases = []

            for component_list in self.food_components.values():
                for keyword in component_list:
                    if keyword in text:
                        # Extract context around the keyword
                        pattern = rf'\b\w+\s+{keyword}\s+\w+\b|\b{keyword}\s+\w+\b|\b\w+\s+{keyword}\b'
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        key_phrases.extend(matches)

            return list(set(key_phrases))[:5]  # Return top 5 unique phrases

        except Exception as e:
            logger.warning(f"Error extracting key phrases: {e}")
            return []

    def _generate_suggestions(
        self,
        aspect_sentiments: Dict[str, Dict[str, Any]],
        food_insights: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable suggestions based on analysis"""

        suggestions = []

        # Suggestions based on negative aspects
        for aspect, sentiment_data in aspect_sentiments.items():
            if sentiment_data['sentiment_score'] < -0.3:
                if aspect == 'taste':
                    suggestions.append("Consider adjusting spice levels or sauce combinations")
                elif aspect == 'temperature':
                    suggestions.append("Ensure food is served at optimal temperature")
                elif aspect == 'portion':
                    suggestions.append("Review portion sizes for better satisfaction")
                elif aspect == 'texture':
                    suggestions.append("Focus on cooking techniques for better texture")

        # Suggestions based on improvement indicators
        improvement_suggestions = food_insights.get('improvement_suggestions', [])
        for suggestion in improvement_suggestions:
            if 'increase' in suggestion:
                component = suggestion.replace('increase_', '')
                suggestions.append(f"Consider offering more {component} options")
            elif 'decrease' in suggestion:
                component = suggestion.replace('decrease_', '')
                suggestions.append(f"Consider reducing {component} intensity")

        return suggestions[:3]  # Return top 3 suggestions

    def _get_neutral_analysis(self) -> Dict[str, Any]:
        """Return neutral analysis for error cases"""
        return {
            'overall_sentiment': {'weighted_average': 0.0},
            'aspect_sentiments': {},
            'food_insights': {
                'mentioned_components': {},
                'preference_indicators': {},
                'improvement_suggestions': []
            },
            'preference_adjustments': {},
            'confidence': 0.1,
            'key_phrases': [],
            'suggestions': [],
            'timestamp': datetime.now().isoformat()
        }

    def _store_analysis(self, feedback_text: str, analysis: Dict[str, Any], context: Dict[str, Any] = None):
        """Store analysis results for future learning"""
        self.feedback_history.append({
            'feedback_text': feedback_text,
            'analysis': analysis,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })

        # Keep only last 1000 entries to prevent memory issues
        if len(self.feedback_history) > 1000:
            self.feedback_history = self.feedback_history[-1000:]

    def get_preference_trends(self, user_id: str = None) -> Dict[str, Any]:
        """Analyze preference trends from feedback history"""
        try:
            relevant_feedback = self.feedback_history

            if user_id:
                relevant_feedback = [
                    fb for fb in self.feedback_history
                    if fb.get('context', {}).get('user_id') == user_id
                ]

            if not relevant_feedback:
                return {'trends': {}, 'insights': []}

            # Analyze trends
            trends = {}
            for aspect in ['taste', 'texture', 'temperature', 'portion']:
                aspect_scores = []
                for fb in relevant_feedback:
                    aspect_data = fb['analysis']['aspect_sentiments'].get(aspect)
                    if aspect_data:
                        aspect_scores.append(aspect_data['sentiment_score'])

                if aspect_scores:
                    trends[aspect] = {
                        'average_sentiment': np.mean(aspect_scores),
                        'trend_direction': 'improving' if len(aspect_scores) > 1 and aspect_scores[-1] > aspect_scores[0] else 'stable',
                        'sample_size': len(aspect_scores)
                    }

            return {
                'trends': trends,
                'total_feedback_analyzed': len(relevant_feedback),
                'period': 'last_30_days'
            }

        except Exception as e:
            logger.error(f"Error analyzing preference trends: {e}")
            return {'trends': {}, 'insights': []}

    def save_models(self):
        """Save NLP model state"""
        try:
            model_state = {
                'feedback_history': self.feedback_history[-100:],  # Save last 100 for context
                'sentiment_cache': getattr(self, 'sentiment_cache', {}),
                'aspect_trends': getattr(self, 'aspect_trends', {}),
                'model_version': '1.0.0',
                'last_updated': datetime.now().isoformat()
            }

            joblib.dump(model_state, self.model_path)
            logger.info(f"NLP models saved to {self.model_path}")

        except Exception as e:
            logger.error(f"Error saving NLP models: {e}")

    def load_models(self):
        """Load NLP model state"""
        try:
            model_state = joblib.load(self.model_path)

            self.feedback_history = model_state.get('feedback_history', [])
            self.sentiment_cache = model_state.get('sentiment_cache', {})
            self.aspect_trends = model_state.get('aspect_trends', {})

            logger.info(f"NLP models loaded from {self.model_path}")

        except FileNotFoundError:
            logger.info("No existing NLP model file found")
            self._initialize_default_state()
        except Exception as e:
            logger.error(f"Error loading NLP models: {e}")
            self._initialize_default_state()
