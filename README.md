# Feddit Sentiment Microsite

A Python microservice for performing sentiment analysis on comments from the Feddit API.

## 🚀 Features

* Fetches comments from a topic on the Feddit API.
* Performs sentiment analysis using VADER.
* Filters comments by date range.
* Sorts results by polarity score (ascending or descending).
* Built with FastAPI and deployable via Poetry.
* Automated tests with Pytest.
* Code linting with ruff and pre-commit hooks.
* GitHub Actions for automated CI (linting + testing).


## 📦 Requirements

* Python >= 3.10
* Poetry
* Docker (for running the Feddit API locally)

## 🛠 Installation

```bash
poetry install
```

## 📥 Example Usage

1. **Start the Feddit API using Docker**:

```bash
docker compose -f <path-to-docker-compose.yml> up -d
```

Visit: [http://0.0.0.0:8080](http://0.0.0.0:8080)

2. **Start the microservice**:

```bash
poetry run uvicorn app.main:app
```

Make sure to run this command from the root directory of the project (where the `app/` folder is located).


The API will be available at `http://localhost:8000`

3. **Send a request**:

```bash
curl "http://localhost:8000/comments/Dummy%20Topic%201?limit=10&start=2021-06-01T00:00:00Z&end=2022-06-01T00:00:00Z&sort_by_polarity_score=desc"
```

You can also paste the URL directly into your browser.

## 🔍 Endpoint

### `GET /comments/{topic}`

**Query Parameters**

* `limit`: Maximum number of comments to return
* `start`: ISO timestamp to filter from (optional)
* `end`: ISO timestamp to filter to (optional)
* `sort_by_polarity_score`: `asc` or `desc` (optional)

**Available Subfeddits**

The Feddit API includes the following predefined subfeddits (topics):
* Dummy Topic 1
* Dummy Topic 2
* Dummy Topic 3

When using them in URLs (e.g. via curl or browser), make sure to encode spaces as '%20'. For example:

```bash
curl "http://localhost:8000/comments/Dummy%20Topic%201"
```

### 🧾 Example Response

```json
[
  {
    "id": 123,
    "text": "I love this!",
    "polarity": 0.8,
    "classification": "positive"
  },
  {
    "id": 124,
    "text": "This is terrible.",
    "polarity": -0.6,
    "classification": "negative"
  }
]
```

## 📂 Project structure

```
feddit-sentiment-api/
├── app/
│   ├── main.py             # FastAPI app entrypoint
│   ├── feddit_client.py    # Client to fetch comments from Feddit
│   ├── sentiment.py        # Sentiment analysis logic using VADER
│   └── models.py           # Data models (if applicable)
├── tests/                  # Pytest-based test suite
├── .github/workflows/ci.yml # GitHub Actions workflow for linting and testing
├── pyproject.toml          # Poetry project configuration
└── README.md
```

## 🧱 Tech Stack

**Language & Framework**
- Python 3.10+
- FastAPI – for building the RESTful API

**Sentiment Analysis**
- VADER Sentiment (via `nltk.sentiment`)

**Dependency Management**
- Poetry – for managing dependencies and packaging

**Testing & Linting**
- Pytest – unit testing framework
- Ruff – fast Python linter
- pre-commit – git hooks for enforcing code style

**Continuous Integration**
- GitHub Actions – run tests and linting automatically on each push

**Dev Tools**
- Docker – to run the Feddit API locally

## 🤝 Contributing

Feel free to submit issues or pull requests. For major changes, please open an issue first.

## 📄 License

MIT

---

Created by Mateu Busquets
