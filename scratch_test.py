import basedosdados as bd
from codes.bd_config import BILLING_ID

query = """
SELECT id_municipio_ocorrencia, id_uf_ocorrencia, ano, sexo_paciente
FROM `basedosdados.br_ms_sinan.microdados_violencia`
WHERE id_municipio_ocorrencia LIKE '355030%'
LIMIT 10
"""
try:
    df = bd.read_sql(query=query, billing_project_id=BILLING_ID)
    print("Columns found:")
    print(df)
except Exception as e:
    print("Error:", e)
