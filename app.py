import streamlit as st
import pickle
import pandas as pd
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

API_KEY = '8265bd1679663a7ea12ac168da84d2e8'

def fetch_movie_details(movie_id):
    try:
        response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US")
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching movie details for movie_id: {movie_id}, error: {e}")
        return None

def fetch_cast_and_crew(movie_id):
    try:
        response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}&language=en-US")
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching cast and crew for movie_id: {movie_id}, error: {e}")
        return None

def fetch_poster(movie_id):
    try:
        response = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US")
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
    recommended_movie_ids = []
    count = 0
    for similar_movie in top_similar_movies:
        similar_movie_index = similar_movie[0]
        movie_id = movies.iloc[similar_movie_index].movie_id
        recommended_movies.append(movies.iloc[similar_movie_index].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
        recommended_movie_ids.append(movie_id)
        count += 1
        if count >= num_recommendations:
            break
    
    return recommended_movies, recommended_movies_posters, recommended_movie_ids

def display_movie_details(movie_id):
    movie_details = fetch_movie_details(movie_id)
    cast_and_crew = fetch_cast_and_crew(movie_id)
    
    if movie_details:
        st.image(fetch_poster(movie_details.get('poster_path')))
        st.header(movie_details.get('title'))
        st.subheader("Overview")
        st.write(movie_details.get('overview'))
        st.subheader("Genre")
        genres = [genre['name'] for genre in movie_details.get('genres', [])]
        st.write(", ".join(genres))
    
    if cast_and_crew:
        st.subheader("Top 2 Actors")
        for actor in cast_and_crew.get('cast', [])[:2]:
            st.image(fetch_poster(actor.get('profile_path')), width=100)
            st.write(actor.get('name'))
        
        st.subheader("Director")
        for crew_member in cast_and_crew.get('crew', []):
            if crew_member.get('job') == 'Director':
                st.image(fetch_poster(crew_member.get('profile_path')), width=100)
                st.write(crew_member.get('name'))
                break

# Load movies and similarity data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
top_n_similarity = pickle.load(open('top_n_similarity.pkl', 'rb'))

# Check if 'poster_path' column exists
if 'poster_path' not in movies.columns:
    logging.error("'poster_path' column not found in the movies DataFrame")

# Initialize session state
if 'view' not in st.session_state:
    st.session_state.view = 'main'
if 'selected_movie_id' not in st.session_state:
    st.session_state.selected_movie_id = None

def show_main_view():
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

    if st.button('Recommend'):
        names, posters, movie_ids = recommend(selected_movie_name, num_recommendations=15)
        
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
                        st.image(posters[index])
                        if st.button(f"Show details {index}", key=f"details_{index}"):
                            st.session_state.view = 'details'
                            st.session_state.selected_movie_id = movie_ids[index]
                            st.experimental_rerun()

def show_details_view():
    display_movie_details(st.session_state.selected_movie_id)
    if st.button('Go Back'):
        st.session_state.view = 'main'
        st.experimental_rerun()

# Display the appropriate view
if st.session_state.view == 'main':
    show_main_view()
elif st.session_state.view == 'details':
    show_details_view()
