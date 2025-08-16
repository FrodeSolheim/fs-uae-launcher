# syntax=docker/dockerfile:1.16
FROM python:3.13-alpine3.22@sha256:a70b35b575e33d951e3f9d3fe94163ef0fd338c22552bc587a1b098a87ed6184 AS base

ENV PLAYERS=2
ENV PASSWORD=""

RUN adduser fs-uae -u 101 -h /fs-uae -D
COPY launcher/server/game.py /fs-uae/game.py
COPY launcher/server/entrypoint.sh /entrypoint.sh
RUN iconv -f UTF-16 -t UTF-8 /fs-uae/game.py
WORKDIR /fs-uae
ENTRYPOINT ["/entrypoint.sh"]
USER 101
EXPOSE 25101