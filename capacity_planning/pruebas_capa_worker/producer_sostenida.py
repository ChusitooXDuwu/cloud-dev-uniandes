import uuid
import time
from datetime import datetime
from celery import Celery
import pandas as pd

celery_app = Celery(
    "producer",
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://"
)

video_sizes = [50, 100]              # MB
concurrencias = [1, 2, 4]            # número de workers activos
test_duration_sec = 300              # duración de cada prueba (5 min)
rate_tareas_por_seg = 1              # tasa de envío (tareas/segundo)
DATA_PATH = "capacity_planning/pruebas_capa_worker/Resultados/test_sostenida.csv"

records = []

for size in video_sizes:
    video_file = f"capacity_planning/pruebas_capa_worker/videos_test/test_{size}mb.mp4"

    for concurrency in concurrencias:
        print(f"\n=== Prueba sostenida: {size}MB | {concurrency} worker(s) ===")
        start_time = datetime.now()

        enviados = 0
        completados = 0
        pendientes = []
        interval = 1.0 / rate_tareas_por_seg

        tiempo_inicio_prueba = time.time()

        while (time.time() - tiempo_inicio_prueba) < test_duration_sec:
            # Enviar tarea
            vid = str(uuid.uuid4())
            result = celery_app.send_task("process_video", args=[vid, video_file])
            pendientes.append(result.id)
            enviados += 1

            
            for task_id in pendientes[:]:
                res = celery_app.AsyncResult(task_id)
                if res.ready():
                    completados += 1
                    pendientes.remove(task_id)

            time.sleep(interval)  

        # Esperar que terminen las pendientes
        print(" Esperando tareas restantes...")
        while pendientes:
            for task_id in pendientes[:]:
                res = celery_app.AsyncResult(task_id)
                if res.ready():
                    completados += 1
                    pendientes.remove(task_id)
            time.sleep(2)

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


df = pd.DataFrame(records)
df.to_csv(DATA_PATH, index=False)
print(f"\n Resultados guardados en {DATA_PATH}")
