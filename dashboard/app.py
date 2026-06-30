import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pickle

#  PAGE CONFIG 
st.set_page_config(
    page_title="OTT Trends Dashboard",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
    <style>
    .main-title {
        font-size: 36px;
        font-weight: bold;
        color: #E50914;
    }
    </style>
""", unsafe_allow_html=True)


#  LOAD DATA 
@st.cache_data
def load_data():
    netflix = pd.read_csv('../data/netflix_clean.csv')
    trending = pd.read_csv('../data/tmdb_trending.csv')
    forecast = pd.read_csv('../data/forecast_results.csv')
    top_genres = pd.read_csv('../data/top_genres.csv')
    return netflix, trending, forecast, top_genres

netflix, trending, forecast, top_genres = load_data()


#  SIDEBAR NAVIGATION 
st.sidebar.markdown('<p class="main-title">🎬 OTT Trends</p>', unsafe_allow_html=True)
st.sidebar.markdown("---")

page = st.sidebar.radio("Navigate to:", [
    "📊 Overview",
    "📈 Trend Viewer",
    "🔮 Prediction Panel",
    "🔍 Search & Filter"
])



# PAGE 1: OVERVIEW

if page == "📊 Overview":
    st.title("OTT Content Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Titles", len(netflix))
    col2.metric("Movies", len(netflix[netflix['type'] == 'Movie']))
    col3.metric("TV Shows", len(netflix[netflix['type'] == 'TV Show']))
    col4.metric("Countries", netflix['country'].nunique())

    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Top 10 Genres")
        genres = netflix['listed_in'].str.split(', ').explode()
        top10 = genres.value_counts().head(10).reset_index()
        top10.columns = ['Genre', 'Count']
        fig = px.bar(top10, x='Count', y='Genre', orientation='h',
                     color='Count', color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Content Split")
        type_counts = netflix['type'].value_counts().reset_index()
        type_counts.columns = ['Type', 'Count']
        fig2 = px.pie(type_counts, values='Count', names='Type',
                      color_discrete_sequence=['#E50914', '#1A73E8'])
        st.plotly_chart(fig2, use_container_width=True)



# PAGE 2: TREND VIEWER

elif page == "📈 Trend Viewer":
    st.title("Content Trends Over Time")

    years = netflix['year_added'].dropna()
    min_year, max_year = int(years.min()), int(years.max())

    sel_range = st.slider(
        "Select Year Range",
        min_year, max_year, (min_year, max_year)
    )

    filtered = netflix[
        (netflix['year_added'] >= sel_range[0]) &
        (netflix['year_added'] <= sel_range[1])
    ]

    yearly = filtered.groupby('year_added').size().reset_index()
    yearly.columns = ['Year', 'Titles Added']

    fig = px.line(yearly, x='Year', y='Titles Added',
                  markers=True, line_shape='spline')
    fig.update_traces(line_color='#E50914', line_width=3)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Genre-wise Breakdown")
    all_genres = netflix['listed_in'].str.split(', ').explode().unique()
    selected_genre = st.selectbox("Select a Genre", sorted(all_genres))

    genre_filtered = filtered[filtered['listed_in'].str.contains(selected_genre, na=False)]
    genre_yearly = genre_filtered.groupby('year_added').size().reset_index()
    genre_yearly.columns = ['Year', 'Count']

    fig2 = px.bar(genre_yearly, x='Year', y='Count',
                 color_discrete_sequence=['#1A73E8'])
    st.plotly_chart(fig2, use_container_width=True)



# PAGE 3: PREDICTION PANEL

elif page == "🔮 Prediction Panel":
    st.title("Trend Predictions")

    # ── FORECAST CHART ──────────────────────────────────────────
    st.subheader("Genre Trend Forecast (Next 3 Years)")

    try:
        forecast['ds'] = pd.to_datetime(forecast['ds'], errors='coerce')
        forecast_clean = forecast.dropna(subset=['ds', 'yhat'])

        if forecast_clean.empty:
            st.error(" forecast_results.csv has no valid data. Re-run Phase 4 Step 9 in your notebook.")
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=forecast_clean['ds'], y=forecast_clean['yhat'],
                mode='lines', name='Forecast', line=dict(color='#E50914', width=3)
            ))
            fig.add_trace(go.Scatter(
                x=forecast_clean['ds'], y=forecast_clean['yhat_upper'],
                mode='lines', name='Upper Bound',
                line=dict(color='lightgrey', dash='dash')
            ))
            fig.add_trace(go.Scatter(
                x=forecast_clean['ds'], y=forecast_clean['yhat_lower'],
                mode='lines', name='Lower Bound',
                line=dict(color='lightgrey', dash='dash')
            ))
            fig.update_layout(xaxis_title="Year", yaxis_title="Predicted Titles", height=400)
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f" Could not load forecast chart: {e}")

    st.markdown("---")

    #  RATING PREDICTOR 
    st.subheader(" Predict If a Title Will Be Highly Rated")

    col1, col2, col3 = st.columns(3)
    with col1:
        popularity = st.slider("Popularity Score", 0, 1000, 200)
    with col2:
        vote_count = st.slider("Expected Vote Count", 0, 10000, 1000)
    with col3:
        year = st.number_input("Release Year", 2000, 2030, 2025)

    if st.button("🔮 Predict Rating", type="primary"):
        try:
            with open('../models/rating_predictor.pkl', 'rb') as f:
                model = pickle.load(f)

            prediction = model.predict([[popularity, vote_count, year]])[0]

            if prediction == 1:
                st.success(" Prediction: **HIGH RATED** (7.0+)")
            else:
                st.warning(" Prediction: **Average or Below Average**")

        except FileNotFoundError:
            st.error(" Model file not found at '../models/rating_predictor.pkl'. "
                      "Make sure you saved it in Phase 4, Step 17, and that you're "
                      "running streamlit from inside the dashboard/ folder.")
        except Exception as e:
            st.error(f" Prediction failed: {e}")



# PAGE 4: SEARCH & FILTER

elif page == "🔍 Search & Filter":
    st.title("Search & Filter Content")

    col1, col2, col3 = st.columns(3)

    with col1:
        search_query = st.text_input("Search by Title")
    with col2:
        type_filter = st.selectbox("Type", ["All", "Movie", "TV Show"])
    with col3:
        # FIX: convert all rating values to string first so sorted()
        # doesn't crash on mixed data types (e.g. text + NaN + numbers)
        rating_options = netflix['rating'].dropna().astype(str).unique().tolist()
        rating_filter = st.selectbox("Rating", ["All"] + sorted(rating_options))

    results = netflix.copy()

    if search_query:
        results = results[results['title'].str.contains(search_query, case=False, na=False)]
    if type_filter != "All":
        results = results[results['type'] == type_filter]
    if rating_filter != "All":
        results = results[results['rating'].astype(str) == rating_filter]

    st.write(f"Found **{len(results)}** results")
    st.dataframe(
        results[['title', 'type', 'listed_in', 'release_year', 'rating', 'country']],
        use_container_width=True
    )