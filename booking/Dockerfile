FROM node:22-bookworm AS build
WORKDIR /app

RUN apt-get update \\
  && apt-get install -y --no-install-recommends git ca-certificates python3 \\
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/operonhub/virex-barbershop.git . \\
  && git checkout b5433b62213f88223c868cca279364d524546336

COPY . /booking
RUN python3 /booking/patch.py
RUN npm ci
RUN npm run build

FROM node:22-bookworm-slim
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app /app
EXPOSE 3000
CMD ["npm", "start"]
