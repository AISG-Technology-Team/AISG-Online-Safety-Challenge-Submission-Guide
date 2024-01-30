# AI Singapore Online Safety Prize Challenge Submission Guide

Participants must submit a **compressed Docker container in the tar.gz format** via the [challenge platform](https://ospc.aisingapore.org/).  This repository serves as a step by step guide to help participants with creating a valid submission for the Online Safety Prize Challenge.

## Getting Started

We are using Docker for this challenge so that participants can choose their preferred programming languages and open source dependencies to create the best performing detection models.

While the proper term for the Docker generated artefacts is "Docker images", we will use the term "Docker container" instead to disambiguate it from the [computer] images that serve as input to the challenge.

To build and run GPU accelerated Docker containers, please install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) in your development environment.

## Important Notice

### Hardware/Software Specifications

All participants' compressed Docker containers will be executed on virtual machines with the following resource allocation:

| vCPU | Mem (GB) | GPU            | tmpfs (GiB) |
|------|----------|----------------|-------------|
| 6    | 60       | V100 16GB VRAM | 5           |

This will be reflected in the `docker run` command options. Participants may specify different settings for their own testing purposes, but these will not be reflected in the official run-time environment for scoring.

The general software specification
* Ubuntu 22.04
* NVIDIA Driver Version: 535.129.03
    * CUDA 11.x-12.x
    * Check for [CUDA - NVIDIA Driver Compatability](https://docs.nvidia.com/deploy/cuda-compatibility/)


### Execution Guidelines
This section will cover several important guidelines on building your solution for submission.

>**Note 1: Use `stdin` as input and `stdout` as output**
>
> Your solution must use `stdin`, where each line from `stdin` is a mounted file path to a single image. This simulates a real-world situation whereby your solution will be called on a per-image basis. Further details on how this is done for a Python Docker solution is detailed [Usage of sample submission](#usage-of-sample-submission) and [Creating your own submission](#creating-your-own-submission)
>
>
> Your solution must use `stdout`, to output the result of your analysis for each `stdin` (represents a single image filepath). Your output must be either a `1` or `0`; representing `harmful` or `not harmful`. Further details on how this is done for a Python Docker solution is detailed [Usage of sample submission](#usage-of-sample-submission) and [Creating your own submission](#creating-your-own-submission).
>
> For each line of text from `stdin` that is piped into your solution, there needs to be a corresponding output line conforming to the output standards piped to `stdout`. Please do not attempt to skip any.
>
> **_Failure to do so may result in inaccurate scoring of your results._**

>**Note 2: Ensure you DO NOT ATTEMPT to "over log" (`stderr`)**
>
> Your solution must use `stderr` for the writing of any logs to assist you in determining any programming errors within your solution. Take note that logs are given  a file size limit. Failure to follow this limit by logging excessively will result in an error in your solution.
>
> Further details on how this is done for a Python Docker solution can be found in [Usage of sample submission](#usage-of-sample-submission) and [Creating your own submission](#creating-your-own-submission)
>
> **_Non-compliance may result in premature termination of your solution with a Resource Limit Exceeded error._**

>**Note 3: Max Docker Container Size**
>
> Your solution upon saving [using docker save](#compress-your-docker-container-to-targz-format-using-docker-save) must not exceed the maximum filesize of 25 GiB.
>

>**Note 4: Max Docker Container Runtime**
>
> Your solution must not exceed 2.5 hours of runtime to process around 1700 images.
>
> **_Non-compliance will result in a Time Limit Exceeded error._**


>**Note 5: Submitted Docker Container Isolation**
>
> Your solution must have all its necessary modules, model weights, etc pre-packaged in your Docker container. This is because there will be a multi-layered network isolation to ensure your Docker container is isolated without internet connectivity or the ability to access external resources or data.
>
> **_Non-compliance will result in your Docker container facing issues/error when trying to access external resources._**


## Usage of sample submission

### Pre-condition: Create the isolated Docker network
Before participants try out using the [sample submission](#usage-of-sample-submission) or go on to [create your own submission](#creating-your-own-submission), they need to create a local Docker network to simulate the environment setup for the execution of solutions.

Run the following command to create your own isolated Docker network. If it is already created, you can skip this step.

```
ISOLATED_DOCKER_NETWORK_NAME=exec_env_jail_network
ISOLATED_DOCKER_NETWORK_DRIVER=bridge
ISOLATED_DOCKER_NETWORK_INTERNAL=true
ISOLATED_DOCKER_NETWORK_SUBNET=172.20.0.0/16

docker network create \
    --driver "$ISOLATED_DOCKER_NETWORK_DRIVER" \
    $( [ "$ISOLATED_DOCKER_NETWORK_INTERNAL" = "true" ] && echo "--internal" ) \
    --subnet "$ISOLATED_DOCKER_NETWORK_SUBNET" \
    "$ISOLATED_DOCKER_NETWORK_NAME"
```

### Clone this repository and navigate to it

```
git clone https://github.com/AISG-Technology-Team/xxxxxxx.git
```

### Change into the sample submission directory

```
cd sample_submission
```

### Build the sample Docker container

You can add a `--no-cache` option in the `docker build` command to force a clean rebuild.

```
docker build -t sample_container .
```

_Please take note that the "`.`" indicates the current working directory and should be added into the `docker build` command to provide the correct build context._

### Test sample Docker container locally

Please ensure you are in the parent directory before executing the following command. The `$(pwd)` command in the `--mount` option yields the current working directory. The test is successful if no error messages are seen and a `stdout.csv` is created in the `local_test/test_output` directory.

Alter the options for `--cpus`, `--gpus`, `--memory` to suit the system you are using to test.

Ensure that you are not in the main project directory and not in `sample_submission` directory before you execute the command below.
```
ISOLATED_DOCKER_NETWORK_NAME=exec_env_jail_network

cat local_test/test_stdin/stdin.csv | \
docker run --init \
        --attach "stdin" \
        --attach "stdout" \
        --attach "stderr" \
        --cpus 2 \
        --gpus "device=0" \
        --memory 4g \
        --memory-swap 0 \
        --ulimit nproc=1024 \
        --ulimit nofile=1024 \
        --network exec_env_jail_network \
        --read-only \
        --mount type=bind,source="$(pwd)"/local_test/test_images,target=/images,readonly \
        --mount type=tmpfs,destination=/tmp,tmpfs-size=5368709120,tmpfs-mode=1777 \
        --interactive \
        sample_container \
 1>local_test/test_output/stdout.csv \
 2>local_test/test_output/stderr.csv
```
_Please note that the above `docker run` command would be equivalent to running the following command locally:_

```
cat local_test/test_stdin/stdin.csv | \
    python3 sample_submission/main.py  \
        1>local_test/test_output/stdout.csv \
        2>local_test/test_output/stderr.csv
```

### (Optional) Adding own images
You can add a few more custom meme images (`.png`) into `local_test/test_images`. After doing that, you can regenerate the `stdin.csv` located in `local_test/test_stdin` using the following command.
```
cd utils

# Using the default location for the test_images and output_folder for storing stdin.csv
python3 gen_input.py --image_folder ../local_test/test_images --output_folder ../local_test/test_stdin
```

You can then re-run the [Test sample Docker container locally](#test-sample-docker-container-locally)

### Compress your sample container to `.tar.gz` format using [`docker save`](https://docs.docker.com/engine/reference/commandline/save/)

```
docker save sample_container:latest | gzip > sample_container.tar.gz
```

### Upload sample container

Submit your `sample_container.tar.gz` file onto the [challenge platform](https://ospc.aisingapore.org/). Please note that if you do this, it will take up one count of your submission quota.


## Creating your own submission

The process of creating your own submission would be very similar to using the aforementioned sample submission.

### Create a project directory and navigate into it

```
mkdir Online-Safety-Challenge && cd Online-Safety-Challenge
```

### Create a main file

The main file has to be able to interact with standard streams such as `stdin`, `stdout`, and `stderr`.

<!-- - `-input` is a directory which contains all videos of the test set, e.g. /images/ ('/' should appear at the end of the line)
- `-output` is the name (with path) of the output file, e.g. /data/output/submission.csv -->

In general, the main file should have the following characteristics:

1. Read the PNG images from the file paths obtained from `stdin` (file path per line);
1. Predict whether each input meme image is `0` for benign, or `1` for harmful;
1. Output a single prediction per line of `stdout` for each line of `stdin`, using `\n` as the line separator;
1. Use `stderr` to log any necessary exceptions/errors.

>**Note:**
>
> Please ensure that the prediction output to `stdout` is in the same order as the `stdin` because the order in which `stdout` is assessed strictly follows the order of the input from `stdin`.
>
> You must use `/tmp` within your Docker container for any temporary files for processing. This is because the Docker container will be executed with the options:
> - `--read-only` which sets the root file-system as read only.
> - `--tmpfs /tmp` which sets a fixed `/tmp` directory for any app to write to.


You may refer to the [`main.py`](sample_submission/main.py) of the sample submission as an example of a main file.

### Create a `Dockerfile`

You may use the [sample `Dockerfile`](sample_submission/Dockerfile) provided for you. However, please install the relevant dependencies required for your detection model. Additionally, you may wish to change the `ENTRYPOINT` if you are using another main file or if you prefer to use a shell script:

```
ENTRYPOINT ["bash","/path/to/your/main.sh"]
```

_If you are not familiar with how to build a `Dockerfile`, please refer to the [official documentation](https://docs.docker.com/engine/reference/builder/) for more information._

### Build your Docker container using [`docker build`](https://docs.docker.com/engine/reference/commandline/build/)

```
docker build -t your_container .
```

_Please take note that the "`.`" indicates the current working directory and should be added into the `docker build` command to provide the correct build context._

### Test your Docker container locally

#### 1. Create a test directory outside of your project directory

```
mkdir local_test && cd local_test
```

#### 2. Create input and output directory within your test directory

```
mkdir test_images test_output
```

#### 3. Add test meme images (`.png`) into `test_images` directory

#### 4. Generate the input file (`.csv`).

You can use the following script `utils/gen_input.py` in the AISG-Online-Safety-Challenge-Submission-Guide to generate the `stdin.csv` which will be used as the source for `stdin`.

```
# Using the default location for the test_images and output_folder for storing stdin.csv
python3 gen_input.py --image_folder ../local_test/test_images --output_folder ../local_test/test_stdin
```

The script will create a `stdin.csv` file within `local_test/test_stdin` which will be used as the input for your Docker container.

#### 5. Test your container using [`docker run`](https://docs.docker.com/engine/reference/run/)

Please ensure you are in the parent directory before executing the following command. The `$(pwd)` command in the `--mount` option yields the current working directory. The test is successful if no error messages are seen and a `stdout.csv` is created in the `local_test/test_output` directory.

Alter the options for `--cpus`, `--gpus`, `--memory` to suit the system you are using to test.

```
cat local_test/test_stdin/stdin.csv | \
docker run --init \
        --attach "stdin" \
        --attach "stdout" \
        --attach "stderr" \
        --cpus 2 \
        --gpus "device=0" \
        --memory 4g \
        --memory-swap 0 \
        --ulimit nproc=1024 \
        --ulimit nofile=1024 \
        --network exec_env_jail_network \
        --read-only \
        --mount type=bind,source="$(pwd)"/local_test/test_images,target=/images,readonly \
        --mount type=tmpfs,destination=/tmp,tmpfs-size=5368709120,tmpfs-mode=1777 \
        --interactive \
        your_container \
 1>local_test/test_output/stdout.csv \
 2>local_test/test_output/stderr.csv
```


### Compress your Docker container to `.tar.gz` format using [`docker save`](https://docs.docker.com/engine/reference/commandline/save/)

```
docker save your_container:latest | gzip > your_container.tar.gz
```

### Upload your container

Submit your `your_container.tar.gz` file onto the [challenge platform](https://ospc.aisingapore.org/). Please note that if you do this, it will take up one count of your submission quota.
