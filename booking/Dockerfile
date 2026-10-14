FROM node:22-bookworm AS build
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates python3 && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/operonhub/virex-barbershop.git . && git checkout b5433b62213f88223c868cca279364d524546336
COPY patch /tmp/booking-patch
RUN python3 /tmp/booking-patch/main.py
RUN python3 /tmp/booking-patch/finalize.py
RUN python3 /tmp/booking-patch/cleanup.py
RUN python3 /tmp/booking-patch/demo_cleanup.py
RUN python3 /tmp/booking-patch/brand_cleanup.py
RUN python3 /tmp/booking-patch/comment_cleanup.py
RUN python3 /tmp/booking-patch/source_finalize.py
RUN python3 /tmp/booking-patch/final_audit.py
RUN python3 /tmp/booking-patch/ui_final.py
RUN python3 /tmp/booking-patch/modern-ui.py
RUN python3 /tmp/booking-patch/payroll-discovery.py
RUN python3 /tmp/booking-patch/timezone-i18n.py
RUN python3 /tmp/booking-patch/i18n-runtime.py
RUN python3 /tmp/booking-patch/mobile-polish.py
RUN python3 /tmp/booking-patch/app-mobile-shell.py
RUN python3 /tmp/booking-patch/inventory-install.py
RUN python3 /tmp/booking-patch/ranks-install.py
RUN python3 /tmp/booking-patch/staff-install.py
RUN python3 /tmp/booking-patch/payroll-install.py
RUN python3 /tmp/booking-patch/analytics-install.py
RUN python3 /tmp/booking-patch/ai-setup.py
RUN python3 /tmp/booking-patch/mixed-ui-copy.py
RUN python3 /tmp/booking-patch/verify_i18n.py
RUN cp /tmp/booking-patch/migrate-booking.mjs /app/scripts/migrate-booking.mjs
RUN npm ci
RUN python3 /tmp/booking-patch/test-compat.py
RUN npm run test:db
RUN NEXT_PUBLIC_BOOKING_TIME_ZONE=America/Argentina/Buenos_Aires npm test
RUN npm run build

FROM node:22-bookworm-slim
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app /app
EXPOSE 3000
CMD ["sh","-c","node scripts/migrate-booking.mjs && npm start"]
