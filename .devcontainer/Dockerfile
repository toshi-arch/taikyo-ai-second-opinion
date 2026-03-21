# Microsoftが提供するPython開発用公式イメージ（Python 3.11）
FROM mcr.microsoft.com/vscode/devcontainers/python:3.11

# 環境変数の設定
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# 必要に応じてOSレベルのパッケージをインストール（現在は最小限）
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# requirements.txt は devcontainer.json の postCreateCommand でインストールされるため
# ここでは COPY しません（ローカルファイルを直接マウントして利用するため）