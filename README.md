# Potpie Assignment
## Setup

### Prerequisites

- Python 3.8 or higher
- Celery
- Redis (for Celery backend)
- Azure Chat OpenAI API

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Mihan786Chistie/potpie-assignment.git
    cd potpie-assignment
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Start Redis server (for task queue):

    ```bash
    redis-server
    ```

4. Set up the environment variables (see below).

    ```bash
    docker run -d -p 6379:6379 redis
    ```

5. Run the Celery worker:

    ```bash
    celery -A app.core.celery_app worker --loglevel=info
    ```

6. Start your main script:

    ```bash
    uvicorn app.main:app --reload
    ```
