FROM ghcr.io/owl-corp/python-poetry-base:3.12-slim

# Override the base image's env
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

WORKDIR /client
COPY pyproject.toml poetry.lock ./
# TODO: Exclude development dependencies
RUN --mount=type=cache,target=${POETRY_CACHE_DIR} poetry install --no-root
RUN poetry install --no-root

COPY ./ ./

ENTRYPOINT ["poetry", "run"]
CMD ["python", "-m", "client"]
