# Movie Recommender System with Machine Learning

This project implements a movie recommender system using Streamlit, leveraging machine learning techniques to recommend movies based on user selection.

## Overview
The Movie Recommender System allows users to:
- Select a movie from a dropdown menu or by typing its name.
- Receive recommendations of similar movies based on precomputed similarity scores.
- View recommended movies along with their posters fetched from The Movie Database (TMDb) API.

## How It Works
### Data Preparation and Model Training
- The system is pre-trained with a dataset containing movie titles, genres, plot summaries, and user ratings.
- A machine learning model computes similarity scores between movies based on these features.

### Recommendation Process
- When a user selects a movie, the system retrieves precomputed similarity scores to find similar movies.
- It fetches movie posters using real-time API calls to TMDb for visual appeal.

### User Interface
- Users interact with the system through a Streamlit web interface.
- They select a movie from a dropdown menu and click "Recommend" to receive movie suggestions.

## Live Demo
Check out the live demo of the Movie Recommender System [here](https://movie-recommendation-ai.streamlit.app/).
