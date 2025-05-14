# /ui/kiosk_app.py
"""
UI application for the self-ordering kiosk system.
This provides Streamlit-based UI for customers to interact with the ordering system.
"""

import streamlit as st
import time
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Import recommendation component
from components.recommendation_highlight import render_recommendations

def run_kiosk_ui(kiosk):
    """Run the kiosk UI application."""
    st.title("Curry Creations Ordering Kiosk")

    # Check if a session ID exists, otherwise create one
    if 'session_id' not in st.session_state:
        st.session_state.session_id = int(time.time())
        st.session_state.order_started = False
        st.session_state.current_step = 'start'
        st.session_state.order_data = None
        st.session_state.customer_data = None
        st.session_state.selections = {}
        st.session_state.order_items = []

    # Order start screen
    if not st.session_state.order_started:
        st.header("Welcome to Curry Creations!")
        st.subheader("Ready to create your perfect meal?")

        if st.button("Start New Order", key="start_order"):
            st.session_state.order_started = True
            st.session_state.order_data = kiosk.start_new_order()
            st.session_state.current_step = 'identify'
            st.rerun()

    # Main order flow
    if st.session_state.order_started:
        # Customer identification
        if st.session_state.current_step == 'identify':
            st.header("Let's identify you")

            col1, col2 = st.columns(2)
            with col1:
                phone_number = st.text_input("Phone Number:")

            with col2:
                take_photo = st.camera_input("Take a photo")

            if phone_number and st.button("Continue with Phone"):
                image_data = take_photo.getvalue() if take_photo else None
                identification = kiosk.identify_customer(image_data=image_data, phone_number=phone_number)
                st.session_state.customer_data = identification

                if identification["identified"]:
                    st.session_state.current_step = 'activity'
                else:
                    st.session_state.current_step = 'new_customer'
                st.rerun()

        # New customer
        elif st.session_state.current_step == 'new_customer':
            st.header("Welcome, new customer!")
            name = st.text_input("Your Name:")

            if name and st.button("Save & Continue"):
                customer_data = kiosk.update_customer_info(name)
                st.session_state.customer_data.update(customer_data)
                st.session_state.current_step = 'activity'
                st.rerun()

        # Activity level
        elif st.session_state.current_step == 'activity':
            st.header("What are you up to today?")
            customer_name = st.session_state.customer_data.get("customer_name", "there")
            st.write(f"Hi {customer_name}! We'll help you find the perfect meal.")

            activities = ["Study", "Active/Gym", "Work", "Chilling"]
            activity = st.radio("Activity level:", activities)

            if st.button("Get Recommendations"):
                recommendations = kiosk.get_health_recommendations(activity.lower())
                st.session_state.health_recommendations = recommendations
                st.session_state.current_step = 'health_recommendation'
                st.rerun()

        # Health recommendation
        elif st.session_state.current_step == 'health_recommendation':
            st.header("Health Recommendations")

            recommendations = st.session_state.health_recommendations

            st.write(f"Based on your '{recommendations.get('activity_level', '')}' activity:")
            st.write(recommendations.get('reasoning', ''))

            # Display benefits
            st.subheader("Nutritional Benefits:")
            for benefit in recommendations.get('health_benefits', []):
                st.write(f"- {benefit}")

            # Show protein recommendation with highlighting UI
            protein_container = render_recommendations(
                recommendations,
                "Select Protein",
                "protein",
                lambda x: x,
                st.session_state.get('selected_protein')
            )

            # Get user feedback
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Ignore"):
                    kiosk.process_recommendation_feedback("health", "ignore")
                    st.session_state.current_step = 'weather_recommendation'
                    st.rerun()

            with col2:
                if st.button("Accept"):
                    suggested_protein = recommendations.get('suggested_protein')
                    st.session_state.selected_protein = suggested_protein
                    st.session_state.selections["protein"] = suggested_protein
                    kiosk.process_recommendation_feedback("health", "accept")
                    st.session_state.current_step = 'weather_recommendation'
                    st.rerun()

            with col3:
                custom = st.text_input("My suggestion:")
                if custom and st.button("Apply Custom"):
                    st.session_state.selected_protein = custom
                    st.session_state.selections["protein"] = custom
                    kiosk.process_recommendation_feedback("health", "custom", custom)
                    st.session_state.current_step = 'weather_recommendation'
                    st.rerun()

        # Weather recommendation
        elif st.session_state.current_step == 'weather_recommendation':
            st.header("Weather-Based Recommendations")

            # Get weather recommendations
            if 'weather_recommendations' not in st.session_state:
                recommendations = kiosk.get_weather_recommendations()
                st.session_state.weather_recommendations = recommendations
            else:
                recommendations = st.session_state.weather_recommendations

            # Show current weather
            weather_data = recommendations.get("weather_data", {})
            st.write(f"Current weather: {weather_data.get('condition', 'Unknown')}, {weather_data.get('temperature', 'N/A')}°C")
            st.write(f"Time of day: {recommendations.get('time_of_day', 'afternoon')}")
            st.write(recommendations.get('reasoning', ''))

            # Show base recommendation with highlighting UI
            base_container = render_recommendations(
                recommendations,
                "Select Base",
                "base",
                lambda x: x,
                st.session_state.get('selected_base')
            )

            # Get user feedback
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Ignore Weather Rec"):
                    kiosk.process_recommendation_feedback("weather", "ignore")
                    st.session_state.current_step = 'dish_name'
                    st.rerun()

            with col2:
                if st.button("Accept Weather Rec"):
                    suggested_base = recommendations.get('suggested_base')
                    st.session_state.selected_base = suggested_base
                    st.session_state.selections["base_type"] = suggested_base

                    # Set base option based on type
                    if suggested_base == "Biryani":
                        st.session_state.selections["base_option"] = "Rice"
                    elif suggested_base == "Sandwich":
                        st.session_state.selections["base_option"] = "Sourdough"
                    elif suggested_base == "Wrap":
                        st.session_state.selections["base_option"] = "Naan"

                    kiosk.process_recommendation_feedback("weather", "accept")
                    st.session_state.current_step = 'dish_name'
                    st.rerun()

            with col3:
                custom = st.text_input("My base suggestion:")
                if custom and st.button("Apply Custom Base"):
                    st.session_state.selected_base = custom
                    st.session_state.selections["base_type"] = custom

                    # Set default base option
                    if custom == "Biryani":
                        st.session_state.selections["base_option"] = "Rice"
                    elif custom == "Sandwich":
                        st.session_state.selections["base_option"] = "Sourdough"
                    elif custom == "Wrap":
                        st.session_state.selections["base_option"] = "Naan"

                    kiosk.process_recommendation_feedback("weather", "custom", custom)
                    st.session_state.current_step = 'dish_name'
                    st.rerun()

        # Dish name generation
        elif st.session_state.current_step == 'dish_name':
            st.header("Your Personalized Dish Name")

            # Get dish name suggestions if not already done
            if 'dish_name_suggestions' not in st.session_state:
                # Get current selections
                current_selections = {
                    "protein": st.session_state.selections.get("protein"),
                    "base_type": st.session_state.selections.get("base_type")
                }

                suggestions = kiosk.get_dish_name(current_selections)
                st.session_state.dish_name_suggestions = suggestions
            else:
                suggestions = st.session_state.dish_name_suggestions

            # Display primary suggestion
            st.subheader("Suggested Dish Name:")
            st.markdown(f"### 🎉 {suggestions.get('name', 'Custom Creation')}")

            # Display alternatives
            st.write("Alternative options:")
            for alt in suggestions.get("alternatives", []):
                st.write(f"- {alt}")

            # Get user feedback
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Ignore Name"):
                    kiosk.process_recommendation_feedback("dish_name", "ignore")
                    st.session_state.current_step = 'sauce_selection'
                    st.rerun()

            with col2:
                if st.button("Accept Name"):
                    selected_name = suggestions.get('name')
                    st.session_state.selected_dish_name = selected_name
                    st.session_state.selections["dish_name"] = selected_name
                    kiosk.process_recommendation_feedback("dish_name", "accept")
                    st.session_state.current_step = 'sauce_selection'
                    st.rerun()

            with col3:
                custom = st.text_input("My dish name:")
                if custom and st.button("Use Custom Name"):
                    st.session_state.selected_dish_name = custom
                    st.session_state.selections["dish_name"] = custom
                    kiosk.process_recommendation_feedback("dish_name", "custom", custom)
                    st.session_state.current_step = 'sauce_selection'
                    st.rerun()

        # Sauce selection
        elif st.session_state.current_step == 'sauce_selection':
            st.header("Select Your Sauce")

            # Show sauce options with highlighting UI
            # Use combined recommendations from health and weather
            combined_recommendations = {
                "sauces": st.session_state.health_recommendations.get("sauces", [])
            }

            sauce_container = render_recommendations(
                combined_recommendations,
                "Select Sauce",
                "sauce",
                lambda x: x,
                st.session_state.get('selected_sauce')
            )

            # Manual selection as fallback
            sauces = [
                "Curry Special", "Malai Masala", "Curry Masala", "Marinara",
                "Yogurt/Raita", "Red Spicy Sauce", "Mint Sauce", "Green Spicy Sauce"
            ]

            selected_sauce = st.selectbox("Select a sauce:", sauces)

            if st.button("Continue with Sauce"):
                st.session_state.selected_sauce = selected_sauce
                st.session_state.selections["sauce"] = selected_sauce
                st.session_state.current_step = 'veggie_selection'
                st.rerun()

        # Veggie selection
        elif st.session_state.current_step == 'veggie_selection':
            st.header("Select Your Veggies")

            # Combined recommendations from health
            combined_recommendations = {
                "veggies": st.session_state.health_recommendations.get("veggies", [])
            }

            # Show veggie options with highlighting UI
            veggie_container = render_recommendations(
                combined_recommendations,
                "Select Veggies (First 5 included, extras $1 each, Avocado $3)",
                "veggie",
                lambda x: x,
                st.session_state.get('selected_veggies', [])
            )

            # Manual selection as fallback
            veggies = [
                "Grilled Onion", "Bell Pepper", "Tomato", "Cilantro",
                "Avocado", "Pineapple", "Spinach", "Jalapeño",
                "Banana Pepper", "Fried Onions", "Corn", "Cabbage",
                "Ghee", "Mango Chutney"
            ]

            selected_veggies = st.multiselect("Select veggies:", veggies)

            # Show pricing info
            st.info("First 5 veggies are included. Additional veggies cost $1 each. Avocado costs $3.")

            # Calculate veggie cost
            veggie_count = len(selected_veggies)
            extra_count = max(0, veggie_count - 5)
            avocado_count = 1 if "Avocado" in selected_veggies else 0

            veggie_cost = extra_count + (avocado_count * 3)
            if veggie_cost > 0:
                st.write(f"Veggie cost: ${veggie_cost:.2f}")

            if st.button("Add to Order"):
                st.session_state.selected_veggies = selected_veggies
                st.session_state.selections["veggies"] = selected_veggies

                # Add the item to the order
                order_item = kiosk.add_order_item(st.session_state.selections)
                st.session_state.order_items.append(order_item)

                # Clear selections for next item
                st.session_state.selections = {}

                # Go to order summary
                st.session_state.current_step = 'order_summary'
                st.rerun()

        # Order summary
        elif st.session_state.current_step == 'order_summary':
            st.header("Order Summary")

            # Display all order items
            total_price = 0
            for idx, item in enumerate(st.session_state.order_items):
                with st.expander(f"Item {idx + 1}: {item.get('dish_name', 'Custom Creation')}"):
                    st.write(f"**Protein:** {item.get('protein')}")
                    st.write(f"**Sauce:** {item.get('sauce')}")
                    st.write(f"**Base:** {item.get('base_type')} - {item.get('base_option')}")
                    st.write(f"**Veggies:** {', '.join(item.get('veggies', []))}")
                    st.write(f"**Price:** ${item.get('price', 0):.2f}")

                total_price += item.get('price', 0)

            st.subheader(f"Total Price: ${total_price:.2f}")

            # Add another item or complete order
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Add Another Item"):
                    # Reset selections
                    st.session_state.selections = {}
                    st.session_state.current_step = 'activity'
                    st.rerun()

            with col2:
                if st.button("Complete Order"):
                    completed_order = kiosk.complete_order()
                    st.session_state.completed_order = completed_order
                    st.session_state.current_step = 'social_sharing'
                    st.rerun()

        # Social sharing
        elif st.session_state.current_step == 'social_sharing':
            st.header("Share Your Masterpiece!")
            st.subheader("Your order is being prepared!")

            # Get order details
            order_id = st.session_state.completed_order.get("order_id")
            customer_id = st.session_state.customer_data.get("customer_id")

            # Get the last item's dish name
            if st.session_state.order_items:
                last_item = st.session_state.order_items[-1]
                dish_name = last_item.get("dish_name", "Custom Creation")
            else:
                dish_name = "Custom Creation"

            # Generate share prompt
            sharing_prompt = kiosk.social_agent.generate_share_prompt(
                st.session_state.customer_data.get("customer_name", "Guest"),
                dish_name
            )

            # Display share info
            st.subheader("Take a photo with your creation!")
            customer_photo = st.camera_input("Snap a pic with your masterpiece!")

            # Display sharing options
            st.write("Share on social media:")
            platforms = ["facebook", "instagram", "tiktok"]
            selected_platforms = []

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.checkbox("Facebook"):
                    selected_platforms.append("facebook")
            with col2:
                if st.checkbox("Instagram"):
                    selected_platforms.append("instagram")
            with col3:
                if st.checkbox("TikTok"):
                    selected_platforms.append("tiktok")

            # Display suggested caption
            st.text_area(
                "Caption:",
                sharing_prompt.get("caption", "") + "\n\n" +
                " ".join([f"#{tag}" for tag in sharing_prompt.get("hashtags", [])]),
                height=100
            )

            # Share button
            if customer_photo and selected_platforms and st.button("Share Now!"):
                # Store the photo and share
                image_data = customer_photo.getvalue()

                # In a real app, this would actually share to social media
                sharing_result = kiosk.handle_social_sharing(
                    customer_id=customer_id,
                    image_data=image_data,
                    dish_name=dish_name,
                    platforms=selected_platforms,
                    caption=sharing_prompt.get("caption", "")
                )

                if sharing_result.get("success"):
                    st.success(f"Shared to {', '.join(sharing_result.get('successful_platforms', []))}!")

                    # Show QR code or receipt for order pickup
                    st.session_state.current_step = 'complete'
                    st.rerun()
                else:
                    st.error("Sharing failed. Please try again.")

            # Skip sharing
            if st.button("Skip Sharing"):
                st.session_state.current_step = 'complete'
                st.rerun()

        # Order complete
        elif st.session_state.current_step == 'complete':
            st.balloons()
            st.header("Order Complete!")
            st.subheader(f"Order #{st.session_state.completed_order.get('order_id')}")

            st.success("Your order has been placed and will be ready shortly!")
            st.write("Please proceed to the counter to pick up your order.")

            # Show receipt path
            receipt_path = st.session_state.completed_order.get("receipt_path")
            if receipt_path and os.path.exists(receipt_path):
                with open(receipt_path, 'r') as f:
                    receipt_content = f.read()
                st.text_area("Receipt", receipt_content, height=300)

            # New order button
            if st.button("Start New Order"):
                # Reset everything
                for key in list(st.session_state.keys()):
                    if key != 'session_id':
                        del st.session_state[key]

                st.session_state.order_started = False
                st.session_state.current_step = 'start'
                st.rerun()