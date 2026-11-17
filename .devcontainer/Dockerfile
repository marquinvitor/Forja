FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jdk kotlin git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
