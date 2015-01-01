create or replace function subteam_group_name (in name text, in pattern text)
returns text as $$
begin
	if name ~ pattern then
	  return substring(upper(name) from pattern);
	else
	  return name;
	end if;
end;
$$
language 'plpgsql' immutable strict;
