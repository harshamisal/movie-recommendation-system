import streamlit as st
import pickle
import requests

# Function to fetch movie poster from TMDB API with caching
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    api_key = "d204c9450af52ddb03a15ca8e00c663c"  # Replace with your actual API key
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750.png?text=No+Image"

    except requests.exceptions.RequestException as e:
        print("Error fetching poster:", e)
        return "https://via.placeholder.com/500x750.png?text=No+Image"


# Function to recommend movies
def recommend(movie, movies_list, similarity):
    movie_index = movies_list[movies_list['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_indices:
        movie_id = movies_list.iloc[i[0]].id  # Ensure your DataFrame has 'id' column
        recommended_movies.append(movies_list.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))  # Cached function

    return recommended_movies, recommended_posters


# Load data
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies_list = pickle.load(open('movies.pkl', 'rb'))  # DataFrame with 'title' & 'id'

# Streamlit UI
st.title('Movie Recommendation System')

selected_movie_name = st.selectbox(
    "Select a movie:", movies_list['title'].values
)

st.write("You selected:", selected_movie_name)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name, movies_list, similarity)

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(names[idx])
            st.image(posters[idx])
