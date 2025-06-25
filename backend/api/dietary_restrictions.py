"""
FastAPI endpoints for dietary restrictions and allergen management
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import sys
import os

# Import dietary restrictions manager
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ml_engine.dietary_restrictions import DietaryRestrictionsManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize dietary restrictions manager
dietary_manager = DietaryRestrictionsManager()

router = APIRouter(prefix="/api/dietary", tags=["dietary-restrictions"])

# Pydantic models
class DietaryRestrictionsRequest(BaseModel):
    user_id: str
    restrictions: List[str]  # e.g., ['vegan', 'no_beef']

class AllergensRequest(BaseModel):
    user_id: str
    allergens: List[str]  # e.g., ['dairy', 'nuts']

class SafeOptionsRequest(BaseModel):
    user_id: str
    category: str  # 'protein', 'sauce', 'base', 'vegetables'

class FilterRecommendationsRequest(BaseModel):
    user_id: str
    recommendations: List[Dict[str, Any]]

class DietaryResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    warnings: Optional[List[str]] = None

@router.get("/restrictions/available")
async def get_available_restrictions():
    """Get all available dietary restrictions"""
    try:
        restrictions = {}
        for key, value in dietary_manager.dietary_restrictions.items():
            restrictions[key] = {
                'name': value['name'],
                'description': value['description'],
                'excluded_proteins': value['excluded_proteins'],
                'allowed_proteins': value['allowed_proteins']
            }
        
        return DietaryResponse(
            success=True,
            message="Available dietary restrictions retrieved",
            data={'restrictions': restrictions}
        )
    except Exception as e:
        logger.error(f"Error getting available restrictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/allergens/available")
async def get_available_allergens():
    """Get all available allergen categories"""
    try:
        allergens = {}
        for key, value in dietary_manager.allergens.items():
            allergens[key] = {
                'name': value['name'],
                'ingredients': value['ingredients']
            }
        
        return DietaryResponse(
            success=True,
            message="Available allergens retrieved",
            data={'allergens': allergens}
        )
    except Exception as e:
        logger.error(f"Error getting available allergens: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restrictions/set")
async def set_dietary_restrictions(request: DietaryRestrictionsRequest):
    """Set dietary restrictions for a user"""
    try:
        result = dietary_manager.set_user_dietary_restrictions(
            request.user_id, 
            request.restrictions
        )
        
        if result['success']:
            return DietaryResponse(
                success=True,
                message=f"Dietary restrictions set for user {request.user_id}",
                data=result,
                warnings=[result.get('warning')] if result.get('warning') else None
            )
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Unknown error'))
            
    except Exception as e:
        logger.error(f"Error setting dietary restrictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/allergens/set")
async def set_allergens(request: AllergensRequest):
    """Set allergen information for a user"""
    try:
        result = dietary_manager.set_user_allergens(
            request.user_id,
            request.allergens
        )
        
        if result['success']:
            return DietaryResponse(
                success=True,
                message=f"Allergens set for user {request.user_id}",
                data=result,
                warnings=[result.get('warning')] if result.get('warning') else None
            )
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Unknown error'))
            
    except Exception as e:
        logger.error(f"Error setting allergens: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{user_id}")
async def get_user_dietary_profile(user_id: str):
    """Get complete dietary profile for a user"""
    try:
        profile = dietary_manager.get_user_profile(user_id)
        
        return DietaryResponse(
            success=True,
            message=f"Dietary profile for user {user_id}",
            data=profile
        )
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/options/safe")
async def get_safe_options(request: SafeOptionsRequest):
    """Get safe food options for a user based on their restrictions"""
    try:
        safe_options = dietary_manager.get_safe_options(
            request.user_id,
            request.category
        )
        
        return DietaryResponse(
            success=True,
            message=f"Safe {request.category} options for user {request.user_id}",
            data=safe_options
        )
    except Exception as e:
        logger.error(f"Error getting safe options: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations/filter")
async def filter_recommendations(request: FilterRecommendationsRequest):
    """Filter recommendations based on user's dietary restrictions"""
    try:
        filtered_recs = dietary_manager.filter_recommendations(
            request.user_id,
            request.recommendations
        )
        
        original_count = len(request.recommendations)
        filtered_count = len(filtered_recs)
        
        return DietaryResponse(
            success=True,
            message=f"Filtered {original_count} recommendations to {filtered_count} safe options",
            data={
                'original_count': original_count,
                'filtered_count': filtered_count,
                'filtered_recommendations': filtered_recs,
                'restrictions_applied': True
            }
        )
    except Exception as e:
        logger.error(f"Error filtering recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ingredients/{item_name}")
async def get_ingredient_info(item_name: str):
    """Get detailed ingredient information for a menu item"""
    try:
        ingredient_info = dietary_manager.get_ingredient_info(item_name)
        
        return DietaryResponse(
            success=True,
            message=f"Ingredient information for {item_name}",
            data=ingredient_info
        )
    except Exception as e:
        logger.error(f"Error getting ingredient info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/profile/{user_id}/restrictions")
async def clear_dietary_restrictions(user_id: str):
    """Clear all dietary restrictions for a user"""
    try:
        result = dietary_manager.set_user_dietary_restrictions(user_id, [])
        
        return DietaryResponse(
            success=True,
            message=f"Dietary restrictions cleared for user {user_id}",
            data=result
        )
    except Exception as e:
        logger.error(f"Error clearing restrictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/profile/{user_id}/allergens")
async def clear_allergens(user_id: str):
    """Clear all allergen information for a user"""
    try:
        result = dietary_manager.set_user_allergens(user_id, [])
        
        return DietaryResponse(
            success=True,
            message=f"Allergens cleared for user {user_id}",
            data=result
        )
    except Exception as e:
        logger.error(f"Error clearing allergens: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_dietary_stats():
    """Get statistics about dietary restrictions usage"""
    try:
        total_users = len(dietary_manager.user_profiles)
        users_with_restrictions = sum(
            1 for profile in dietary_manager.user_profiles.values()
            if profile.get('dietary_restrictions') or profile.get('allergens')
        )
        
        # Count restriction types
        restriction_counts = {}
        allergen_counts = {}
        
        for profile in dietary_manager.user_profiles.values():
            for restriction in profile.get('dietary_restrictions', []):
                restriction_counts[restriction] = restriction_counts.get(restriction, 0) + 1
            
            for allergen in profile.get('allergens', []):
                allergen_counts[allergen] = allergen_counts.get(allergen, 0) + 1
        
        stats = {
            'total_users': total_users,
            'users_with_restrictions': users_with_restrictions,
            'restriction_usage_rate': users_with_restrictions / total_users if total_users > 0 else 0,
            'popular_restrictions': restriction_counts,
            'popular_allergens': allergen_counts
        }
        
        return DietaryResponse(
            success=True,
            message="Dietary restriction statistics",
            data=stats
        )
    except Exception as e:
        logger.error(f"Error getting dietary stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
