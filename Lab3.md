> Question 1: Open the "Models" tab in the mlflow UI. What version number was your model given? What's the difference between a run's logged model artifact and a registered model?

    The model will be given **Version 1** when it is registered, assuming this is the first version of the `food11` model.

    A logged model artifact belongs to a specific MLflow run and represents the model produced by that training run. A registered model is a named model in the MLflow Model Registry that can have multiple numbered versions, making it easier to manage and track different trained models.

> Question 2: What aliases replaced the old built-in stages in mlflow? Why version a model separately from the run that produced it, and why is an alias more flexible than a fixed stage name?

    MLflow replaced fixed stages like **Staging** and **Production** with **aliases**.

    The run records the training experiment, while the registered model versions the actual model separately. An alias is more flexible because it can point to any model version and be moved when needed.

> Question 3: Why load the model through an mlflow model URI (`models:/food11@champion`) instead of pointing directly at the `.pth` file on disk? What would you have to change to serve a newer model version?

    Loading the model through `models:/food11@champion` allows the service to use the MLflow Model Registry and the `champion` alias instead of depending on a specific `.pth` file path. This makes model version management easier and keeps the serving code unchanged when models are updated.

    To serve a newer model version, we only need to move the `champion` alias to the new version. The FastAPI code does not need to change.

> Question 4: Why copy `pyproject.toml`/`uv.lock` and run `uv sync` *before* copying the rest of the source code, instead of copying everything at once? What happens to the build cache when you only change a line in `serve.py`?

    Copying pyproject.toml and uv.lock before the source code allows Docker to cache the dependency installation layer. If only serve.py changes, Docker reuses the cached dependency layer instead of running uv sync again, making the rebuild much faster. If everything were copied at once, a source-code change would invalidate the layer and reinstall the dependencies.

> Question 5: What's the size difference between a naive single-stage image and your multi-stage one? Use `docker history <image>` to see which layers are the biggest.

    The multi-stage image is smaller because the final image only contains the runtime Python image, the virtual environment, and the application source code. The largest layer is the copied .venv, at about 1.44 GB. The Python base image contributes roughly 142 MB, while the source code is only about 49 KB. A naive single-stage image would also contain the build tooling and other intermediate files, making it larger.


> Question 6: What happens to build speed and image size if you forget the `.dockerignore`? Which of the excluded folders would actually break the build if they were sent to the Docker daemon?

    Without a .dockerignore, Docker sends unnecessary files such as the dataset, .venv, MLflow artifacts, Git history, and caches to the Docker daemon. This increases the build context size and can make builds slower, especially when large folders like data/ are included. The final image size does not necessarily increase with the current Dockerfile because those files are not copied into the runtime stage, but the build process becomes slower and less efficient. None of the excluded folders are required for this Dockerfile to build successfully; they mainly waste build-context transfer time and resources.

> Question 7: Why can't the container simply use `127.0.0.1:5000` to reach the mlflow server on your host? What does `host.docker.internal` resolve to?

    A container has its own network namespace, so 127.0.0.1 inside the container refers to the container itself, not the host machine. Therefore, 127.0.0.1:5000 cannot reach the MLflow server running on the host. On Docker Desktop for Windows/macOS, host.docker.internal resolves to the host machine, allowing the container to access the host's MLflow server.


> Question 8: Stop the container and start a new one from the same image. Does the model still load correctly without you rebuilding? What does that tell you about what's baked into the image versus fetched at runtime?

    Yes, the model still loads correctly without rebuilding the image. This shows that the application code and dependencies are baked into the Docker image, while the model itself is fetched from MLflow at runtime. This allows us to update or change the registered model without rebuilding the Docker image.


> Question 9: The Dockerfile and image are versioned differently — one lives in git, the other doesn't (yet). What's still missing before another machine (like a CI runner or a Kubernetes cluster) could reliably pull and run the exact image you just built?

    The Docker image needs to be pushed to a container registry such as Docker Hub or GitHub Container Registry. The image should also be tagged with a specific version or commit tag rather than relying only on latest. This allows another machine, CI runner, or Kubernetes cluster to pull and run the exact same image reliably.