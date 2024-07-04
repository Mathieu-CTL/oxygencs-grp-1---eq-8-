# Stage 1: Build stage
FROM python:3.8-alpine as builder

# Install dependencies needed for compilation
RUN apk add --no-cache gcc musl-dev libffi-dev

# Install pipenv
RUN pip install --no-cache-dir pipenv

WORKDIR /app

# Copy Pipfile and Pipfile.lock to install dependencies
COPY Pipfile Pipfile.lock ./

# Install dependencies with pipenv
RUN pipenv install --deploy --ignore-pipfile

# Stage 2: Production stage
FROM python:3.8-alpine

# Install pipenv in the final image
RUN pip install --no-cache-dir pipenv

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /root/.local /root/.local

# Copy application files
COPY . .

RUN pip install --no-cache-dir pytz

# Add local binaries folder to PATH
ENV PATH=/root/.local/bin:$PATH

CMD ["pipenv", "run", "start"]