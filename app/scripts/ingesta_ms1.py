"""
ingesta-ms1 — Extrae las 6 tablas de pasajeros_db y sube CSVs a S3.

Formato S3:  raw/ms1/<tabla>/<YYYY-MM-DD>/<tabla>.csv
Tablas:     persona, categoria_migratoria, pasajero, ticket, checkin, equipaje

Dependencias (DS):
  - DS-04: Bucket S3 creado por el Lead (nombre del bucket en AWS_S3_BUCKET)
  - DS-05: VM-INGESTA con credenciales AWS configuradas (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)

Uso:
  docker exec -it ms1-pasajeros-api-app-1 python -m app.scripts.ingesta_ms1

Variables de entorno requeridas (en .env o entorno Docker):
  DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
  AWS_S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION
"""

import csv
import io
import os
from datetime import date

import boto3
from sqlalchemy import create_engine, text

TABLAS = ["persona", "categoria_migratoria", "pasajero", "ticket", "checkin", "equipaje"]


def get_engine():
    url = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )


def extraer_tabla(engine, tabla: str) -> list[dict]:
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {tabla}"))
        columns = result.keys()
        return [dict(zip(columns, row)) for row in result.fetchall()]


def subir_csv_s3(s3, bucket: str, tabla: str, rows: list[dict]):
    if not rows:
        print(f"  {tabla}: 0 filas, skip")
        return

    fecha = date.today().isoformat()
    key = f"raw/ms1/{tabla}/{fecha}/{tabla}.csv"

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=buffer.getvalue().encode("utf-8"),
        ContentType="text/csv",
    )
    print(f"  {tabla}: {len(rows)} filas → s3://{bucket}/{key}")


def main():
    bucket = os.getenv("AWS_S3_BUCKET")
    if not bucket:
        raise RuntimeError("AWS_S3_BUCKET no configurado (DS-04 pendiente)")

    print(f"[ingesta-ms1] Bucket: {bucket}")
    engine = get_engine()
    s3 = get_s3_client()

    for tabla in TABLAS:
        print(f"Extrayendo {tabla}...")
        rows = extraer_tabla(engine, tabla)
        subir_csv_s3(s3, bucket, tabla, rows)

    print("[ingesta-ms1] Completado.")


if __name__ == "__main__":
    main()
