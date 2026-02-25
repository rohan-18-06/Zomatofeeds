# ================================
# ZOMATO FEEDBACK ANALYZER (Single File Structured Version)
# ================================

import streamlit as st
import pandas as pd
import plotly.express as px
import time
import re


# ================================
# 1️⃣ PAGE CONFIGURATION
# ================================

def setup_page():
    st.set_page_config(
        page_title="MyFeeds@ZOMATO.com",
        page_icon="🍕",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def inject_css():
    st.markdown("""
    <style>
        .stApp {
            background-color: ivory;
            color: #2e7d32;
            font-family: 'Segoe UI', sans-serif;
        }
        .price-tag {
            font-size: 20px;
            font-weight: bold;
            color: white;
            background-color: #d32f2f;
            padding: 5px 12px;
            border-radius: 20px;
        }
        .review-box {
            border-left: 5px solid;
            padding: 10px;
            margin: 8px 0;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)


# ================================
# 2️⃣ SESSION INITIALIZATION
# ================================

def init_session():
    if "db" not in st.session_state:
        st.session_state.db = []

    if "products" not in st.session_state:
        st.session_state.products = {
            "Pizza": {
                "ts": 0, "c": 0,
                "type": "Breads",
                "price": 549,
                "vnv": "Veg/Non-Veg",
                "data": "Cheese, Mushroom, Chicken"
            },
            "Burger": {
                "ts": 0, "c": 0,
                "type": "Breads",
                "price": 349,
                "vnv": "Veg/Non-Veg",
                "data": "Cheese, Onion, Patty"
            },
            "French Fries": {
                "ts": 0, "c": 0,
                "type": "Snacks",
                "price": 249,
                "vnv": "Veg",
                "data": "Salted, Roasted"
            },
            "Nuggets": {
                "ts": 0, "c": 0,
                "type": "Snacks",
                "price": 199,
                "vnv": "Veg/Non-Veg",
                "data": "Crispy Chicken/Veg"
            }
        }


# ================================
# 3️⃣ HELPER FUNCTIONS
# ================================

def valid_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email)


def calculate_average(total_score, count):
    if count == 0:
        return 0
    return round(total_score / count, 1)


def analyze_sentiment(text):
    text = re.sub(r"[^\w\s]", "", text.lower())

    positive_words = ["delicious", "good", "wonderful", "happy", "best", "tasty", "love"]
    negative_words = ["bad", "worst", "bitter", "salty", "regret", "slow", "cold", "disappointing"]

    pos = sum(len(re.findall(rf"\b{w}\b", text)) for w in positive_words)
    neg = sum(len(re.findall(rf"\b{w}\b", text)) for w in negative_words)

    if pos > neg:
        return "Positive 😊", "#2E7D32"
    elif neg > pos:
        return "Negative 😞", "#D32F2F"
    else:
        return "Neutral 😐", "#FFA000"


# ================================
# 4️⃣ FEEDBACK SECTION
# ================================

def feedback_section():
    st.subheader("🍽 Explore Menu")

    cols = st.columns(4)

    for i, (name, info) in enumerate(st.session_state.products.items()):
        with cols[i % 4]:
            avg = calculate_average(info["ts"], info["c"])

            st.markdown(f"""
                <h3>{name}</h3>
                <p>⭐ {avg} ({info['c']} reviews)</p>
                <p>{info['vnv']} | {info['type']}</p>
                <p>{info['data']}</p>
                <div class="price-tag">₹{info['price']}</div>
            """, unsafe_allow_html=True)

    st.divider()
    st.subheader("✍ Submit Review")

    email = st.text_input("Email Address")
    product = st.selectbox("Select Product", list(st.session_state.products.keys()))
    rating = st.slider("Rate the Item", 1, 5, 3)
    review = st.text_area("Write your feedback")

    if st.button("Submit Review", use_container_width=True):

        if not valid_email(email):
            st.error("Please enter a valid email address.")

        elif any(r for r in st.session_state.db
                 if r["email"] == email and r["prod"] == product):
            st.warning("You already submitted a review for this product.")

        elif review.strip() == "":
            st.warning("Review cannot be empty.")

        else:
            sentiment, color = analyze_sentiment(review)

            st.session_state.products[product]["ts"] += rating
            st.session_state.products[product]["c"] += 1

            st.session_state.db.append({
                "email": email,
                "prod": product,
                "rating": rating,
                "review": review,
                "sentiment": sentiment,
                "color": color,
                "time": time.time()
            })

            st.success("Thank you for your feedback!")
            time.sleep(1)
            st.rerun()


# ================================
# 5️⃣ ANALYTICS SECTION
# ================================

def analytics_section():
    st.subheader("📊 Performance Insights")

    if not st.session_state.db:
        st.info("No reviews submitted yet.")
        return

    df = pd.DataFrame(st.session_state.db)

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.histogram(
            df,
            x="prod",
            color="sentiment",
            title="Sentiment Distribution",
            barmode="group"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        avg_df = df.groupby("prod")["rating"].mean().reset_index()
        fig2 = px.bar(
            avg_df,
            x="prod",
            y="rating",
            title="Average Rating by Product"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📝 Recent Reviews")

    df = df.sort_values("time", ascending=False)

    for _, row in df.iterrows():
        st.markdown(f"""
            <div class="review-box" style="border-color:{row['color']};">
                <b>{row['email']}</b> | {row['sentiment']}<br>
                {"⭐"*row['rating']}<br>
                "{row['review']}"
            </div>
        """, unsafe_allow_html=True)


# ================================
# 6️⃣ MAIN FUNCTION
# ================================

def main():
    setup_page()
    inject_css()
    init_session()

    st.title("🍕 Zomato Feedback Analyzer")

    menu = st.sidebar.radio("Navigation", ["Feedback", "Analytics"])

    if menu == "Feedback":
        feedback_section()
    else:
        analytics_section()


# ================================
# RUN APP
# ================================

if __name__ == "__main__":
    main()
