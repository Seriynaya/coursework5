# Coursework 5 — Blog/Content Management

C++ implementation of a blog content management system inspired by the Django project.

## Algorithms & Complexity

| Operation | Time | Method |
|---|---|---|
| Filter by tag | O(n * t) | set membership per post |
| Filter by tag intersection | O(n * t * q) | subset check |
| Top-K by views | O(n log K) | partial_sort |
| Full-text search (KMP) | O(n + m) per post | KMP failure function |
| Tag frequency map | O(n * t) | unordered_map counting |

## Build & Run

```bash
g++ -std=c++17 -O2 -o coursework5 main.cpp
./coursework5
```

## Description

- Post struct with id, author, title, content, tags, views, and creation time
- Tag-based filtering with set intersection
- Top-K posts by view count using partial_sort
- KMP pattern matching for full-text search across post content
- Tag frequency analysis via hash map
