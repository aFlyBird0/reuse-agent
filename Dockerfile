#fixme
# 用于构建虚拟环境的构建器镜像
FROM python:3.11-buster as builder

RUN apt-get update && apt-get install -y git

ENV POETRY_NO_INTERACTION=1 \
POETRY_VIRTUALENVS_IN_PROJECT=1 \
POETRY_VIRTUALENVS_CREATE=1 \
POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install poetry

ENV HOST=0.0.0.0
ENV LISTEN_PORT 8080
EXPOSE 8080

WORKDIR /app

#COPY pyproject.toml ./app/pyproject.toml
#COPY poetry.lock ./app/poetry.lock
COPY pyproject.toml poetry.lock ./

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

# 用于仅运行提供的代码及其虚拟环境的运行时镜像
FROM python:3.11-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY . /app
#COPY ./.streamlit ./.streamlit

CMD ["streamlit", "run", "🏠_home.py", "--server.port", "8080"]