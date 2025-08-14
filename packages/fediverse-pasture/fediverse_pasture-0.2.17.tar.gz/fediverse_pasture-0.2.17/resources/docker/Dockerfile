FROM python:3.13-alpine
RUN apk add build-base

ARG tag=0.2.15
RUN --mount=type=cache,target=/root/.cache/  pip install fediverse-pasture==${tag}

COPY sha.patch .
RUN patch usr/local/lib/python3.13/site-packages/bovine/crypto/helper.py sha.patch