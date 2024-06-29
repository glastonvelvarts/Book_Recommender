# Book Recommendation Agent

This repository contains a simple Book Recommendation Agent built with FastAPI and Hugging Face's transformers library. The agent fetches book data from the Google Books API and provides book recommendations based on a specified genre.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [License](#license)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/book-recommendation-agent.git
    cd book-recommendation-agent
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Start the FastAPI server:
    ```bash
    uvicorn main:app --reload
    ```

2. Make a POST request to the `/recommend` endpoint with a JSON body containing the genre of the books you want to be recommended.

Example request:
```bash
curl -X POST "http://127.0.0.1:8000/recommend" -H "Content-Type: application/json" -d '{"genre": "fiction"}'
```

Example response:
```json
{
    "recommendation": "We recommend 'The Great Gatsby' for you."
}
```

## API Endpoints

### POST /recommend

Fetches book recommendations based on a specified genre.

**Request Body:**
- `genre` (string): The genre of books to get recommendations for.

**Response:**
- `recommendation` (string): A recommended book title from the specified genre.

## Project Structure

```
book-recommendation-agent/
│
├── main.py                 # Main application file
├── requirements.txt        # Python dependencies
├── README.md               # Project readme file
└── .gitignore              # Git ignore file
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Code Explanation

### main.py

```python
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
```

This code initializes a book recommendation agent, fetches book data from the Google Books API based on a specified genre, filters the top 10 books, selects a random book from these, and provides a recommendation.

## Notes

- Ensure you have a stable internet connection as the application fetches data from an external API.
- The code uses the `distilgpt2` model from Hugging Face, which may require additional setup to download the model weights.
