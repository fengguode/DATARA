"""Fixed PostgreSQL 17 diagnostic collector. No adoption operation."""
import json
QUERIES = json.loads(r'''{"catalog_01":"SELECT current_database() AS database, session_user, current_user,\n current_setting('server_version_num') AS server_version_num,\n version() AS server_build, current_setting('transaction_read_only') AS read_only,\n current_setting('transaction_isolation') AS isolation,\n current_setting('search_path') AS search_path,\n current_setting('row_security') AS row_security,\n pg_is_in_recovery() AS recovery, pg_current_snapshot()::text AS snapshot","catalog_02":"SELECT datname, pg_encoding_to_char(encoding) AS encoding, datlocprovider,\n datcollate, datctype, datlocale, daticurules, datcollversion,\n pg_database_collation_actual_version(oid) AS actual_collversion\nFROM pg_database WHERE datname = current_database()","catalog_03":"SELECT nspname,pg_get_userbyid(nspowner) AS owner,nspacl\nFROM pg_namespace\nWHERE nspname NOT IN ('pg_catalog','information_schema')\n AND nspname NOT LIKE 'pg_toast%' AND nspname NOT LIKE 'pg_temp%'\nORDER BY nspname","catalog_04":"SELECT n.nspname, c.relname, c.relkind, c.relpersistence,\n c.relispartition, c.relrowsecurity, c.relforcerowsecurity,\n pg_get_userbyid(c.relowner) AS owner, c.reloptions, c.relacl,\n am.amname AS access_method, ts.spcname AS tablespace,\n pg_get_partkeydef(c.oid) AS partition_key,\n pg_get_expr(c.relpartbound,c.oid,false) AS partition_bound\nFROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace\nLEFT JOIN pg_am am ON am.oid=c.relam\nLEFT JOIN pg_tablespace ts ON ts.oid=c.reltablespace\nWHERE n.nspname NOT IN ('pg_catalog','information_schema')\n AND n.nspname NOT LIKE 'pg_toast%' AND n.nspname NOT LIKE 'pg_temp%'\nORDER BY n.nspname,c.relname","catalog_05":"SELECT n.nspname,c.relname,a.attnum,a.attname,a.attisdropped,\n tn.nspname AS type_schema,t.typname,format_type(a.atttypid,a.atttypmod) AS type,\n a.attndims,a.attnotnull,a.attidentity,a.attgenerated,\n cn.nspname AS collation_schema,co.collname,co.collprovider,co.collisdeterministic,\n co.collencoding,co.collcollate,co.collctype,co.colllocale,co.collicurules,co.collversion,\n pg_collation_actual_version(co.oid) AS actual_collation_version,\n pg_get_expr(d.adbin,d.adrelid,false) AS default_expression,\n a.attstorage,a.attcompression,a.attoptions\nFROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid\nJOIN pg_namespace n ON n.oid=c.relnamespace\nLEFT JOIN pg_type t ON t.oid=a.atttypid LEFT JOIN pg_namespace tn ON tn.oid=t.typnamespace\nLEFT JOIN pg_attrdef d ON d.adrelid=a.attrelid AND d.adnum=a.attnum\nLEFT JOIN pg_collation co ON co.oid=a.attcollation\nLEFT JOIN pg_namespace cn ON cn.oid=co.collnamespace\nWHERE a.attnum>0 AND a.attrelid = ANY(%(relations)s::regclass[])\nORDER BY n.nspname,c.relname,a.attnum","catalog_06":"SELECT n.nspname,c.relname,k.conname,k.contype,k.condeferrable,k.condeferred,\n k.convalidated,k.conislocal,k.coninhcount,k.connoinherit,\n ARRAY(SELECT a.attname FROM unnest(k.conkey) WITH ORDINALITY x(num,ord)\n       JOIN pg_attribute a ON a.attrelid=k.conrelid AND a.attnum=x.num ORDER BY x.ord) AS columns,\n rn.nspname AS target_schema,rc.relname AS target_table,\n ARRAY(SELECT a.attname FROM unnest(k.confkey) WITH ORDINALITY x(num,ord)\n       JOIN pg_attribute a ON a.attrelid=k.confrelid AND a.attnum=x.num ORDER BY x.ord) AS target_columns,\n k.confupdtype,k.confdeltype,k.confmatchtype,\n pg_get_constraintdef(k.oid,false) AS definition,\n CASE WHEN k.conindid<>0 THEN k.conindid::regclass::text END AS backing_index\nFROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid\nJOIN pg_namespace n ON n.oid=c.relnamespace\nLEFT JOIN pg_class rc ON rc.oid=k.confrelid\nLEFT JOIN pg_namespace rn ON rn.oid=rc.relnamespace\nWHERE k.conrelid=ANY(%(relations)s::regclass[]) OR k.confrelid=ANY(%(relations)s::regclass[])\nORDER BY n.nspname,c.relname,k.contype,k.conname","catalog_07":"SELECT n.nspname,t.relname,ix.relname AS index_name,am.amname,\n i.indisunique,i.indnullsnotdistinct,i.indisprimary,i.indisexclusion,\n i.indimmediate,i.indisvalid,i.indisready,i.indislive,i.indisreplident,\n i.indnkeyatts,i.indnatts,\n ARRAY(SELECT pg_get_indexdef(i.indexrelid,p,false)\n       FROM generate_series(1,i.indnatts) p ORDER BY p) AS keys_and_include,\n pg_get_expr(i.indexprs,i.indrelid,false) AS expressions,\n pg_get_expr(i.indpred,i.indrelid,false) AS predicate,\n pg_get_indexdef(i.indexrelid,0,false) AS full_definition,\n ix.reloptions,ts.spcname AS tablespace\nFROM pg_index i JOIN pg_class t ON t.oid=i.indrelid\nJOIN pg_namespace n ON n.oid=t.relnamespace\nJOIN pg_class ix ON ix.oid=i.indexrelid JOIN pg_am am ON am.oid=ix.relam\nLEFT JOIN pg_tablespace ts ON ts.oid=ix.reltablespace\nWHERE i.indrelid=ANY(%(relations)s::regclass[])\nORDER BY n.nspname,t.relname,ix.relname","catalog_08":"SELECT n.nspname,c.relname,format_type(s.seqtypid,NULL) AS type,\n s.seqstart,s.seqincrement,s.seqmax,s.seqmin,s.seqcache,s.seqcycle,\n pg_get_userbyid(c.relowner) AS owner,c.relacl,\n d.deptype,tn.nspname AS table_schema,t.relname AS table_name,a.attname AS column_name\nFROM pg_sequence s JOIN pg_class c ON c.oid=s.seqrelid\nJOIN pg_namespace n ON n.oid=c.relnamespace\nLEFT JOIN pg_depend d ON d.classid='pg_class'::regclass AND d.objid=c.oid\n AND d.refclassid='pg_class'::regclass AND d.deptype IN ('a','i')\nLEFT JOIN pg_class t ON t.oid=d.refobjid\nLEFT JOIN pg_namespace tn ON tn.oid=t.relnamespace\nLEFT JOIN pg_attribute a ON a.attrelid=t.oid AND a.attnum=d.refobjsubid\nWHERE n.nspname=ANY(%(schemas)s::text[]) OR t.oid=ANY(%(relations)s::regclass[])\nORDER BY n.nspname,c.relname,tn.nspname,t.relname,a.attnum","catalog_09":"SELECT tg.tgrelid::regclass::text AS relation,tg.tgname,tg.tgenabled,\n tg.tgisinternal,pg_get_triggerdef(tg.oid,false) AS definition\nFROM pg_trigger tg WHERE tg.tgrelid=ANY(%(relations)s::regclass[]) ORDER BY 1,2","catalog_10":"SELECT polrelid::regclass::text AS relation,polname,polcmd,polpermissive,\n ARRAY(SELECT CASE WHEN x=0 THEN 'PUBLIC' ELSE pg_get_userbyid(x) END\n       FROM unnest(polroles) x ORDER BY x) AS roles,\n pg_get_expr(polqual,polrelid,false) AS using_expression,\n pg_get_expr(polwithcheck,polrelid,false) AS check_expression\nFROM pg_policy WHERE polrelid=ANY(%(relations)s::regclass[]) ORDER BY 1,2","catalog_11":"SELECT ev_class::regclass::text AS relation,rulename,pg_get_ruledef(oid,false) AS definition\nFROM pg_rewrite WHERE ev_class=ANY(%(relations)s::regclass[]) ORDER BY 1,2","catalog_12":"SELECT e.extname,e.extversion,d.classid::regclass::text AS object_catalog,\n pg_describe_object(d.classid,d.objid,d.objsubid) AS object\nFROM pg_depend d JOIN pg_extension e ON e.oid=d.refobjid\nWHERE d.refclassid='pg_extension'::regclass AND d.deptype='e'\n AND d.classid='pg_class'::regclass AND d.objid=ANY(%(relations)s::regclass[])\nORDER BY 1,3","catalog_13":"SELECT rolname,rolsuper,rolinherit,rolcreaterole,rolcreatedb,rolcanlogin,\n rolreplication,rolbypassrls FROM pg_roles ORDER BY rolname","catalog_14":"SELECT pg_get_userbyid(roleid) AS granted_role,pg_get_userbyid(member) AS member,\n pg_get_userbyid(grantor) AS grantor,admin_option,inherit_option,set_option\nFROM pg_auth_members ORDER BY 1,2,3","catalog_15":"SELECT n.nspname,pg_get_userbyid(n.nspowner) AS owner,n.nspacl,\n r AS role,has_schema_privilege(r,n.oid,'USAGE') AS usage,\n has_schema_privilege(r,n.oid,'CREATE') AS create_privilege\nFROM pg_namespace n CROSS JOIN unnest(%(roles)s::text[]) r\nWHERE n.nspname=ANY(%(schemas)s::text[]) ORDER BY 1,4","catalog_16":"SELECT c.oid::regclass::text AS relation,r AS role,p AS privilege,\n has_table_privilege(r,c.oid,p) AS allowed\nFROM pg_class c CROSS JOIN unnest(%(roles)s::text[]) r\nCROSS JOIN unnest(ARRAY['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER','MAINTAIN']) p\nWHERE c.oid=ANY(%(relations)s::regclass[]) ORDER BY 1,2,3","catalog_17":"SELECT c.oid::regclass::text AS sequence,r AS role,p AS privilege,\n has_sequence_privilege(r,c.oid,p) AS allowed\nFROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace\nCROSS JOIN unnest(%(roles)s::text[]) r CROSS JOIN unnest(ARRAY['USAGE','SELECT','UPDATE']) p\nWHERE c.relkind='S' AND n.nspname=ANY(%(schemas)s::text[]) ORDER BY 1,2,3","catalog_18":"SELECT a.attrelid::regclass::text AS relation,a.attname,r AS role,p AS privilege,\n has_column_privilege(r,a.attrelid,a.attnum,p) AS allowed,a.attacl\nFROM pg_attribute a CROSS JOIN unnest(%(roles)s::text[]) r\nCROSS JOIN unnest(ARRAY['SELECT','INSERT','UPDATE','REFERENCES']) p\nWHERE a.attnum>0 AND NOT a.attisdropped AND a.attrelid=ANY(%(relations)s::regclass[])\nORDER BY 1,2,3,4","catalog_19":"SELECT pg_get_userbyid(defaclrole) AS role,n.nspname,defaclobjtype,defaclacl\nFROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace\nORDER BY 1,2,3","catalog_20":"SELECT i.indexrelid::regclass::text AS index_name,x.ord AS key_ordinal,\n x.collation_oid=0 AS no_collation,n.nspname AS collation_schema,\n co.collname,co.collprovider,co.collisdeterministic,co.collencoding,\n co.collcollate,co.collctype,co.colllocale,co.collicurules,co.collversion,\n pg_collation_actual_version(co.oid) AS actual_collation_version\nFROM pg_index i\nCROSS JOIN LATERAL unnest(i.indcollation::oid[]) WITH ORDINALITY x(collation_oid,ord)\nLEFT JOIN pg_collation co ON co.oid=x.collation_oid\nLEFT JOIN pg_namespace n ON n.oid=co.collnamespace\nWHERE i.indrelid=ANY(%(relations)s::regclass[])\nORDER BY index_name,key_ordinal"}''')
import re
from .canonical import FORMAT, digest, structural_objects
from .data_checks import MISSING_COVERAGE

SERVICE = re.compile(r"[A-Za-z0-9_.-]{1,128}\Z")

def collect(connection_service, manifest, policy):
    """Execute fixed catalog SELECTs in a single read-only PG17 transaction.

    Named relation parameters must use manifest [schema, relation] pairs. These
    compose quoted regclass names; no runtime policy SQL is accepted.
    """
    from psycopg import connect, sql
    from psycopg.rows import dict_row
    if not isinstance(connection_service, str) or not SERVICE.fullmatch(connection_service):
        raise ValueError("INVALID_CONNECTION_SERVICE")
    if not isinstance(manifest, dict) or not isinstance(policy, dict):
        raise ValueError("INVALID_INPUT_SHAPE")
    schemas = manifest.get("schemas")
    pairs = manifest.get("relations")
    roles = policy.get("roles")
    if not isinstance(schemas, list) or not schemas or not all(type(s) is str and s for s in schemas):
        raise ValueError("UNKNOWN_SCOPE")
    if not isinstance(pairs, list) or not pairs or not all(isinstance(p, list) and len(p) == 2 and all(type(s) is str and s for s in p) for p in pairs):
        raise ValueError("UNKNOWN_RELATION_SCOPE")
    if not isinstance(roles, list) or not roles or not all(type(r) is str and r for r in roles):
        raise ValueError("UNKNOWN_ACCESS_SCOPE")
    result = {"format": FORMAT, "observations": {}, "covered_query_ids": [], "errors": [],
              "missing_coverage": list(MISSING_COVERAGE), "data_validity_complete": False,
              "eligible": False, "query_names": dict(QUERY_NAMES), "reason_codes": ["UNKNOWN_IMPLEMENTATION_COVERAGE", "UNKNOWN_DATA_VALIDITY", "UNKNOWN_RECORDER_SCOPE", "UNKNOWN_ROLE_SETTINGS"]}
    # Errors expose only SQLSTATE; server messages may contain row values or credentials.
    try:
        with connect(service=connection_service, autocommit=True, row_factory=dict_row) as connection:
            cursor = connection.cursor()
            cursor.execute("BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY")
            try:
                for command in ("SET LOCAL search_path = pg_catalog", "SET LOCAL TimeZone = 'UTC'", "SET LOCAL statement_timeout = '60s'", "SET LOCAL lock_timeout = '5s'", "SET LOCAL row_security = off"):
                    cursor.execute(command)
                parameters = {"schemas": schemas, "roles": roles,
                              "relations": [sql.Identifier(*pair).as_string(connection) for pair in pairs]}
                for query_id, query in QUERIES.items():
                    cursor.execute(query, parameters if "%(" in query else None)
                    rows = cursor.fetchall()
                    result["observations"][query_id] = rows
                    result["covered_query_ids"].append(query_id)
                    if query_id == "catalog_01":
                        identity = rows[0] if len(rows) == 1 else {}
                        if not str(identity.get("server_version_num", "")).startswith("17") or identity.get("recovery") is not False or identity.get("read_only") != "on" or identity.get("isolation") != "repeatable read":
                            result["errors"].append({"code": "UNKNOWN_SESSION_IDENTITY"})
                            break
                if not result["errors"]:
                    # SELECT takes ACCESS SHARE without disclosing table rows.
                    for pair in pairs:
                        cursor.execute(sql.SQL("SELECT 1 FROM {} LIMIT 0").format(sql.Identifier(*pair)))
                    _collect_acls(cursor, parameters, result)
                    # Recorder rows are omitted until reviewed identity validation exists.
            finally:
                cursor.execute("ROLLBACK")
    except Exception as error:
        state = getattr(error, "sqlstate", None)
        result["errors"].append({"code": "UNKNOWN_COLLECTION_ERROR", "sqlstate": state if isinstance(state, str) and re.fullmatch(r"[A-Z0-9]{5}", state) else None})
    result["raw_observations_hash"] = digest(result["observations"])
    result["structural_hash"] = digest({"format": FORMAT, "baseline_input_hashes": manifest.get("baseline_input_hashes", {}), "structural_objects": structural_objects(result["observations"])})
    return result

def _collect_acls(cursor, parameters, result):
    fixed = {
        "acl_relations": """SELECT n.nspname,c.relname,c.relacl IS NULL AS default_acl,
 CASE WHEN x.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(x.grantee) END AS grantee,
 pg_get_userbyid(x.grantor) AS grantor,x.privilege_type,x.is_grantable
 FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
 CROSS JOIN LATERAL aclexplode(COALESCE(c.relacl,acldefault(CASE WHEN c.relkind='S' THEN 's'::\"char\" ELSE 'r'::\"char\" END,c.relowner))) x
 WHERE c.oid=ANY(%(relations)s::regclass[]) OR (c.relkind='S' AND n.nspname=ANY(%(schemas)s::text[])) ORDER BY 1,2,3,4,5,6,7""",
        "acl_namespaces": """SELECT n.nspname,n.nspacl IS NULL AS default_acl,
 CASE WHEN x.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(x.grantee) END AS grantee,
 pg_get_userbyid(x.grantor) AS grantor,x.privilege_type,x.is_grantable
 FROM pg_namespace n CROSS JOIN LATERAL aclexplode(COALESCE(n.nspacl,acldefault('n',n.nspowner))) x
 WHERE n.nspname=ANY(%(schemas)s::text[]) ORDER BY 1,2,3,4,5,6""",
        "acl_database": """SELECT d.datacl IS NULL AS default_acl,
 CASE WHEN x.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(x.grantee) END AS grantee,
 pg_get_userbyid(x.grantor) AS grantor,x.privilege_type,x.is_grantable
 FROM pg_database d CROSS JOIN LATERAL aclexplode(COALESCE(d.datacl,acldefault('d',d.datdba))) x
 WHERE d.datname=current_database() ORDER BY 1,2,3,4,5""",
        "acl_columns": """SELECT a.attrelid::regclass::text AS relation,a.attname,
 CASE WHEN x.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(x.grantee) END AS grantee,
 pg_get_userbyid(x.grantor) AS grantor,x.privilege_type,x.is_grantable
 FROM pg_attribute a CROSS JOIN LATERAL aclexplode(a.attacl) x
 WHERE a.attnum>0 AND NOT a.attisdropped AND a.attacl IS NOT NULL AND a.attrelid=ANY(%(relations)s::regclass[]) ORDER BY 1,2,3,4,5,6""",
        "database_privileges": """SELECT r AS role,p AS privilege,has_database_privilege(r,current_database(),p) AS allowed
 FROM unnest(%(roles)s::text[]) r CROSS JOIN unnest(ARRAY['CONNECT','CREATE','TEMP']) p ORDER BY 1,2""",
    }
    for query_id, query in fixed.items():
        cursor.execute(query, parameters)
        result["observations"][query_id] = cursor.fetchall()
        result["covered_query_ids"].append(query_id)

# Additional fixed index semantics. Support-function dependency closure remains unknown.
QUERIES["catalog_21"] = """SELECT i.indexrelid::regclass::text AS index_name,x.ord AS key_ordinal,
 n.nspname AS opclass_schema,oc.opcname,oc.opcdefault,
 fn.nspname AS opfamily_schema,f.opfname,am.amname,
 tn.nspname AS input_type_schema,t.typname AS input_type,
 i.indoption[x.ord-1] AS key_options
 FROM pg_index i
 CROSS JOIN LATERAL unnest(i.indclass::oid[]) WITH ORDINALITY x(opclass_oid,ord)
 LEFT JOIN pg_opclass oc ON oc.oid=x.opclass_oid
 LEFT JOIN pg_namespace n ON n.oid=oc.opcnamespace
 LEFT JOIN pg_opfamily f ON f.oid=oc.opcfamily
 LEFT JOIN pg_namespace fn ON fn.oid=f.opfnamespace
 LEFT JOIN pg_am am ON am.oid=oc.opcmethod
 LEFT JOIN pg_type t ON t.oid=oc.opcintype
 LEFT JOIN pg_namespace tn ON tn.oid=t.typnamespace
 WHERE i.indrelid=ANY(%(relations)s::regclass[])
 ORDER BY index_name,key_ordinal"""


QUERY_NAMES = {
    "catalog_01": "session_identity", "catalog_02": "database_collation",
    "catalog_03": "namespaces", "catalog_04": "relations", "catalog_05": "columns",
    "catalog_06": "constraints", "catalog_07": "indexes", "catalog_08": "sequences",
    "catalog_09": "triggers", "catalog_10": "policies", "catalog_11": "rules",
    "catalog_12": "extensions", "catalog_13": "roles", "catalog_14": "memberships",
    "catalog_15": "schema_privileges", "catalog_16": "table_privileges",
    "catalog_17": "sequence_privileges", "catalog_18": "column_privileges",
    "catalog_19": "default_acls", "catalog_20": "index_collations",
    "catalog_21": "index_opclasses",
}


