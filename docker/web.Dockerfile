FROM node:22-alpine

WORKDIR /app

COPY . /app
RUN corepack enable && pnpm install

CMD ["pnpm", "--filter", "saturn-web", "dev"]
