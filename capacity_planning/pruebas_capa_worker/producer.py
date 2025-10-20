import uuid
import random
import time
from datetime import datetime
from celery import Celery
import pandas as pd


celery_app = Celery(
    "producer",
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://"
)


# Escenarios de prueba
video_sizes = [50, 100]  # MB
concurrencias = [1, 2, 4]  # hilos/procesos de worker
videos_por_prueba = 10  # cantidad por experimento

# Archivo base
DATA_PATH = "capacity_planning\pruebas_capa_worker/Resultados/test_data.csv"
records = []

for size in video_sizes:
    video_file = f"capacity_planning\pruebas_capa_worker/videos_test/test_{size}mb.mp4"
    for concurrency in concurrencias:
        print(f"\n Ejecutando prueba: {size}MB | {concurrency} worker(s)")


        start_time = datetime.now()

        task_ids = []
        for i in range(videos_por_prueba):
            vid = str(uuid.uuid4())
            result = celery_app.send_task(
                "process_video",
                args=[vid, video_file],
            )
            task_ids.append(result.id)
            time.sleep(0.1) 

        print(" Esperando resultados...")
        finished = 0
        while finished < len(task_ids):
            i = 0
            for task_id in task_ids:
                res = celery_app.AsyncResult(task_id)
                if res.ready():
                    finished += 1
                    task_ids.remove(task_id)
            time.sleep(2)
            i += 1

        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()
        throughput = len(task_ids) / (elapsed / 60)

        records.append({
            "video_size_mb": size,
            "concurrency": concurrency,
            "total_videos": videos_por_prueba,
            "elapsed_seconds": round(elapsed, 2),
            "throughput_videos_per_min": round(throughput, 2),
            "start_time": start_time,
            "end_time": end_time,
        })

        print(f" Finalizada prueba {size}MB @ {concurrency} — {throughput:.2f} videos/min")


df = pd.DataFrame(records)
df.to_csv(DATA_PATH, index=False)
print(f"\n Resultados guardados en {DATA_PATH}")
