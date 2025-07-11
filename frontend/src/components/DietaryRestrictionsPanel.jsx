import React, { useState, useEffect } from 'react';
import './DietaryRestrictionsPanel.css';

const DietaryRestrictionsPanel = ({
    customerId,
    onRestrictionsChange,
    onAllergensChange,
    visible = true,
    position = 'side' // 'side' or 'modal'
}) => {
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    const [dietaryRestrictions, setDietaryRestrictions] = useState([]);
    const [allergens, setAllergens] = useState([]);
    const [availableRestrictions, setAvailableRestrictions] = useState({});
    const [availableAllergens, setAvailableAllergens] = useState({});
    const [userProfile, setUserProfile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [showIngredients, setShowIngredients] = useState({});

    // Define dietary restrictions with user-friendly labels
    const restrictionLabels = {
        'vegan': '🌱 Vegan',
        'vegetarian': '🥬 Vegetarian (No eggs)',
        'lacto_vegetarian': '🥛 Lacto-Vegetarian',
        'ovo_vegetarian': '🥚 Ovo-Vegetarian',
        'lacto_ovo_vegetarian': '🥛🥚 Lacto-Ovo Vegetarian',
        'halal': '☪️ Halal',
        'no_beef': '🚫🥩 No Beef',
        'no_pork': '🚫🥓 No Pork'
    };

    // Define restriction compatibility rules
    const restrictionCompatibility = {
        'vegan': {
            incompatible: ['vegetarian', 'lacto_vegetarian', 'ovo_vegetarian', 'lacto_ovo_vegetarian', 'halal', 'no_beef', 'no_pork'],
            description: 'Most restrictive - excludes all animal products'
        },
        'vegetarian': {
            incompatible: ['vegan', 'lacto_vegetarian', 'ovo_vegetarian', 'lacto_ovo_vegetarian'],
            description: 'No meat, fish, or eggs - only dairy allowed'
        },
        'lacto_vegetarian': {
            incompatible: ['vegan', 'vegetarian', 'ovo_vegetarian', 'lacto_ovo_vegetarian'],
            description: 'Dairy allowed, no meat/fish/eggs'
        },
        'ovo_vegetarian': {
            incompatible: ['vegan', 'vegetarian', 'lacto_vegetarian', 'lacto_ovo_vegetarian'],
            description: 'Eggs allowed, no meat/fish/dairy'
        },
        'lacto_ovo_vegetarian': {
            incompatible: ['vegan', 'vegetarian', 'lacto_vegetarian', 'ovo_vegetarian'],
            description: 'Dairy and eggs allowed, no meat/fish'
        },
        'halal': {
            incompatible: ['vegan'],
            description: 'Halal certified only - compatible with most restrictions'
        },
        'no_beef': {
            incompatible: [],
            description: 'No beef products - compatible with most restrictions'
        },
        'no_pork': {
            incompatible: [],
            description: 'No pork products - compatible with most restrictions'
        }
    };

    const allergenLabels = {
        'dairy': '🥛 Dairy',
        'eggs': '🥚 Eggs',
        'nuts': '🥜 Tree Nuts',
        'peanuts': '🥜 Peanuts',
        'soy': '🫘 Soy',
        'gluten': '🌾 Gluten',
        'shellfish': '🦐 Shellfish',
        'fish': '🐟 Fish',
        'sesame': '🌰 Sesame'
    };

    useEffect(() => {
        loadAvailableOptions();
        if (customerId) {
            loadUserProfile();
        }
    }, [customerId]);

    const loadAvailableOptions = async () => {
        try {
            const [restrictionsRes, allergensRes] = await Promise.all([
                fetch(`${API_URL}/api/dietary/restrictions/available`),
                fetch(`${API_URL}/api/dietary/allergens/available`)
            ]);

            if (restrictionsRes.ok) {
                const data = await restrictionsRes.json();
                setAvailableRestrictions(data.data?.restrictions || {});
            } else {
                console.error('Failed to load restrictions:', restrictionsRes.status);
                setAvailableRestrictions({});
            }

            if (allergensRes.ok) {
                const data = await allergensRes.json();
                setAvailableAllergens(data.data?.allergens || {});
            } else {
                console.error('Failed to load allergens:', allergensRes.status);
                setAvailableAllergens({});
            }
        } catch (error) {
            console.error('Error loading available options:', error);
            setAvailableRestrictions({});
            setAvailableAllergens({});
        }
    };

    const loadUserProfile = async () => {
        if (!customerId) return;

        try {
            setLoading(true);
            const response = await fetch(`${API_URL}/api/dietary/profile/${customerId}`);
            if (response.ok) {
                const data = await response.json();
                const profile = data.data;
                setUserProfile(profile);
                setDietaryRestrictions(profile.dietary_restrictions || []);
                setAllergens(profile.allergens || []);
            }
        } catch (error) {
            console.error('Error loading user profile:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleRestrictionToggle = async (restriction) => {
        if (!customerId) return;

        let newRestrictions;

        if (dietaryRestrictions.includes(restriction)) {
            // Removing restriction
            newRestrictions = dietaryRestrictions.filter(r => r !== restriction);
        } else {
            // Adding restriction - apply smart compatibility rules
            const compatibility = restrictionCompatibility[restriction];
            if (compatibility) {
                // Remove incompatible restrictions
                newRestrictions = dietaryRestrictions.filter(r =>
                    !compatibility.incompatible.includes(r)
                );
                // Add the new restriction
                newRestrictions = [...newRestrictions, restriction];
            } else {
                newRestrictions = [...dietaryRestrictions, restriction];
            }
        }

        setDietaryRestrictions(newRestrictions);
        await saveRestrictions(newRestrictions);

        if (onRestrictionsChange) {
            onRestrictionsChange(newRestrictions);
        }
    };

    const handleAllergenToggle = async (allergen) => {
        if (!customerId) return;

        const newAllergens = allergens.includes(allergen)
            ? allergens.filter(a => a !== allergen)
            : [...allergens, allergen];

        setAllergens(newAllergens);
        await saveAllergens(newAllergens);

        if (onAllergensChange) {
            onAllergensChange(newAllergens);
        }
    };

    const saveRestrictions = async (restrictions) => {
        try {
            setLoading(true);
            const response = await fetch(`${API_URL}/api/dietary/restrictions/${customerId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    restrictions: restrictions
                })
            });

            if (response.ok) {
                console.log('Dietary restrictions saved successfully');
            }
        } catch (error) {
            console.error('Error saving restrictions:', error);
        } finally {
            setLoading(false);
        }
    };

    const saveAllergens = async (allergensToSave) => {
        try {
            setLoading(true);
            const response = await fetch(`${API_URL}/api/dietary/allergens/${customerId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    allergens: allergensToSave
                })
            });

            if (response.ok) {
                console.log('Allergens saved successfully');
            }
        } catch (error) {
            console.error('Error saving allergens:', error);
        } finally {
            setLoading(false);
        }
    };

    const getIngredientInfo = async (itemName) => {
        try {
            const response = await fetch(`${API_URL}/api/dietary/ingredient-info?item_name=${encodeURIComponent(itemName)}`);
            if (response.ok) {
                const data = await response.json();
                return data;
            }
        } catch (error) {
            console.error('Error getting ingredient info:', error);
        }
        return null;
    };

    const toggleIngredientInfo = async (itemName) => {
        if (showIngredients[itemName]) {
            setShowIngredients(prev => ({ ...prev, [itemName]: null }));
        } else {
            const info = await getIngredientInfo(itemName);
            setShowIngredients(prev => ({ ...prev, [itemName]: info }));
        }
    };

    const clearAllRestrictions = async () => {
        if (!customerId) return;

        setDietaryRestrictions([]);
        setAllergens([]);
        await Promise.all([
            saveRestrictions([]),
            saveAllergens([])
        ]);

        if (onRestrictionsChange) onRestrictionsChange([]);
        if (onAllergensChange) onAllergensChange([]);
    };

    // Helper function to check if a restriction is disabled due to incompatibility
    const isRestrictionDisabled = (restriction) => {
        if (dietaryRestrictions.includes(restriction)) return false;

        // Check if any currently selected restriction is incompatible with this one
        return dietaryRestrictions.some(selectedRestriction => {
            const compatibility = restrictionCompatibility[selectedRestriction];
            return compatibility && compatibility.incompatible.includes(restriction);
        });
    };

    if (!visible) return null;

    const containerClass = position === 'modal' ? 'dietary-modal' : 'dietary-panel';

    return (
        <div className={containerClass}>
            <div className="dietary-header">
                <h3>🍽️ Dietary Preferences & Allergies</h3>
                {(dietaryRestrictions.length > 0 || allergens.length > 0) && (
                    <button
                        className="clear-all-btn"
                        onClick={clearAllRestrictions}
                        disabled={loading}
                    >
                        Clear All
                    </button>
                )}
            </div>

            {loading && (
                <div className="loading-indicator">
                    <div className="spinner"></div>
                    <span>Updating preferences...</span>
                </div>
            )}

            {!customerId && (
                <div className="no-customer-warning">
                    <p>⚠️ Please identify yourself first to save dietary preferences</p>
                </div>
            )}

                        {(!availableRestrictions || !availableAllergens) && (
                <div className="loading-indicator">
                    <div className="spinner"></div>
                    <span>Loading dietary options...</span>
                </div>
            )}

            {/* Dietary Restrictions Section */}
            {availableRestrictions && (
                <div className="restrictions-section">
                    <h4>🥗 Dietary Restrictions</h4>
                    <p className="restriction-help-text">
                        💡 <strong>Smart Selection:</strong> Selecting certain restrictions will automatically deselect incompatible ones to avoid confusion.
                    </p>
                    <div className="options-grid">
                        {Object.keys(availableRestrictions).map(restriction => {
                            const isDisabled = isRestrictionDisabled(restriction);
                            const isSelected = dietaryRestrictions.includes(restriction);
                            const compatibility = restrictionCompatibility[restriction];

                            return (
                                <div key={restriction} className={`restriction-item ${isDisabled ? 'disabled' : ''} ${isSelected ? 'selected' : ''}`}>
                                    <label className="restriction-checkbox">
                                        <input
                                            type="checkbox"
                                            checked={isSelected}
                                            onChange={() => handleRestrictionToggle(restriction)}
                                            disabled={!customerId || loading || isDisabled}
                                        />
                                        <span className="checkmark"></span>
                                        <span className="restriction-label">
                                            {restrictionLabels[restriction] || restriction}
                                        </span>
                                    </label>
                                    <div className="restriction-description">
                                        {compatibility?.description || availableRestrictions[restriction]?.description}
                                    </div>
                                    {isSelected && (
                                        <div className="allowed-proteins">
                                            <strong>✅ Allowed proteins:</strong>{' '}
                                            {availableRestrictions[restriction]?.allowed_proteins?.join(', ') || 'None specified'}
                                        </div>
                                    )}
                                    {isDisabled && (
                                        <div className="incompatible-notice">
                                            ⚠️ Incompatible with current selection
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Allergens Section */}
            {availableAllergens && (
                <div className="allergens-section">
                    <h4>⚠️ Allergies & Sensitivities</h4>
                    <p className="allergen-warning">
                        Please select ALL ingredients you are allergic to or sensitive to
                    </p>
                    <div className="options-grid">
                        {Object.keys(availableAllergens).map(allergen => (
                            <div key={allergen} className="allergen-item">
                                <label className="allergen-checkbox">
                                    <input
                                        type="checkbox"
                                        checked={allergens.includes(allergen)}
                                        onChange={() => handleAllergenToggle(allergen)}
                                        disabled={!customerId || loading}
                                    />
                                    <span className="checkmark allergen-checkmark"></span>
                                    <span className="allergen-label">
                                        {allergenLabels[allergen] || allergen}
                                    </span>
                                </label>
                                <button
                                    className="ingredient-info-btn"
                                    onClick={() => toggleIngredientInfo(allergen)}
                                    title="View ingredients that contain this allergen"
                                >
                                    ℹ️ Ingredients
                                </button>

                                {showIngredients[allergen] && (
                                    <div className="ingredient-details">
                                        <strong>Contains:</strong>
                                        <div className="ingredient-list">
                                            {availableAllergens[allergen]?.ingredients?.map(ingredient => (
                                                <span key={ingredient} className="ingredient-tag">
                                                    {ingredient}
                                                </span>
                                            )) || 'No specific ingredients listed'}
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Current Profile Summary */}
            {userProfile && userProfile.has_restrictions && availableRestrictions && availableAllergens && (
                <div className="profile-summary">
                    <h4>📋 Your Current Preferences</h4>
                    <div className="summary-content">
                        {dietaryRestrictions.length > 0 && (
                            <div className="summary-section">
                                <strong>Dietary Restrictions:</strong>
                                <div className="tag-list">
                                    {dietaryRestrictions.map(restriction => (
                                        <span key={restriction} className="restriction-tag">
                                            {restrictionLabels[restriction] || restriction}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {allergens.length > 0 && (
                            <div className="summary-section">
                                <strong>Allergies:</strong>
                                <div className="tag-list">
                                    {allergens.map(allergen => (
                                        <span key={allergen} className="allergen-tag">
                                            {allergenLabels[allergen] || allergen}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {userProfile.last_updated && (
                            <div className="last-updated">
                                Last updated: {new Date(userProfile.last_updated).toLocaleDateString()}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Safety Notice */}
            <div className="safety-notice">
                <h4>🛡️ AI Safety Notice</h4>
                <p>
                    Our AI system will automatically filter out recommendations that conflict with your dietary restrictions and allergies.
                    However, please always verify ingredients with restaurant staff for severe allergies.
                </p>
                <p>
                    <strong>Next time you visit:</strong> Your preferences will be remembered to provide better, safer suggestions.
                </p>
            </div>
        </div>
    );
};

export default DietaryRestrictionsPanel;
