# Booking / Termin / Запис

Phase 1 rebrand layer for the MIT-licensed upstream codebase.

- Canonical source UI: English
- Supported presentation locales: English, German, Ukrainian
- Localized product name: Booking / Termin / Запис
- Neutral monochrome visual system
- Dark and light themes
- No business workflows changed in this phase

## Localization architecture

Runtime strings are generated into `src/i18n/messages.ts`. The exported `t(value, locale)` / `translateText(value, locale)` functions are the canonical translation API for new UI code. `LocaleBridge` remains as a compatibility layer for legacy upstream components and dynamically inserted UI text.

Translation rows live in `booking/patch/rows*.json` as:

```json
["source-or-legacy-text", "English", "Deutsch", "Українська"]
```

When adding new product copy, write the source UI in English and add one translation row. To add another language later, extend the `Locale` type, add the new value to the catalog rows, and add it to the language selector. Dynamic messages that contain values should use `t()` or an explicit dynamic translation pattern rather than hardcoded language-specific concatenation.

Internal compatibility identifiers such as existing database enum values, API field names and routes may remain in their original technical form. They are not presentation copy and must not be renamed during translation-only changes.

The Railway image pins the upstream source commit and applies this branch’s rebrand/i18n layer during build. The original `main` branch of this repository is untouched.
