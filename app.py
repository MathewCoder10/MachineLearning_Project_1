import streamlit as st
import pickle
import pandas as pd
import requests
import logging
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_poster(movie_id):
    try:
        response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US")
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            logging.warning(f"No poster path found for movie_id: {movie_id}")
            return "default_poster_url"  # Replace with a valid default URL
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching poster for movie_id: {movie_id}, error: {e}")
        return "default_poster_url"  # Replace with a valid default URL

def recommend(movie, num_recommendations=15):
    movie_index = movies[movies['title'] == movie].index[0]
    top_similar_movies = top_n_similarity[movie_index]
    
    recommended_movies = []
    recommended_movies_posters = []
    count = 0
    for similar_movie in top_similar_movies:
        similar_movie_index = similar_movie[0]
        movie_id = movies.iloc[similar_movie_index].movie_id
        recommended_movies.append(movies.iloc[similar_movie_index].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
        count += 1
        if count >= num_recommendations:
            break
    
    return recommended_movies, recommended_movies_posters

# Load movies and similarity data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
top_n_similarity = pickle.load(open('top_n_similarity.pkl', 'rb'))

# User Authentication (Simple Version)
if 'username' not in st.session_state:
    st.session_state['username'] = None

if st.session_state['username'] is None:
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button('Login'):
        st.session_state['username'] = username
        st.success(f'Welcome {username}!')
else:
    st.title(f'Welcome {st.session_state["username"]}!')

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
        names, posters = recommend(selected_movie_name, num_recommendations=num_recommendations)
        
        # Display recommendations
        num_cols = 5
        num_rows = len(names) // num_cols + 1
        for i in range(num_rows):
            row = st.columns(num_cols)
            for j in range(num_cols):
                index = i * num_cols + j
                if index < len(names):
                    with row[j]:
                        st.text(names[index])
                        try:
                            st.image(posters[index])
                        except Exception as e:
                            logging.error(f"Error displaying image for {names[index]}: {e}")
                            st.text("Image not available")

    # Log out button
    if st.button('Logout'):
        st.session_state['username'] = None
        st.experimental_rerun()
