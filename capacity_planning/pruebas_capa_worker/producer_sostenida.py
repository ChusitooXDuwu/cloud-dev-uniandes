import uuid
import time
from datetime import datetime
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import pandas as pd

from app.core.config import settings
from app.models.video import Video
from app.models.user import User


celery_app = Celery(
    "producer",
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://"
)


SYNC_DATABASE_URL = settings.DATABASE_URL.replace("+asyncpg", "")
sync_engine = create_engine(SYNC_DATABASE_URL)
SyncSessionLocal = sessionmaker(bind=sync_engine)


video_sizes = [50, 100]       # MB
concurrency = 1     # número de workers activos
test_duration_sec = 300       # duración de 5 minutos
rate_tareas_por_seg = 1       # tasa de envío 
DATA_PATH = "capacity_planning/pruebas_capa_worker/Resultados/test_sostenida_1.csv"

records = []
i = 0
for size in video_sizes:
    video_file = Path(f"capacity_planning/pruebas_capa_worker/videos/flex_mini_{i}.mp4")

    if not video_file.exists():
        print(f" Archivo de prueba {video_file} no encontrado")
    else:

        print(f"\n=== Prueba sostenida: {size}MB | {concurrency} worker(s) ===")
        start_time = datetime.now()

        enviados = 0
        completados = 0
        pendientes = []
        interval = 1.0 / rate_tareas_por_seg
        tiempo_inicio_prueba = time.time()

        # Crear sesión DB y obtener user_id existente
        db = SyncSessionLocal()
        user_id = db.query(User.id).first()[0]

        while (time.time() - tiempo_inicio_prueba) < test_duration_sec:
            vid = uuid.uuid4()
            file_size = video_file.stat().st_size

            # Crear registro del video
            video_entry = Video(
                id=vid,
                user_id=user_id,
                title=f"Video sostenido {size}MB #{enviados + 1}",
                original_filename=video_file.name,
                file_path=str(video_file),
                status="uploaded",
                duration_seconds=None,
                file_size_bytes=file_size,
                is_public=False,
                votes_count=0,
                uploaded_at=datetime.utcnow(),
            )
            db.add(video_entry)
            db.commit()

            # Enviar tarea Celery
            result = celery_app.send_task("process_video", args=[str(vid), str(video_file)])
            pendientes.append(result.id)
            enviados += 1

            # Revisión de tareas completadas
            for task_id in pendientes[:]:
                res = celery_app.AsyncResult(task_id)
                if res.ready():
                    completados += 1
                    pendientes.remove(task_id)

            time.sleep(interval)

        while pendientes:
            for task_id in pendientes[:]:
                res = celery_app.AsyncResult(task_id)
                if res.ready():
                    completados += 1
                    pendientes.remove(task_id)
            time.sleep(2)

        db.close()

        # --- Métricas de rendimiento ---
        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        throughput = completados / (elapsed / 60)

        records.append({
            "video_size_mb": size,
            "concurrency": concurrency,
            "test_duration_sec": test_duration_sec,
            "rate_tareas_por_seg": rate_tareas_por_seg,
            "enviados": enviados,
            "completados": completados,
            "throughput_videos_por_min": round(throughput, 2),
            "start_time": start_time,
            "end_time": end_time,
            "elapsed_seconds": round(elapsed, 2)
        })

        print(f" Finalizada: {size}MB @ {concurrency}w — {throughput:.2f} videos/min")
    i+=1
# Guardar resultados 
df = pd.DataFrame(records)
df.to_csv(DATA_PATH, index=False)
print(f"\n Resultados guardados en {DATA_PATH}")
