FROM node:22-alpine

WORKDIR /app

COPY . /app

CMD ["pnpm", "--filter", "saturn-web", "dev"]
