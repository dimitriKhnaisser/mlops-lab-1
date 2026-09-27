> Question 1: Look at pyproject.toml and uv.lock. What changed?

    `pyproject.toml` was updated to include MLflow, PyTorch, torchvision, and scikit-learn as project dependencies.
    `uv.lock` was created/updated with the exact versions of these packages and their dependencies, ensuring the same environment can be reproduced later.



> Question 2: What is `--backend-store-uri` used for? What is `--default-artifact-root` used for? What is the difference between the metadata mlflow stores and the artifacts it stores?

    `--backend-store-uri` specifies where MLflow stores the tracking metadata, such as experiments, runs, parameters, and metrics. In our case, it uses the SQLite database `mlflow.db`.

    `--default-artifact-root` specifies where MLflow stores artifacts such as trained models, plots, and other output files. In our case, they are stored in the `./mlruns` folder.

    The difference is that metadata describes the experiment and its results, while artifacts are the actual files produced or saved during a run.



> Question 3: Why shouldn't `mlflow.db` and `mlruns/` be tracked by git, and why shouldn't they be tracked by dvc either?

    `mlflow.db` and `mlruns/` should not be tracked by Git because they contain local experiment-tracking data that can become large and change frequently.

    They should not be tracked by DVC either because DVC is meant for versioning datasets and large data/model files, not MLflow's experiment metadata and artifacts.



> Question 4: What happens the first time you call `set_experiment` with a name that doesn't exist yet? Check the mlflow UI.

    The first time `set_experiment("food11")` is called, MLflow creates a new experiment named **food11** because it does not exist yet. It then appears in the MLflow UI as a new experiment, ready to contain training runs.

> Question 5: What is the difference between `mlflow.log_param` and `mlflow.log_metric`? Why does `log_metric` take a `step` argument and `log_param` doesn't?
    
    `mlflow.log_param` records a parameter that is fixed for a run, such as the learning rate, batch size, or number of epochs.

    `mlflow.log_metric` records a value produced during training, such as loss or accuracy, which can change over time.

    `log_metric` takes a `step` argument because metrics can be recorded repeatedly during training, for example once per epoch. The `step` identifies when the metric was recorded and allows MLflow to display its evolution over time. Parameters are normally logged once per run, so they do not need a step.

> Question 6: Open the run in the mlflow UI. Find the params, the metric charts, and the logged model artifact. Where does the model artifact actually live on disk?

    In the MLflow UI, the run contains the logged parameters, metric charts (train_loss, val_loss, val_accuracy, and test_accuracy), and the trained model artifact.

    The model artifact is stored on disk under the ./mlruns/ directory, inside the experiment and run folders, specifically in the run's artifacts/model/ folder.


> Question 7: In the mlflow UI, open the `food11` experiment. Select these runs and click "Compare". Which learning rate gave the best `val_accuracy`? Is higher always better?

    The learning rate of **0.0001** gave the best validation accuracy, with a `val_accuracy` of **0.728 (72.8%)**. Higher `val_accuracy` is generally better because it means the model correctly classified more validation samples.



> Question 8: Use the parallel coordinates plot on the compare page to look at `lr`, `batch_size` and `val_accuracy` together. What pattern do you see?
    The parallel coordinates plot shows that lower learning rates generally gave higher validation accuracy in these experiments. With a batch size of 32, reducing the learning rate from 0.01 to 0.001 and then to 0.0001 increased `val_accuracy` from 0.167 to 0.505 and then 0.728. Increasing the batch size from 32 to 64 at a learning rate of 0.001 also increased `val_accuracy` from 0.505 to 0.569.
    So we can call it a negative relationship between learning rate and validation accuracy



> Question 9: Sort the runs table by `val_accuracy` descending. Which run is the best one? Note its run ID, you'll need it in the next lab.
   
    3d7423f8c3f64287992e096b495d3a4f --> val_accuracy: 0.728
    5f24afd0dd314b67b7ac0e6a7d2a131e --> val_accuary: 0.569
    0bf8e01335744b7db84661fab1cc0b82 --> val_accuracy: 0.505
    36c19db039664c47a3be93a98c366548 --> val_accuracy: 0.081

    The best run is the one with the highest `val_accuracy` of 0.728.
    Run ID: 3d7423f8c3f64287992e096b495d3a4f
