-- Isolated fake data for automated visual QA. NEVER apply to production.
BEGIN;
INSERT INTO staff (name, role, commission_pct)
VALUES ('Olena QA','dueno',0),('Max QA','barbero',45),('Danylo QA','barbero',40)
ON CONFLICT DO NOTHING;

INSERT INTO services(name,category,duration_min,price,counts_for_loyalty,sort)
VALUES ('Haircut (scissors + clipper)','corte',60,500,true,1),
       ('Beard trim','barba',30,300,false,2),
       ('Haircut + beard','combo',90,750,true,3);
INSERT INTO clients(name,phone)
VALUES ('Test Client One','+491700000000'),('Test Client Two','+491700000001'),('Test Client Three','+491700000002')
ON CONFLICT(phone) DO NOTHING;
INSERT INTO staff_schedules(staff_id,weekday,start_time,end_time)
SELECT s.id, d.weekday, '09:00'::time, '20:00'::time
FROM staff s CROSS JOIN generate_series(0,6) AS d(weekday)
WHERE s.name LIKE '% QA';

WITH today AS (SELECT (now() AT TIME ZONE 'Europe/Berlin')::date AS d),
records AS (
 SELECT s.id staff_id,c.id client_id,x.id service_id,
 ((today.d+v.start_at) AT TIME ZONE 'Europe/Berlin') starts_at,
 ((today.d+v.end_at) AT TIME ZONE 'Europe/Berlin') ends_at,
 v.status,v.price
 FROM (VALUES
 ('Olena QA','Test Client One','Haircut (scissors + clipper)','10:00'::time,'11:00'::time,'completado',500),
 ('Max QA','Test Client Two','Haircut + beard','11:30'::time,'13:00'::time,'confirmado',750),
 ('Danylo QA','Test Client Three','Beard trim','14:00'::time,'14:30'::time,'pendiente',300),
 ('Max QA','Test Client One','Haircut (scissors + clipper)','16:00'::time,'17:00'::time,'confirmado',500)
 ) AS v(staff,client,service,start_at,end_at,status,price)
 JOIN staff s ON s.name=v.staff
 JOIN clients c ON c.name=v.client
 JOIN services x ON x.name=v.service
 CROSS JOIN today
 )
 INSERT INTO appointments(client_id,staff_id,service_id,starts_at,ends_at,status,source,price)
 SELECT client_id,staff_id,service_id,starts_at,ends_at,status,'panel',price FROM records;

INSERT INTO payments(appointment_id,client_id,staff_id,service_id,concept,kind,list_price,discount,tip,amount,method)
SELECT a.id,a.client_id,a.staff_id,a.service_id,s.name,'servicio',a.price,0,0,a.price,'efectivo'
FROM appointments a JOIN services s ON s.id=a.service_id WHERE a.status='completado';
COMMIT;
