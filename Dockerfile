FROM python:3.13-slim AS builder

# prevents Python from generating .pyc or .pyo files. Saves space.
ENV PYTHONDONTWRITEBYTECODE=1
# disables output buffering, enabling realtime logging.
ENV PYTHONBUFFERED=1
# prevents pip from storing downloaded packages in a cache directory.
ENV PIP_NO_CACHE_DIR=1

# Sets directory in the container where the source will reside.
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copies the requirements file to the container to make use of Docker cache.
COPY requirements.txt .

# Create a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Run stage
FROM python:3.13-slim

# create dedicated user
RUN addgroup --system --gid 1001 appuser && \
    adduser --system --uid 1001 --ingroup appuser appuser

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY . .

# set path to be the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# set user to be appuser
USER appuser

CMD ["python", "-m", "src.main"]



