> Question 1: What happens to everything written to `/mlflow-data` if you never mount a volume there and just `docker run` this image standalone? Try it: run the container, register nothing, stop it, remove it, start a new one from the same image — what do you see in the UI?

    if no volume is mounted at /mlflow-data, the database and artifacts are stored inside the container's writable filesystem. They remain when the container is stopped, but are lost when the container is removed. A new container from the same image will therefore show an empty MLflow UI.

> Question 2: Why a named volume here instead of a bind mount to a folder in your repo (the way you might for local dev)? Would a bind mount work just as well?

    A named volume is used because it keeps MLflow's database and artifacts persistent and independent of the container, without putting service data inside the Git repository. A bind mount would also work, but it ties the storage to a specific host directory and is less portable/clean for this Compose setup.

> Question 3: In Lab 3 you had to use `host.docker.internal` or `--network host` to reach mlflow from inside the container. In this lab, `MLFLOW_TRACKING_URI` will simply be `http://mlflow:5000`. Why does that hostname resolve now when it didn't before?

    Docker Compose creates a shared network for the services and provides built-in DNS that resolves service names to their container IPs. Since the MLflow service is named mlflow, the inference container can reach it using http://mlflow:5000. In Lab 3, MLflow was running on the host, so mlflow was not a resolvable container hostname.

> Question 4: Why does the frontend read `INFERENCE_URL` from an environment variable instead of hardcoding `http://inference:8000`? Think about what happens if you ever `docker run` this frontend image on its own, outside Compose.

    The frontend reads `INFERENCE_URL` from an environment variable so the same image can work in different environments.

    In Docker Compose, `INFERENCE_URL` can be set to `http://inference:8000`, where `inference` is the Compose service name. If the frontend is run independently with `docker run`, that hostname may not exist, so the default `http://127.0.0.1:8000` can be used instead.

    This makes the frontend image more flexible and reusable without changing its code.

> Question 5: Only `mlflow` and `frontend` publish a port to the host. `inference` doesn't. Why not, and how does the frontend still reach it?

    The inference service does not need to publish a port because it is only accessed by the frontend service, not directly by the user.

    Docker Compose puts all three services on the same private network, so the frontend can reach the inference service using its service name:

    http://inference:8000

    Only mlflow and frontend publish ports because they need to be accessible from the host: MLflow for its UI and frontend for the Streamlit web page.

> Question 6: `depends_on` here only waits for the mlflow *container process* to start, not for the tracking server inside it to be ready to accept connections. If your `serve.py` tries to load the Staging model at startup and mlflow isn't ready yet, what happens to the `inference` container? Look at `docker compose logs inference` if it fails.

    If inference starts before the MLflow server is ready, serve.py may fail when it tries to connect to MLflow and load the model.

    The inference container will typically exit or restart depending on its configuration, rather than waiting automatically for MLflow to become ready. depends_on only controls the startup order; it does not check whether MLflow is actually ready to accept requests.

    The error can be inspected with:
    docker compose logs inference

> Question 7: Run `docker compose ps`. Which services have a published port listed, and which don't? Does that match what you'd expect from the `docker-compose.yml`?
    Yes, this matches expectations. The frontend is accessible from the browser on port 8501, and MLflow is accessible on port 5000. The inference service is accessed internally by the frontend through Docker Compose networking at http://inference:8000, so it doesn't need a published host port.


> Question 8: Refresh the frontend and upload an image again. Does the prediction come from the new model version, or the old one? Your `serve.py` loads the model once, at startup — what single command lets you pick up the new Staging version without rebuilding any image?
    The prediction will still come from the old model version, because serve.py loads the model once when the inference container starts.


> Question 9: Why does `restart` alone work here — no rebuild needed? What does that tell you about what's baked into the inference image versus fetched at container startup?
    docker compose restart inference works without rebuilding because the model is fetched from the MLflow server at container startup, rather than being baked into the Docker image.
- Baked into the inference image: the application code (serve.py), Python environment, dependencies, and inference API.
- Fetched at startup: the model referenced by the champion alias in MLflow (models:/food11@champion).
Restarting the container reruns the application startup, so it loads whichever model version the alias points to at that moment. Rebuilding is unnecessary because neither the application code nor its dependencies changed.

> Question 10: Is your registered model and its Staging assignment still there after this `down`/`up` cycle? Now try `docker compose down -v` followed by `docker compose up` — what's different this time, and why?

    docker compose down followed by docker compose up: Yes, the registered model and its Staging assignment should remain, because down removes containers and networks but preserves your bind-mounted mlflow.db and mlruns files.

    docker compose down -v followed by docker compose up: In your current setup, the model should still remain, because mlflow.db and mlruns are mounted from local folders/files, not stored in a Compose-managed named volume. The -v flag removes Compose-managed named volumes, not these bind-mounted files.

> Question 11: This compose file is still meant to run on one machine. What would have to change for the `inference` service to run as three replicas behind a load balancer, or for the mlflow service to survive a machine failure? (You don't need to implement this — just name what Docker Compose can't give you here.)

    Three inference replicas behind a load balancer: We would need container orchestration, such as Docker Swarm or Kubernetes, to manage replicas, distribute traffic, and handle service discovery and health checks. Standard Docker Compose is primarily designed for single-machine deployments.

    MLflow surviving a machine failure: We would need high availability across multiple machines, with persistent storage accessible from another machine, a replicated or managed database for the MLflow registry, and a failover strategy. Docker Compose alone does not provide cross-machine failover or high availability.