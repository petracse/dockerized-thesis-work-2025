FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Budapest

# Alap rendszer csomagok és Python 3.12 telepítése
RUN apt-get update && \
    apt-get install -y tzdata software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.12 python3.12-venv python3.12-dev \
        git build-essential ffmpeg libsndfile1 && \
    ln -s /usr/bin/python3.12 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Virtuális környezet létrehozása
RUN python3.12 -m venv /opt/venv

# Aktiváld a virtuális környezetet minden további RUN, CMD, ENTRYPOINT parancshoz
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

# pip és setuptools frissítése, majd csomagok telepítése
RUN pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
