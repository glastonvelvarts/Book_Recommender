import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import random

class BookRecommendationAgent:
    def __init__(self):
        try:
            self.llm = pipeline("text-generation", model="distilgpt2")
        except Exception as e:
            print(f"Error initializing model: {e}")
            raise HTTPException(status_code=500, detail="Error initializing the model.")
        self.top_100_books = []
        self.top_10_books = []
        self.selected_book = None

    def fetch_top_100_books(self, genre):
        url = f"https://www.googleapis.com/books/v1/volumes?q=subject:{genre}&maxResults=40"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            self.top_100_books = data['items'][:100]
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch books from Google Books API.")

    def filter_top_10_books(self):
        self.top_10_books = self.top_100_books[:10]

    def select_top_book(self):
        if self.top_10_books:
            self.selected_book = random.choice(self.top_10_books)

    def get_recommendation(self):
        if self.selected_book:
            return f"We recommend '{self.selected_book['volumeInfo']['title']}' for you."
        else:
            return "Sorry, we couldn't find a book in this genre."

app = FastAPI()
agent = BookRecommendationAgent()

class GenreRequest(BaseModel):
    genre: str

@app.post("/recommend")
def recommend_book(request: GenreRequest):
    try:
        agent.fetch_top_100_books(request.genre)
        agent.filter_top_10_books()
        agent.select_top_book()
        recommendation = agent.get_recommendation()
        return {"recommendation": recommendation}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred.")
