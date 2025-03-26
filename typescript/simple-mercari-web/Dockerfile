FROM node:20-alpine

RUN addgroup -S mercari && adduser -S trainee -G mercari

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm ci

COPY . .

RUN chown -R trainee:mercari /app

USER trainee

EXPOSE 3000

CMD ["npm", "run", "start"]