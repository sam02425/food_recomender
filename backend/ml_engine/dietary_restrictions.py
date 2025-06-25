"""
Dietary Restrictions and Allergy Management System
Handles dietary preferences, restrictions, and allergen tracking for food recommendations
"""

import logging
from typing import Dict, List, Set, Any, Optional
from datetime import datetime
import json
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DietaryRestrictionsManager:
    """Manages dietary restrictions, allergies, and food preferences"""
    
    def __init__(self, model_path: str = "models/dietary_restrictions.joblib"):
        self.model_path = model_path
        
        # Dietary restriction categories
        self.dietary_restrictions = {
            'vegan': {
                'name': 'Vegan',
                'description': 'No animal products',
                'excluded_ingredients': [
                    'chicken', 'egg', 'paneer', 'cheese', 'milk', 'cream', 'butter', 
                    'yogurt', 'ghee', 'honey', 'pepperoni', 'beef', 'pork', 'fish'
                ],
                'excluded_proteins': ['Chicken', 'Egg', 'Paneer/Indian Cheese', 'Pepperoni'],
                'allowed_proteins': ['Soya', 'Potato'],
                'excluded_sauces': ['Malai Masala', 'Yogurt/Raita'],
                'allowed_sauces': ['Curry Special', 'Curry Masala', 'Red Spicy Sauce', 'Mint Sauce', 'Green Spicy Sauce']
            },
            'vegetarian': {
                'name': 'Vegetarian',
                'description': 'No meat, fish, or poultry',
                'excluded_ingredients': [
                    'chicken', 'beef', 'pork', 'fish', 'pepperoni', 'meat'
                ],
                'excluded_proteins': ['Chicken', 'Pepperoni'],
                'allowed_proteins': ['Egg', 'Paneer/Indian Cheese', 'Soya', 'Potato'],
                'excluded_sauces': [],
                'allowed_sauces': ['Curry Special', 'Malai Masala', 'Curry Masala', 'Marinara', 'Yogurt/Raita', 'Red Spicy Sauce', 'Mint Sauce', 'Green Spicy Sauce']
            },
            'halal': {
                'name': 'Halal',
                'description': 'Islamic dietary laws',
                'excluded_ingredients': ['pork', 'alcohol', 'gelatin', 'non-halal meat'],
                'excluded_proteins': ['Pepperoni'],  # Assuming pepperoni contains pork
                'allowed_proteins': ['Chicken', 'Egg', 'Paneer/Indian Cheese', 'Soya', 'Potato'],
                'excluded_sauces': [],
                'allowed_sauces': ['Curry Special', 'Malai Masala', 'Curry Masala', 'Marinara', 'Yogurt/Raita', 'Red Spicy Sauce', 'Mint Sauce', 'Green Spicy Sauce']
            },
            'no_beef': {
                'name': 'No Beef',
                'description': 'No beef products',
                'excluded_ingredients': ['beef', 'beef stock', 'beef gelatin'],
                'excluded_proteins': [],  # None of our current proteins are beef
                'allowed_proteins': ['Chicken', 'Egg', 'Paneer/Indian Cheese', 'Soya', 'Potato', 'Pepperoni'],
                'excluded_sauces': [],
                'allowed_sauces': ['Curry Special', 'Malai Masala', 'Curry Masala', 'Marinara', 'Yogurt/Raita', 'Red Spicy Sauce', 'Mint Sauce', 'Green Spicy Sauce']
            },
            'no_pork': {
                'name': 'No Pork',
                'description': 'No pork products',
                'excluded_ingredients': ['pork', 'bacon', 'ham', 'pepperoni', 'pork gelatin'],
                'excluded_proteins': ['Pepperoni'],
                'allowed_proteins': ['Chicken', 'Egg', 'Paneer/Indian Cheese', 'Soya', 'Potato'],
                'excluded_sauces': [],
                'allowed_sauces': ['Curry Special', 'Malai Masala', 'Curry Masala', 'Marinara', 'Yogurt/Raita', 'Red Spicy Sauce', 'Mint Sauce', 'Green Spicy Sauce']
            }
        }
        
        # Common allergens and their ingredient mappings
        self.allergens = {
            'dairy': {
                'name': 'Dairy',
                'ingredients': ['milk', 'cheese', 'paneer', 'cream', 'butter', 'yogurt', 'ghee', 'whey', 'casein']
            },
            'eggs': {
                'name': 'Eggs',
                'ingredients': ['egg', 'eggs', 'egg white', 'egg yolk', 'mayonnaise']
            },
            'nuts': {
                'name': 'Tree Nuts',
                'ingredients': ['almonds', 'cashew', 'walnuts', 'pistachios', 'pecans', 'hazelnuts']
            },
            'peanuts': {
                'name': 'Peanuts',
                'ingredients': ['peanuts', 'peanut oil', 'peanut butter']
            },
            'soy': {
                'name': 'Soy',
                'ingredients': ['soy', 'soya', 'tofu', 'soy sauce', 'soybean']
            },
            'gluten': {
                'name': 'Gluten',
                'ingredients': ['wheat', 'barley', 'rye', 'naan', 'bread', 'flour']
            },
            'shellfish': {
                'name': 'Shellfish',
                'ingredients': ['shrimp', 'lobster', 'crab', 'prawns']
            },
            'fish': {
                'name': 'Fish',
                'ingredients': ['fish', 'salmon', 'tuna', 'cod']
            },
            'sesame': {
                'name': 'Sesame',
                'ingredients': ['sesame', 'tahini', 'sesame oil']
            }
        }
        
        # Ingredient database for all menu items
        self.ingredient_database = {
            # Proteins
            'Chicken': ['chicken', 'spices', 'oil'],
            'Egg': ['egg', 'spices'],
            'Paneer/Indian Cheese': ['paneer', 'milk', 'spices'],
            'Soya': ['soya', 'spices', 'oil'],
            'Potato': ['potato', 'spices', 'oil'],
            'Pepperoni': ['pork', 'beef', 'spices', 'sodium nitrate'],
            
            # Sauces
            'Curry Special': ['tomatoes', 'onions', 'garlic', 'ginger', 'spices', 'oil'],
            'Malai Masala': ['cream', 'cashew', 'tomatoes', 'spices', 'butter'],
            'Curry Masala': ['tomatoes', 'onions', 'spices', 'oil'],
            'Marinara': ['tomatoes', 'basil', 'garlic', 'oil'],
            'Yogurt/Raita': ['yogurt', 'cucumber', 'mint', 'spices'],
            'Red Spicy Sauce': ['chili', 'tomatoes', 'spices', 'oil'],
            'Mint Sauce': ['mint', 'yogurt', 'spices'],
            'Green Spicy Sauce': ['cilantro', 'chili', 'spices', 'oil'],
            
            # Bases
            'Rice': ['basmati rice'],
            'Naan': ['wheat flour', 'yogurt', 'oil', 'yeast'],
            'Pita': ['wheat flour', 'oil', 'yeast'],
            'Sourdough': ['wheat flour', 'sourdough starter'],
            'Ciabatta': ['wheat flour', 'oil', 'yeast'],
            'White Bread': ['wheat flour', 'milk', 'oil', 'yeast'],
            'Hoagie Bun': ['wheat flour', 'oil', 'yeast'],
            'Bowl': [],  # No additional ingredients for bowl
        }
        
        # User dietary profiles
        self.user_profiles = {}
        
        # Load existing data
        try:
            self.load_profiles()
        except FileNotFoundError:
            logger.info("No existing dietary profiles found. Starting fresh.")
    
    def set_user_dietary_restrictions(self, user_id: str, restrictions: List[str]) -> Dict[str, Any]:
        """Set dietary restrictions for a user"""
        try:
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {
                    'dietary_restrictions': [],
                    'allergens': [],
                    'custom_restrictions': [],
                    'last_updated': None
                }
            
            # Validate restrictions
            valid_restrictions = [r for r in restrictions if r in self.dietary_restrictions]
            invalid_restrictions = [r for r in restrictions if r not in self.dietary_restrictions]
            
            self.user_profiles[user_id]['dietary_restrictions'] = valid_restrictions
            self.user_profiles[user_id]['last_updated'] = datetime.now().isoformat()
            
            # Save updated profiles
            self.save_profiles()
            
            result = {
                'success': True,
                'user_id': user_id,
                'restrictions_set': valid_restrictions,
                'invalid_restrictions': invalid_restrictions,
                'summary': self._generate_restriction_summary(user_id)
            }
            
            if invalid_restrictions:
                result['warning'] = f"Unknown restrictions ignored: {invalid_restrictions}"
            
            logger.info(f"Set dietary restrictions for user {user_id}: {valid_restrictions}")
            return result
            
        except Exception as e:
            logger.error(f"Error setting dietary restrictions: {e}")
            return {'success': False, 'error': str(e)}
    
    def set_user_allergens(self, user_id: str, allergens: List[str]) -> Dict[str, Any]:
        """Set allergen information for a user"""
        try:
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {
                    'dietary_restrictions': [],
                    'allergens': [],
                    'custom_restrictions': [],
                    'last_updated': None
                }
            
            # Validate allergens
            valid_allergens = [a for a in allergens if a in self.allergens]
            invalid_allergens = [a for a in allergens if a not in self.allergens]
            
            self.user_profiles[user_id]['allergens'] = valid_allergens
            self.user_profiles[user_id]['last_updated'] = datetime.now().isoformat()
            
            # Save updated profiles
            self.save_profiles()
            
            result = {
                'success': True,
                'user_id': user_id,
                'allergens_set': valid_allergens,
                'invalid_allergens': invalid_allergens,
                'affected_ingredients': self._get_affected_ingredients(allergens=valid_allergens)
            }
            
            if invalid_allergens:
                result['warning'] = f"Unknown allergens ignored: {invalid_allergens}"
            
            logger.info(f"Set allergens for user {user_id}: {valid_allergens}")
            return result
            
        except Exception as e:
            logger.error(f"Error setting allergens: {e}")
            return {'success': False, 'error': str(e)}
    
    def filter_recommendations(self, user_id: str, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter recommendations based on user's dietary restrictions and allergens"""
        try:
            if user_id not in self.user_profiles:
                return recommendations  # No restrictions, return all
            
            profile = self.user_profiles[user_id]
            restrictions = profile.get('dietary_restrictions', [])
            allergens = profile.get('allergens', [])
            
            if not restrictions and not allergens:
                return recommendations  # No restrictions, return all
            
            filtered_recommendations = []
            
            for rec in recommendations:
                is_safe = True
                safety_issues = []
                
                # Check dietary restrictions
                for restriction in restrictions:
                    if not self._check_dietary_compliance(rec, restriction):
                        is_safe = False
                        safety_issues.append(f"Violates {self.dietary_restrictions[restriction]['name']} diet")
                
                # Check allergens
                for allergen in allergens:
                    if self._contains_allergen(rec, allergen):
                        is_safe = False
                        safety_issues.append(f"Contains {self.allergens[allergen]['name']}")
                
                if is_safe:
                    # Add safety confirmation
                    rec['dietary_safe'] = True
                    rec['dietary_compliance'] = {
                        'restrictions_met': restrictions,
                        'allergens_avoided': allergens
                    }
                    filtered_recommendations.append(rec)
                else:
                    logger.info(f"Filtered out recommendation for {user_id}: {safety_issues}")
            
            logger.info(f"Filtered {len(recommendations)} to {len(filtered_recommendations)} recommendations for user {user_id}")
            return filtered_recommendations
            
        except Exception as e:
            logger.error(f"Error filtering recommendations: {e}")
            return recommendations  # Return original on error
    
    def _check_dietary_compliance(self, recommendation: Dict[str, Any], restriction: str) -> bool:
        """Check if a recommendation complies with a dietary restriction"""
        if restriction not in self.dietary_restrictions:
            return True
        
        restriction_info = self.dietary_restrictions[restriction]
        
        # Check protein compliance
        protein = recommendation.get('protein')
        if protein and protein in restriction_info['excluded_proteins']:
            return False
        
        # Check sauce compliance
        sauce = recommendation.get('sauce')
        if sauce and sauce in restriction_info['excluded_sauces']:
            return False
        
        return True
    
    def _contains_allergen(self, recommendation: Dict[str, Any], allergen: str) -> bool:
        """Check if a recommendation contains a specific allergen"""
        if allergen not in self.allergens:
            return False
        
        allergen_ingredients = self.allergens[allergen]['ingredients']
        
        # Check all components of the recommendation
        components = [
            recommendation.get('protein'),
            recommendation.get('sauce'),
            recommendation.get('base')
        ]
        
        # Check ingredients in each component
        for component in components:
            if component:
                component_ingredients = self.ingredient_database.get(component, [])
                for ingredient in component_ingredients:
                    if ingredient.lower() in [ai.lower() for ai in allergen_ingredients]:
                        return True
        
        return False
    
    def get_safe_options(self, user_id: str, category: str) -> Dict[str, Any]:
        """Get safe options for a specific category (protein, sauce, etc.)"""
        try:
            if user_id not in self.user_profiles:
                return self._get_all_options(category)
            
            profile = self.user_profiles[user_id]
            restrictions = profile.get('dietary_restrictions', [])
            allergens = profile.get('allergens', [])
            
            safe_options = []
            excluded_options = []
            
            all_options = self._get_all_options(category)
            
            for option in all_options['options']:
                is_safe = True
                reasons = []
                
                # Check dietary restrictions
                for restriction in restrictions:
                    if not self._is_option_safe_for_restriction(option['name'], category, restriction):
                        is_safe = False
                        reasons.append(f"{self.dietary_restrictions[restriction]['name']}")
                
                # Check allergens
                for allergen in allergens:
                    if self._option_contains_allergen(option['name'], allergen):
                        is_safe = False
                        reasons.append(f"Contains {self.allergens[allergen]['name']}")
                
                if is_safe:
                    safe_options.append(option)
                else:
                    excluded_options.append({
                        'option': option,
                        'exclusion_reasons': reasons
                    })
            
            return {
                'category': category,
                'safe_options': safe_options,
                'excluded_options': excluded_options,
                'total_available': len(safe_options),
                'total_excluded': len(excluded_options)
            }
            
        except Exception as e:
            logger.error(f"Error getting safe options: {e}")
            return self._get_all_options(category)
    
    def _get_all_options(self, category: str) -> Dict[str, Any]:
        """Get all available options for a category"""
        options_map = {
            'protein': [
                {'name': 'Chicken', 'price': 4.50, 'description': 'Grilled chicken pieces'},
                {'name': 'Egg', 'price': 3.00, 'description': 'Boiled or fried egg'},
                {'name': 'Paneer/Indian Cheese', 'price': 4.00, 'description': 'Fresh Indian cheese cubes'},
                {'name': 'Soya', 'price': 3.50, 'description': 'Marinated soya chunks'},
                {'name': 'Potato', 'price': 2.50, 'description': 'Spiced potato cubes'},
                {'name': 'Pepperoni', 'price': 4.50, 'description': 'Sliced pepperoni'}
            ],
            'sauce': [
                {'name': 'Curry Special', 'description': 'Our signature curry sauce'},
                {'name': 'Malai Masala', 'description': 'Creamy, mild sauce'},
                {'name': 'Curry Masala', 'description': 'Traditional Indian curry sauce'},
                {'name': 'Marinara', 'description': 'Classic tomato sauce'},
                {'name': 'Yogurt/Raita', 'description': 'Cooling yogurt sauce'},
                {'name': 'Red Spicy Sauce', 'description': 'Hot and spicy sauce'},
                {'name': 'Mint Sauce', 'description': 'Fresh mint sauce'},
                {'name': 'Green Spicy Sauce', 'description': 'Herb-based spicy sauce'}
            ]
        }
        
        return {
            'category': category,
            'options': options_map.get(category, []),
            'total_available': len(options_map.get(category, []))
        }
    
    def _is_option_safe_for_restriction(self, option_name: str, category: str, restriction: str) -> bool:
        """Check if a specific option is safe for a dietary restriction"""
        if restriction not in self.dietary_restrictions:
            return True
        
        restriction_info = self.dietary_restrictions[restriction]
        
        if category == 'protein':
            return option_name not in restriction_info['excluded_proteins']
        elif category == 'sauce':
            return option_name not in restriction_info['excluded_sauces']
        else:
            # Check ingredients
            ingredients = self.ingredient_database.get(option_name, [])
            for ingredient in ingredients:
                if ingredient in restriction_info['excluded_ingredients']:
                    return False
            return True
    
    def _option_contains_allergen(self, option_name: str, allergen: str) -> bool:
        """Check if an option contains a specific allergen"""
        if allergen not in self.allergens:
            return False
        
        allergen_ingredients = self.allergens[allergen]['ingredients']
        option_ingredients = self.ingredient_database.get(option_name, [])
        
        for ingredient in option_ingredients:
            if ingredient.lower() in [ai.lower() for ai in allergen_ingredients]:
                return True
        
        return False
    
    def _generate_restriction_summary(self, user_id: str) -> Dict[str, Any]:
        """Generate a summary of user's dietary restrictions"""
        if user_id not in self.user_profiles:
            return {}
        
        profile = self.user_profiles[user_id]
        restrictions = profile.get('dietary_restrictions', [])
        allergens = profile.get('allergens', [])
        
        return {
            'dietary_restrictions': [
                {
                    'type': r,
                    'name': self.dietary_restrictions[r]['name'],
                    'description': self.dietary_restrictions[r]['description']
                } for r in restrictions
            ],
            'allergens': [
                {
                    'type': a,
                    'name': self.allergens[a]['name']
                } for a in allergens
            ],
            'total_restrictions': len(restrictions) + len(allergens)
        }
    
    def _get_affected_ingredients(self, restrictions: List[str] = None, allergens: List[str] = None) -> List[str]:
        """Get list of all affected ingredients"""
        affected = set()
        
        if restrictions:
            for restriction in restrictions:
                if restriction in self.dietary_restrictions:
                    affected.update(self.dietary_restrictions[restriction]['excluded_ingredients'])
        
        if allergens:
            for allergen in allergens:
                if allergen in self.allergens:
                    affected.update(self.allergens[allergen]['ingredients'])
        
        return list(affected)
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get complete dietary profile for a user"""
        if user_id not in self.user_profiles:
            return {
                'user_id': user_id,
                'dietary_restrictions': [],
                'allergens': [],
                'custom_restrictions': [],
                'last_updated': None,
                'has_restrictions': False
            }
        
        profile = self.user_profiles[user_id].copy()
        profile['user_id'] = user_id
        profile['has_restrictions'] = bool(profile.get('dietary_restrictions') or profile.get('allergens'))
        profile['summary'] = self._generate_restriction_summary(user_id)
        
        return profile
    
    def get_ingredient_info(self, item_name: str) -> Dict[str, Any]:
        """Get detailed ingredient information for a menu item"""
        ingredients = self.ingredient_database.get(item_name, [])
        
        # Find potential allergens
        potential_allergens = []
        for allergen, info in self.allergens.items():
            for ingredient in ingredients:
                if ingredient.lower() in [ai.lower() for ai in info['ingredients']]:
                    potential_allergens.append({
                        'allergen': allergen,
                        'name': info['name'],
                        'ingredient': ingredient
                    })
        
        return {
            'item': item_name,
            'ingredients': ingredients,
            'potential_allergens': potential_allergens,
            'allergen_count': len(potential_allergens)
        }
    
    def save_profiles(self):
        """Save user dietary profiles"""
        try:
            profile_data = {
                'user_profiles': self.user_profiles,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0.0'
            }
            joblib.dump(profile_data, self.model_path)
            logger.info(f"Dietary profiles saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving dietary profiles: {e}")
    
    def load_profiles(self):
        """Load user dietary profiles"""
        try:
            profile_data = joblib.load(self.model_path)
            self.user_profiles = profile_data.get('user_profiles', {})
            logger.info(f"Dietary profiles loaded from {self.model_path}")
        except FileNotFoundError:
            logger.info("No existing dietary profile file found")
            self.user_profiles = {}
        except Exception as e:
            logger.error(f"Error loading dietary profiles: {e}")
            self.user_profiles = {}
