FROM node:20-bullseye

# Installer git, Python, gcc/g++, make, et bluez pour le BLE
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    make \
    g++ \
    bluetooth \
    bluez \
    libbluetooth-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package*.json ./

RUN npm install --production

COPY src ./src

ENV NODE_ENV=production

CMD ["npm", "start"]
