FROM node:24-slim

WORKDIR /app

RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install

COPY . .

CMD ["pnpm", "dev", "--host"]