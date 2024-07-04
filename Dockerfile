# Stage 1: Build Stage
FROM python:3.8-alpine as builder

# Install dependencies necessary for compilation
RUN apk add --no-cache gcc musl-dev libffi-dev

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Set working directory
WORKDIR /app

# Copy only the Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies with pipenv
RUN pipenv install --deploy --ignore-pipfile

# Stage 2: Production Stage
FROM python:3.8-alpine

# Copy pipenv and its dependencies from the builder stage
COPY --from=builder /usr/local /usr/local

# Set working directory
WORKDIR /app

# Copy the rest of the application files
COPY . .

# Add local binaries to PATH
ENV PATH=/usr/local/bin:$PATH

# Set Python path explicitly
ENV PYTHONPATH=/usr/local/lib/python3.8/site-packages

# Run command
CMD ["pipenv", "run", "start"]