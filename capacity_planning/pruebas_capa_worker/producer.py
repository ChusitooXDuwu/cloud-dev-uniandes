import uuid
import random
import time
from datetime import datetime
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import pandas as pd

# Importar configuración y modelo
from app.core.config import settings
from app.models.video import Video
from app.models.user import User

# --- Config Celery ---
celery_app = Celery(
    "producer",
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://"
)

# --- Config DB 
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("+asyncpg", "")
sync_engine = create_engine(SYNC_DATABASE_URL)
SyncSessionLocal = sessionmaker(bind=sync_engine)

video_sizes = [50, 100]  # MB
concurrency = 2  # workers activos
videos_por_prueba = 2
DATA_PATH = "capacity_planning/pruebas_capa_worker/Resultados/test_data_c2.csv"

records = []

i = 0
for size in video_sizes:
    video_file = Path(f"capacity_planning/pruebas_capa_worker/videos/flex_mini_{i}.mp4")

    if not video_file.exists():
        print(f"Archivo de prueba {video_file} no encontrado, se omite esta prueba.")
    else:
        print(f"\n Ejecutando prueba: {size}MB | {concurrency} worker(s)")
        start_time = datetime.now()

        db = SyncSessionLocal()
        task_ids = []
        video_ids = []

        # Crear registros de Video en BD
        for i in range(videos_por_prueba):
            vid = uuid.uuid4()

            # Obtener tamaño real del archivo en bytes
            file_size = video_file.stat().st_size

            video_entry = Video(
                id=vid,
                user_id=db.query(User.id).first()[0],
                title=f"Video test {size}MB #{i+1}",
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
            video_ids.append(str(vid))

        db.commit()
        db.close()

        # Lanzar tareas Celery
        for vid in video_ids:
            result = celery_app.send_task(
                "process_video",
                args=[vid, str(video_file)],
            )
            task_ids.append(result.id)
            time.sleep(0.1)  # evitar sobrecargar cola instantáneamente


        finished = 0
        total = len(task_ids)
        while finished < total:
            time.sleep(5)
            completed = []
            for task_id in task_ids:
                res = celery_app.AsyncResult(task_id)
                if res.ready():
                    finished += 1
                    completed.append(task_id)
            for c in completed:
                task_ids.remove(c)
            print(f" → {finished}/{total} completadas")

        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        throughput = videos_por_prueba / (elapsed / 60)

        records.append({
            "video_size_mb": size,
            "concurrency": concurrency,
            "total_videos": videos_por_prueba,
            "elapsed_seconds": round(elapsed, 2),
            "throughput_videos_per_min": round(throughput, 2),
            "start_time": start_time,
            "end_time": end_time,
        })

        print(f" Finalizada prueba {size}MB con {concurrency} workers — {throughput:.2f} videos/min")
    i += 1

df = pd.DataFrame(records)
df.to_csv(DATA_PATH, index=False)
print(f"\n Resultados guardados en {DATA_PATH}")
