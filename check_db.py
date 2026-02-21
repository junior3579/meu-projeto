from backend.database_config import executar_query_fetchall

res = executar_query_fetchall("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'usuarios'
    ORDER BY ordinal_position
""")

for col in res:
    print(col)
