> Question 1: Observe the files created, what do you think they contain.
    pyproject.toml
    README.md 
    python-version
    main.py 
    .gitignore

> Question 2: What are the created files. What do you think they are used for? And which ones should be pushed to git?
    config → DVC project configuration, including your DVC remote (dvc-storage in your case).
    cache/ → DVC's local cache containing stored versions/copies of your data. Do not push this to Git.
    tmp/ → temporary files DVC uses while performing operations. Do not push this to Git.
    .gitignore → tells Git to ignore DVC's cache and temporary files. The file itself can be committed to Git.
> Question 3: Where are the credentials stored? and what are the options other than --global? Should the credentials be pushed to github? 
    Since we used a local DVC remote instead of DagsHub, no credentials were needed or stored.

    The DVC remote was configured to point to our local dvc-storage folder. The --global option would store the configuration globally for the user, while other options include using a project-level configuration without --global, or --local to store machine-specific/private configuration.

    Credentials should never be pushed to GitHub, as they are sensitive information. In our case, there were no credentials to push because we used a local remote.

> Question 4: Take a look at the .gitignore file. Explain what happened.
    After running dvc add data, DVC automatically updates the .gitignore file by adding the data folder to it. This tells Git to ignore the actual dataset because the data is managed and versioned by DVC instead of Git.

> Question 5: Do you see a .dvc file? What does it contain?  
    Yes, a data.dvc file is created after running dvc add data. It contains metadata about the data folder, including its path and a hash (MD5) that identifies the exact version of the data. It acts as a pointer to the data stored by DVC rather than containing the actual dataset itself.
