ARG IMAGE=python
ARG VERSION=3.10.11-slim

FROM ${IMAGE}:${VERSION}
ARG USED_MODELS
ARG FILTER_BATCHES
# Set environment variables
ENV PATH="/root/.local/bin:$PATH"
ENV MODELS=${USED_MODELS}
ENV FILTER_BATCHES=${FILTER_BATCHES}

# Copy project files
COPY app /app

WORKDIR /app

RUN apt-get install apt-transport-https \
    && echo "deb https://notesalexp.org/tesseract-ocr5/bullseye/ bullseye main" \
    | tee /etc/apt/sources.list.d/notesalexp.list > /dev/null \
    && apt-get update -y -oAcquire::AllowInsecureRepositories=true \
    && apt-get install -y --allow-unauthenticated notesalexp-keyring -oAcquire::AllowInsecureRepositories=true \
    && apt-get update -y \
    && apt-get install -y tesseract-ocr

# Install pipx
RUN pip install --no-cache-dir pipx \
    && pipx ensurepath \
    && pipx install poetry

# Install project dependencies
RUN poetry install

CMD ["poetry", "run", "python", "-m", "scripts.main"]
