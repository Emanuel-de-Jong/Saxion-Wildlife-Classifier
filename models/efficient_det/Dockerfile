ARG IMAGE=python
ARG VERSION=3.10.11-slim

# Final image
FROM ${IMAGE}:${VERSION}
ARG USE
COPY app /app
WORKDIR /app
ENV PATH="/root/.local/bin:$PATH"

RUN if [ "$USE" = "GPU" ]; then \
        apt-get update && \
        apt-get install -y python3.10-venv python3-pip && \
        apt-get clean && rm -rf /var/lib/apt/lists/*; \
    fi

RUN pip install --no-cache-dir pipx \
    && pipx ensurepath \
    && pipx install poetry

RUN poetry install

CMD ["poetry", "run", "python", "-m", "scripts.main"]
