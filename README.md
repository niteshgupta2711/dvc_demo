```
claearly we are gonna start with emty repo
```
```
setup the virtual env
```
```
git init 
dvc init
```
```
git status
```
```
commit your initial git commit
```
```
dvc get https:www.github.com/iterative/dataset-registry get-started/data.xml -o path
```
```
dvc get repo_link folder/file -o path
```
```
dvc add data/data.xml
```
```
dvc remote add name gdrive://key
```
```
Inorder to switch between version for both code and data 
git checkout branch
dvc checkout
```
```
dvc list repolink folder_tracked_by_dvc
```
```
dvc get repolink folder_tracked_by_dvc
```
> to get the latest version of any artifact tracked by dvc 
```
You can use dvc list to explore a DVC repository hosted on any Git server. For example, let's see what's in the get-started/ directory of our dataset-registry repo:
```
```
dvc list https://github.com/iterative/dataset-registry get-started
.gitignore
data.xml
data.xml.dvc
```
```
dvc list https://github.com/iterative/dataset-registry get-started
.gitignore
data.xml
data.xml.dvc```
```
One way is to simply download the data with dvc get. This is useful when working outside of a DVC project environment, for example in an automated ML model deployment task:

dvc get https://github.com/iterative/dataset-registry \
          use-cases/cats-dogs
When working inside another DVC project though, this is not the best strategy because the connection between the projects is lost — others won't know where the data came from or whether new versions are available.

Import file or directory
dvc import also downloads any file or directory, while also creating a .dvc file (which can be saved in the project):

dvc import https://github.com/iterative/dataset-registry \
             get-started/data.xml -o data/data.xml
This is similar to dvc get + dvc add, but the resulting .dvc files includes metadata to track changes in the source repository. This allows you to bring in changes from the data source later using dvc update.

💡 Expand to see what happens under the hood.



Python API
It's also possible to integrate your data or models directly in source code with DVC's Python API. This lets you access the data contents directly from within an application at runtime. For example:

import dvc.api

with dvc.api.open(
    'get-started/data.xml',
    repo='https://github.com/iterative/dataset-registry'
) as fd:```
```
Versioning large data files and directories for data science is great, but not enough. How is data filtered, transformed, or used to train ML models? DVC introduces a mechanism to capture data pipelines — series of data processes that produce a final result.

DVC pipelines and their data can also be easily versioned (using Git). This allows you to better organize projects, and reproduce your workflow and results later — exactly as they were built originally! For example, you could capture a simple ETL workflow, organize a data science project, or build a detailed machine learning pipeline.

Watch and learn, or follow along with the code example below!


Pipeline stages
Use dvc stage add to create stages. These represent processes (source code tracked with Git) which form the steps of a pipeline. Stages also connect code to its corresponding data input and output. Let's transform a Python script into a stage:

⚙️ Expand to download example code.
Get the sample code like this:

wget https://code.dvc.org/get-started/code.zip
unzip code.zip
rm -f code.zip
tree
.
├── params.yaml
└── src
    ├── evaluate.py
    ├── featurization.py
    ├── prepare.py
    ├── requirements.txt
    └── train.py
Now let's install the requirements:

We strongly recommend creating a virtual environment first.

pip install -r src/requirements.txt
Please also add or commit the source code directory with Git at this point.

dvc stage add -n prepare \
                -p prepare.seed,prepare.split \
                -d src/prepare.py -d data/data.xml \
                -o data/prepared \
                python src/prepare.py data/data.xml
A dvc.yaml file is generated. It includes information about the command we want to run (python src/prepare.py data/data.xml), its dependencies, and outputs.

DVC uses these metafiles to track the data used and produced by the stage, so there's no need to use dvc add on data/prepared manually.

💡 Expand to see what happens under the hood.







Once you added a stage, you can run the pipeline with dvc repro. Next, you can use dvc push if you wish to save all the data to remote storage (usually along with git commit to version DVC metafiles).

Dependency graphs (DAGs)
By using dvc stage add multiple times, and specifying outputs of a stage as dependencies of another one, we can describe a sequence of commands which gets to a desired result. This is what we call a data pipeline or dependency graph.

Let's create a second stage chained to the outputs of prepare, to perform feature extraction:

dvc stage add -n featurize \
                -p featurize.max_features,featurize.ngrams \
                -d src/featurization.py -d data/prepared \
                -o data/features \
                python src/featurization.py data/prepared data/features
The dvc.yaml file is updated automatically and should include two stages now.

💡 Expand to see what happens under the hood.
The changes to the dvc.yaml should look like this:

 stages:
   prepare:
     cmd: python src/prepare.py data/data.xml
     deps:
     - data/data.xml
     - src/prepare.py
     params:
     - prepare.seed
     - prepare.split
     outs:
     - data/prepared
+  featurize:
+    cmd: python src/featurization.py data/prepared data/features
+    deps:
+    - data/prepared
+    - src/featurization.py
+    params:
+    - featurize.max_features
+    - featurize.ngrams
+    outs:
+    - data/features
⚙️ Expand to add more stages.
Let's add the training itself. Nothing new this time; just the same dvc run command with the same set of options:

dvc stage add -n train \
                -p train.seed,train.n_est,train.min_split \
                -d src/train.py -d data/features \
                -o model.pkl \
                python src/train.py data/features model.pkl
Please check the dvc.yaml again, it should have one more stage now.

This should be a good time to commit the changes with Git. These include .gitignore, dvc.lock, and dvc.yaml — which describe our pipeline.

Reproduce
The whole point of creating this dvc.yaml file is the ability to easily reproduce a pipeline:

dvc repro
⚙️ Expand to have some fun with it.
Let's try to play a little bit with it. First, let's try to change one of the parameters for the training stage:

Open params.yaml and change n_est to 100, and
(re)run dvc repro.
You should see:

dvc repro
Stage 'prepare' didn't change, skipping
Stage 'featurize' didn't change, skipping
Running stage 'train' with command: ...
DVC detected that only train should be run, and skipped everything else! All the intermediate results are being reused.

Now, let's change it back to 50 and run dvc repro again:

dvc repro
Stage 'prepare' didn't change, skipping
Stage 'featurize' didn't change, skipping
As before, there was no need to rerun prepare, featurize, etc. But this time it also doesn't rerun train! The previous run with the same set of inputs (parameters & data) was saved in DVC's run-cache, and reused here.

💡 Expand to see what happens under the hood.



DVC pipelines (dvc.yaml file, dvc stage add, and dvc repro commands) solve a few important problems:

Automation: run a sequence of steps in a "smart" way which makes iterating on your project faster. DVC automatically determines which parts of a project need to be run, and it caches "runs" and their results to avoid unnecessary reruns.
Reproducibility: dvc.yaml and dvc.lock files describe what data to use and which commands will generate the pipeline results (such as an ML model). Storing these files in Git makes it easy to version and share.
Continuous Delivery and Continuous Integration (CI/CD) for ML: describing projects in way that can be reproduced (built) is the first necessary step before introducing CI/CD systems. See our sister project CML for some examples.
Visualize
Having built our pipeline, we need a good way to understand its structure. Seeing a graph of connected stages would help. DVC lets you do so without leaving the terminal!

dvc dag
         +---------+
         | prepare |
         +---------+
              *
              *
              *
        +-----------+
        | featurize |
        +-----------+
              *
              *
              *
          +-------+
          | train |
          +-------+
Refer to dvc dag to explore other ways this command can visualize a pipeline.
```
```
git branch testing
```


