CREATE OR REPLACE FUNCTION update_t()
  RETURNS void AS
$BODY$declare
  line record;
  count integer;
begin
count := 0;
for line in
  select a from t order by a
loop
  count := count + 1;
  update t
    set b = count
    where a = line.a
    ;
end loop;

return;
end;$BODY$
LANGUAGE 'plpgsql' VOLATILE STRICT;
