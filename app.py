import streamlit as st
import pickle
import pandas as pd
import requests

def fetch_poster(movie_id):
    response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id))
    data = response.json()
    poster_path = data['poster_path']
    return "https://image.tmdb.org/t/p/w500/" + poster_path

def recommend(movie, num_recommendations=15):  # Updated to fetch 15 recommendations
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

st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Type or select a movie from the dropdown!',
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name, num_recommendations=15)  # Fetching 15 recommendations
    
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
