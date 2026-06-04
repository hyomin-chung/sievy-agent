FROM node:24-slim

WORKDIR /app

RUN npm install -g pnpm
RUN pnpm config set store-dir /pnpm-store

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

CMD ["pnpm", "dev", "--host"]