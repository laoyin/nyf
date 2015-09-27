# coding=utf-8
import sys,os
reload(sys)
sys.setdefaultencoding('utf-8')
CREATE_TEMPORAL_PARTITION_FUNCTION = \
"""
CREATE OR REPLACE FUNCTION
  public.{0}_partition_function()
RETURNS TRIGGER AS
$BODY$
DECLARE
  _new_time int;
  _tablename text;
  _startdate text;
  _enddate text;
  _result record;
BEGIN
  _tablename := '{0}_'|| to_char(NEW.timestamp, 'YYYYMM');

  -- Check if the partition needed for the current record exists
  PERFORM 1
  FROM   pg_catalog.pg_class c
  JOIN   pg_catalog.pg_namespace n ON n.oid = c.relnamespace
  WHERE  c.relkind = 'r'
  AND    c.relname = _tablename
  AND    n.nspname = 'public';

  -- If the partition needed does not yet exist, then we create it:
  -- Note that || is string concatenation (joining two strings to make one)
  IF NOT FOUND THEN
    _startdate := to_char(NEW.timestamp, 'YYYY-MM-01');
    _enddate := to_char(to_timestamp(_startdate, 'YYYY-MM-DD') + INTERVAL '1 month', 'YYYY-MM-DD');
    EXECUTE 'CREATE TABLE public.' || quote_ident(_tablename) || ' (
      LIKE public.{0} including indexes,
      CHECK ( timestamp >= DATE ' || quote_literal(_startdate) || ' AND timestamp < DATE ' || quote_literal(_enddate) || ')
    ) INHERITS (public.{0})';
  END IF;

  -- Insert the current record into the correct partition, which we are sure will now exist.
  EXECUTE 'INSERT INTO public.' || quote_ident(_tablename) || ' VALUES ($1.*)' USING NEW;
  RETURN NULL;
END;
$BODY$
LANGUAGE plpgsql;
"""

CREATE_INSERT_TRIGGER = \
"""
DROP TRIGGER IF EXISTS {0}_insert_trigger on {0};
CREATE TRIGGER {0}_insert_trigger
BEFORE INSERT ON public.{0}
FOR EACH ROW EXECUTE PROCEDURE public.{0}_partition_function();
"""

DROP_INSERT_TRIGGER = "DROP TRIGGER IF EXISTS {0}_insert_trigger on {0};"

DROP_PARTITION_FUNCTION = "DROP FUNCTION IF EXISTS public.{0}_partition_function();"


if __name__ == "__main__":
    tablename = 'click'
    print CREATE_TEMPORAL_PARTITION_FUNCTION.format(tablename)
    print CREATE_INSERT_TRIGGER.format(tablename)
    print DROP_INSERT_TRIGGER.format(tablename)
    print DROP_PARTITION_FUNCTION.format(tablename)
