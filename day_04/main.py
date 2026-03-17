from fastapi import FastAPI, HTTPException, Depends
from typing import Optional

from models import BookCreate, BookResponse, BookUpdate
from exceptions import (
    BookNotFoundError,
    DuplicateISBNError,
    register_exception_handlers
)
from middleware import RequestContextMiddleware

from dependencies import (
    PaginationParam, get_pagination,
    FakeDB, get_db,
    CurrentUser, get_current_user, require_admin,
    BookFilters, get_book_filters,
    _books_store, _next_id
)

app = FastAPI(
    title="Book Inventory API",
    version="0.3.0",
    description="Production-style error handling demo",
)

app.add_middleware(RequestContextMiddleware)
register_exception_handlers(app)

# ---------------------------------------------------------------
# Notice how clean the route signatures are now.
# No Query(...) boilerplate repeated everywhere.
# No auth logic inside the handler.
# The handler only does one thing: its actual job.
# ---------------------------------------------------------------

@app.get("/books", response_model=list[BookResponse])
def list_books(
    pagination: PaginationParam = Depends(get_pagination),
    filters: BookFilters = Depends(get_book_filters),
    db: FakeDB = Depends(get_db)
    # No auth required on this route — public endpoint
): 
    """
    List books with optional filtering and pagination.
    - No auth required (public endpoint)
    - Dependencies handle pagination, filtering, and DB connection
    - Clean, focused handler that only implements business logic
    """
    # 1. Apply filters
    filtered_books = list(db.store.values())
    if filters.author:
        filtered_books = [b for b in filtered_books if b["author"] == filters.author]
    if filters.min_year:
        filtered_books = [b for b in filtered_books if b["year"] >= filters.min_year]
    if filters.max_year:
        filtered_books = [b for b in filtered_books if b["year"] <= filters.max_year]

    # 2. Apply pagination
    start = pagination.offset
    end = start + pagination.limit
    paginated_books = filtered_books[start:end]

    # 3. Return response models
    return [BookResponse(**b) for b in paginated_books]


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    db: FakeDB = Depends(get_db)
    # Public route - no auth required
):
    """
    Get a single book by ID.
    - No auth required (public endpoint)
    - Dependency handles DB connection
    - Clean, focused handler that only implements business logic
    """
    book = db.store.get(book_id)
    if not book:
        raise BookNotFoundError(book_id)
    return BookResponse(**book)

@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(
    book: BookCreate,
    db: FakeDB = Depends(get_db),
    current_user: CurrentUser = Depends(require_admin)
):
    """
    Create a new book.
    - Requires admin role (auth handled by dependency)
    - Dependency handles DB connection
    - Clean, focused handler that only implements business logic
    """
    global _next_id
    
    # Check for duplicate ISBN
    if book.isbn:
        existing = [b for b in db.store.values() if b.get("isbn") == book.isbn]
        if existing:
            raise DuplicateISBNError(book.isbn)
    
    new_book = {"id": _next_id, **book.model_dump()}
    db.store[_next_id] = new_book
    _next_id += 1
    return BookResponse(**new_book)

@app.delete("/books/{book_id}", status_code=204)
def delete_book(
    book_id: int,
    db: FakeDB = Depends(get_db),
    current_user: CurrentUser = Depends(require_admin)
):
    """
    Delete a book by ID.
    - Requires admin role (auth handled by dependency)
    - Dependency handles DB connection
    - Clean, focused handler that only implements business logic
    """
    if book_id not in db.store:
        raise BookNotFoundError(book_id)
    del db.store[book_id]


@app.get("/me", response_model=dict)
def get_me(current_user: CurrentUser = Depends(get_current_user)):
    """
    Get current user info.
    - Requires authentication (auth handled by dependency)
    - Clean, focused handler that only implements business logic
    """
    return {
        "user_id": current_user.user_id,
        "name": current_user.name,
        "role": current_user.role
    }


@app.get("/health")
def get_health():
    return {"status": "ok"}