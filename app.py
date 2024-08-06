import streamlit as st
import pickle
import pandas as pd
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_poster_and_details(movie_id):
    try:
        response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US")
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        poster_path = data.get('poster_path')
        details = {
            "title": data.get('title'),
            "overview": data.get('overview'),
            "release_date": data.get('release_date'),
            "rating": data.get('vote_average')
        }
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            logging.warning(f"No poster path found for movie_id: {movie_id}")
            poster_url = "default_poster_url"  # Replace with a valid default URL
        
        return poster_url, details
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching poster and details for movie_id: {movie_id}, error: {e}")
        return "default_poster_url", {}  # Replace with a valid default URL

def recommend(movie, num_recommendations=5):
    movie_index = movies[movies['title'] == movie].index[0]
    top_similar_movies = top_n_similarity[movie_index]
    
    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_details = []
    count = 0
    for similar_movie in top_similar_movies:
        similar_movie_index = similar_movie[0]
        movie_id = movies.iloc[similar_movie_index].movie_id
        movie_title = movies.iloc[similar_movie_index].title
        poster_url, details = fetch_poster_and_details(movie_id)
        
        recommended_movies.append(movie_title)
        recommended_movies_posters.append(poster_url)
        recommended_movies_details.append(details)
        
        count += 1
        if count >= num_recommendations:
            break
    
    return recommended_movies, recommended_movies_posters, recommended_movies_details

# Load movies and similarity data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
top_n_similarity = pickle.load(open('top_n_similarity.pkl', 'rb'))

st.title('AI Powered Movie Recommender')

st.markdown(
    """
    <style>
    .custom-select-text {
        color: white;
        font-size: 24px;
        font-weight: bold;
        background: linear-gradient(90deg, rgba(0,210,255,1) 0%, rgba(0,150,255,1) 100%);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .recommendation-card {
        background-color: #f0f2f6;
        padding: 10px;
        margin: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        text-align: center;
        min-width: 200px;
        max-width: 200px;
    }
    .movie-title {
        font-size: 18px;
        font-weight: bold;
    }
    .movie-details {
        font-size: 14px;
        color: #555;
    }
    .horizontal-scroll {
        display: flex;
        overflow-x: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<p class="custom-select-text">Type or select a movie from the dropdown:</p>', unsafe_allow_html=True)

selected_movie_name = st.selectbox(
    '',
    movies['title'].values
)

num_recommendations = st.slider('Number of recommendations', 1, 10, 5)

if st.button('Search'):
    names, posters, details = recommend(selected_movie_name, num_recommendations=num_recommendations)
    
    # Display recommendations in a horizontal scroll container
    st.markdown('<div class="horizontal-scroll">', unsafe_allow_html=True)
    for i in range(len(names)):
        st.markdown(f"""
        <div class="recommendation-card">
            <img src="{posters[i]}" alt="{names[i]}" style="width:100%; height:auto; border-radius:10px;">
            <div class="movie-title">{names[i]}</div>
            <div class="movie-details">
                <p>Release Date: {details[i].get('release_date', 'N/A')}</p>
                <p>Rating: {details[i].get('rating', 'N/A')}</p>
                <p>{details[i].get('overview', 'N/A')}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
