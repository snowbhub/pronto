import { readFileSync } from "node:fs";
import postgres from "postgres";

if (!process.env.DATABASE_URL) {
  console.log("BOOKING_DB_MIGRATE_SKIPPED: DATABASE_URL is not set");
  process.exit(0);
}
const sql=postgres(process.env.DATABASE_URL,{max:1,connect_timeout:15,prepare:false});
const versions=[
  "0001_core.sql","0002_operacion.sql","0003_endurecer.sql",
  "0004_cierre_de_caja.sql","0005_turnos_fijos.sql",
  "0006_historial.sql","0007_intervalo_de_horarios.sql",
  "0008_vales_y_semana.sql",
  "0009_staff_levels.sql","0010_inventory.sql","0011_staff_accounts.sql","0012_cash_management.sql"
];
try {
  await sql`create table if not exists booking_schema_migrations (
    version text primary key, applied_at timestamptz not null default now()
  )`;
  const prior=await sql`select version from booking_schema_migrations`;
  if (!prior.length) {
    const existing=await sql`select to_regclass('public.appointments') as appointments`;
    if(existing[0].appointments) {
      const check=await sql`select to_regclass('public.staff') as staff, to_regclass('public.services') as services, to_regclass('public.payments') as payments, to_regclass('public.shop_settings') as shop`;
      if(!check[0].staff||!check[0].services||!check[0].payments||!check[0].shop) throw new Error("Incomplete Booking schema");
      const registry=await sql`select to_regclass('supabase_migrations.schema_migrations') as present`;
      if(!registry[0].present) throw new Error("Existing schema has no migration audit");
      const records=await sql`select name from supabase_migrations.schema_migrations where name like 'booking_%'`;
      if(records.length<versions.length) throw new Error("Supabase migrations incomplete");
      for(const version of versions)await sql`insert into booking_schema_migrations(version) values (${version}) on conflict do nothing`;
      console.log("BOOKING_SUPABASE_MIGRATIONS_VERIFIED");
    } else {
    await sql.unsafe("create schema if not exists auth");
    await sql.unsafe("create table if not exists auth.users (id uuid primary key)");
    await sql.unsafe("create or replace function auth.uid() returns uuid language sql stable as $$ select null::uuid $$");
    for (const role of ["anon","authenticated"]) {
      const found=await sql`select 1 from pg_roles where rolname=${role}`;
      if(!found.length) await sql.unsafe("create role "+role);
    }
    }
  }
  const refreshed=await sql`select version from booking_schema_migrations`;
  const done=new Set(refreshed.map(row=>row.version));
  for(const filename of versions){
    if(done.has(filename)) continue;
    const body=readFileSync(new URL("../supabase/migrations/"+filename,import.meta.url),"utf8");
    await sql.begin(async tx=>{
      await tx.unsafe(body);
      await tx`insert into booking_schema_migrations (version) values (${filename})`;
    });
    console.log("BOOKING_MIGRATION_OK",filename);
  }
  const tables=await sql`select to_regclass('public.appointments') as appointments, to_regclass('public.staff') as staff`;
  if(!tables[0].appointments||!tables[0].staff)throw new Error("Core booking tables missing");
  console.log("BOOKING_DB_READY");
} catch(err){
  console.error("BOOKING_DB_MIGRATION_FAILED",err?.message || err);
  process.exitCode=1;
} finally {await sql.end({timeout:5});}
