FROM ghcr.io/owl-corp/python-poetry-base:3.12-slim

# Override the base image's env
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN groupadd --gid 1300 disc-msg-store \
 && useradd --uid 1300 --gid 1300 --no-create-home disc-msg-store

WORKDIR /client
COPY pyproject.toml poetry.lock ./
# TODO: Exclude development dependencies
RUN --mount=type=cache,target=${POETRY_CACHE_DIR} poetry install --no-root
RUN poetry install --no-root

COPY ./ ./

USER disc-msg-store

ENTRYPOINT ["poetry", "run"]
CMD ["python", "-m", "client"]
