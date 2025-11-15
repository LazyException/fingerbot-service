FROM node:20-alpine

# Installer git pour permettre à npm de récupérer les dépendances depuis GitHub
RUN apk add --no-cache git

WORKDIR /app

COPY package*.json ./
RUN npm install --production

COPY src ./src

ENV NODE_ENV=production

CMD ["npm", "start"]
