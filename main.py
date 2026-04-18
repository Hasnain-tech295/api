from fastapi import FastAPI, HTTPException
from schemas import BookCreate, BookResponse

app = FastAPI()

books_db: dict[int, dict] = {
    1: {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925},
    2: {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee", "year": 1960},
    3: {"id": 3, "title": "1984", "author": "George Orwell", "year": 1949},
}

@app.get("/books", response_model=list[BookResponse])
def get_books():
    return list(books_db.values())

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail=f"Book with id={book_id} not found")
    return books_db[book_id]

@app.post("/books", status_code=201, response_model=BookResponse)
def create_book(book: BookCreate):
    new_id = max(books_db.keys()) + 1 if books_db else 1
    books_db[new_id] = {**book.model_dump(), "id": new_id}
    return books_db[new_id]

@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail=f"Book with id={book_id} not found")
    del books_db[book_id]
    return None