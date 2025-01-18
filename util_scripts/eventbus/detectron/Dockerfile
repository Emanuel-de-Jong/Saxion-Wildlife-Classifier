FROM python:3.10.11-slim

# Set environment variables
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY scripts /app/scripts
COPY pyproject.toml poetry.lock /app/

WORKDIR /app

# Install pipx
RUN pip install --no-cache-dir pipx \
    && pipx ensurepath

# Install Poetry
RUN pipx install poetry

# Install project dependencies
RUN poetry install

CMD ["poetry", "run", "python", "-m", "scripts.main"]
