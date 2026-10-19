ALTER TABLE shop_settings
  ADD COLUMN IF NOT EXISTS currency_code text NOT NULL DEFAULT 'ARS';

DO $$ BEGIN
  ALTER TABLE shop_settings
    ADD CONSTRAINT shop_settings_currency_code_check
    CHECK (currency_code IN ('EUR', 'UAH', 'USD', 'ARS'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
