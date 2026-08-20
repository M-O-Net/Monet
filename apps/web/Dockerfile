# Build context is the monorepo root (see docker-compose.yml) — pnpm workspaces need the
# root lockfile alongside every package.json to install correctly.

FROM node:26-alpine AS deps
WORKDIR /app
RUN npm install -g corepack && corepack enable
COPY package.json pnpm-workspace.yaml pnpm-lock.yaml* ./
COPY apps/web/package.json apps/web/package.json
COPY packages/api-client/package.json packages/api-client/package.json
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# Runs the Vite dev server against bind-mounted source (see docker-compose.dev.yml) — deps
# installed here are what survive under the anonymous-volume node_modules masks, so a dev
# container never reinstalls on every start, only on `up --build` after a dependency bump.
FROM deps AS dev
WORKDIR /app/apps/web
EXPOSE 5173
CMD ["pnpm", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

FROM deps AS final
COPY packages/api-client packages/api-client
COPY apps/web apps/web
WORKDIR /app/apps/web
RUN pnpm run build

FROM nginx:1.30-alpine AS serve
COPY --from=final /app/apps/web/dist /usr/share/nginx/html
EXPOSE 80
