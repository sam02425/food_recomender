# /components/recommendation_highlight.py
"""
UI component for highlighting and selecting recommendations.
"""

import streamlit as st
import streamlit.components.v1 as components
import json

def render_recommendations(recommendations_data, section_title, category_type, on_selection_change, current_selection=None):
    """
    Render recommendations with highlight/disable UI using custom component.

    Args:
        recommendations_data: Dictionary containing recommendation data
        section_title: Title for the recommendation section
        category_type: Type of category (protein, sauce, base, veggie)
        on_selection_change: Callback when selection changes
        current_selection: Currently selected item(s)
    """
    # Convert data to JSON for the component
    json_data = json.dumps({
        "recommendations": recommendations_data,
        "sectionTitle": section_title,
        "categoryType": category_type,
        "currentSelection": current_selection
    })

    # Define component HTML with React
    component_html = f"""
    <script src="https://unpkg.com/react@17/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@17/umd/react-dom.production.min.js"></script>

    <div id="recommendation-component"></div>

    <script>
    const data = {json_data};

    const RecommendationComponent = () => {{
        const [selected, setSelected] = React.useState(data.currentSelection || null);

        const handleSelect = (item) => {{
            setSelected(item);

            // Send message to Streamlit
            const message = {{
                type: "selection-change",
                category: data.categoryType,
                selection: item
            }};

            window.parent.postMessage({{
                type: "streamlit:setComponentValue",
                value: JSON.stringify(message)
            }}, "*");
        }};

        const isRecommended = (item) => {{
            if (!data.recommendations) return false;

            if (data.categoryType === "protein") {{
                return data.recommendations.proteins &&
                       data.recommendations.proteins.includes(item);
            }}
            else if (data.categoryType === "sauce") {{
                return data.recommendations.sauces &&
                       data.recommendations.sauces.includes(item);
            }}
            else if (data.categoryType === "base") {{
                return data.recommendations.base_types &&
                       data.recommendations.base_types.includes(item);
            }}
            else if (data.categoryType === "veggie") {{
                return data.recommendations.veggies &&
                       data.recommendations.veggies.includes(item);
            }}
            return false;
        }};

        const renderItems = () => {{
            const items = [];

            if (data.categoryType === "protein") {{
                items.push("Chicken", "Egg", "Paneer/Indian Cheese", "Soya", "Potato", "Pepperoni");
            }}
            else if (data.categoryType === "sauce") {{
                items.push("Curry Special", "Malai Masala", "Curry Masala", "Marinara",
                          "Yogurt/Raita", "Red Spicy Sauce", "Mint Sauce", "Green Spicy Sauce");
            }}
            else if (data.categoryType === "base") {{
                return (
                    <div>
                        <div className="base-category">
                            <h4>Biryani</h4>
                            <div className="items-grid">
                                {{renderBaseItem("Rice", "Biryani")}}
                            </div>
                        </div>

                        <div className="base-category">
                            <h4>Sandwich & Subs</h4>
                            <div className="items-grid">
                                {{renderBaseItem("Sourdough", "Sandwich")}}
                                {{renderBaseItem("Ciabatta", "Sandwich")}}
                                {{renderBaseItem("White Bread", "Sandwich")}}
                                {{renderBaseItem("Hoagie Bun", "Sandwich")}}
                            </div>
                        </div>

                        <div className="base-category">
                            <h4>Wrap</h4>
                            <div className="items-grid">
                                {{renderBaseItem("Naan", "Wrap")}}
                                {{renderBaseItem("Pita", "Wrap")}}
                            </div>
                        </div>
                    </div>
                );
            }}
            else if (data.categoryType === "veggie") {{
                items.push("Grilled Onion", "Bell Pepper", "Tomato", "Cilantro",
                          "Avocado", "Pineapple", "Spinach", "Jalapeño",
                          "Banana Pepper", "Fried Onions", "Corn", "Cabbage",
                          "Ghee", "Mango Chutney");
            }}

            return (
                <div className="items-grid">
                    {{items.map(item => renderItem(item))}}
                </div>
            );
        }};

        const renderItem = (item) => {{
            const isSelected = selected === item ||
                              (Array.isArray(selected) && selected.includes(item));
            const recommended = isRecommended(item);

            return (
                <div key={{item}}
                     className={{`item ${{isSelected ? 'selected' : ''}}
                                ${{recommended ? 'recommended' : ''}}`}}
                     onClick={{() => handleSelect(item)}}>
                    <div className="item-content">
                        <span>{{item}}</span>
                        {{recommended && <span className="recommendation-badge">✓</span>}}
                    </div>
                </div>
            );
        }};

        const renderBaseItem = (item, type) => {{
            const baseKey = `${{item}}-${{type}}`;
            const isSelected = selected === baseKey ||
                              (selected && selected.item === item && selected.type === type);
            const recommended = isRecommended(type);

            return (
                <div key={{baseKey}}
                     className={{`item ${{isSelected ? 'selected' : ''}}
                                ${{recommended ? 'recommended' : ''}}`}}
                     onClick={{() => handleSelect({{item, type}})}}>
                    <div className="item-content">
                        <span>{{item}}</span>
                        {{recommended && <span className="recommendation-badge">✓</span>}}
                    </div>
                </div>
            );
        }};

        const renderVeggieInfo = () => {{
            if (data.categoryType === "veggie") {{
                return (
                    <div className="veggie-info">
                        <p>First 5 veggies are included. Each additional veggie costs $1.</p>
                        <p>Avocado costs $3.</p>
                    </div>
                );
            }}
            return null;
        }};

        return (
            <div className="recommendation-container">
                <h3>{{data.sectionTitle}}</h3>
                {{renderItems()}}
                {{renderVeggieInfo()}}

                <style jsx>{{`
                    .recommendation-container {
                        font-family: sans-serif;
                        padding: 10px;
                    }
                    .items-grid {
                        display: grid;
                        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                        gap: 10px;
                        margin-bottom: 15px;
                    }
                    .item {
                        padding: 10px;
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        cursor: pointer;
                        transition: all 0.2s;
                        opacity: 0.7;
                    }
                    .item:hover {
                        border-color: #888;
                        opacity: 0.9;
                    }
                    .item.selected {
                        border-color: #2E86C1;
                        background-color: #D6EAF8;
                        opacity: 1;
                    }
                    .item.recommended {
                        border-color: #27AE60;
                        opacity: 1;
                    }
                    .item.selected.recommended {
                        border-color: #2E86C1;
                        background-color: #D6EAF8;
                        box-shadow: 0 0 0 2px #27AE60;
                    }
                    .item-content {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    .recommendation-badge {
                        color: #27AE60;
                        font-weight: bold;
                    }
                    .base-category {
                        margin-bottom: 15px;
                    }
                    .veggie-info {
                        margin-top: 10px;
                        padding: 10px;
                        background-color: #f8f9fa;
                        border-radius: 5px;
                        font-size: 0.9em;
                    }
                `}}</style>
            </div>
        );
    }};

    ReactDOM.render(
        React.createElement(RecommendationComponent),
        document.getElementById('recommendation-component')
    );
    </script>
    """

    # Render the component
    components.html(component_html, height=400, scrolling=True)

    # Return a container to display the current selection
    return st.empty()