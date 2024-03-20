# AI Singapore Online Safety Prize Challenge Submission Guide

Participants must submit a **compressed Docker container in the tar.gz format** via the [challenge platform](https://ospc.aisingapore.org/). This repository serves as a step-by-step guide to help participants create a valid submission for the Online Safety Prize Challenge.

While the proper term for the Docker generated artefacts is "Docker images", we will use the term "Docker container" instead to disambiguate it from the [computer] images that serve as input to the challenge.

## Getting Started

We are using Docker for this challenge so that participants can choose their preferred programming languages and open source dependencies to create the best performing detection models.

To build and run GPU accelerated Docker containers, please install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) in your development environment.

## Technical Details

### Hardware/Software Specifications

All participants' compressed Docker containers will be executed on virtual machines with the following resource allocation:

| vCPU | Mem (GB) | GPU            | tmpfs (GiB) |
|------|----------|----------------|-------------|
| 6    | 60       | V100 16GB VRAM | 5           |

This will be reflected in the `docker run` command options. Participants may specify different settings for their own testing purposes, but these will not be reflected in the official run-time environment for scoring.

The general software specification
* Instruction Set: x86-64
* Ubuntu 22.04
* NVIDIA Driver Version: 535
    * CUDA 11.x-12.x
    * Check for [CUDA - NVIDIA Driver Compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/)
* Docker Version: 24.0.7
* NVIDIA Container Toolkit: 1.14.4-1

**IMPORTANT NOTE**: The following instructions relating to Docker assumes our general software specification. 

### Submission Specification Guidelines
This section will cover the following important guidelines on building your solution for submission:

1. A brief overview of the dataset;
1. The required input format for your submitted Docker container and the output format from it;
1. The maximum resources of a Docker container for each submission;
1. The performance metrics for this challenge;
1. Instructions on how to run this repository and create your own submission.


#### Dataset, Input, Output

##### Dataset:

The dataset comprises about 1700 images in PNG format with file extension `.png`. The directory containing the dataset will be mounted to your Docker container as read-only at the mount point of `/images`.

##### Input to Docker Container:

Your solution must use `stdin`, where each line from `stdin` corresponds to a file path to a single image. This simulates a real-world situation where your solution is called on a per-image basis. An example of a line of input from `stdin` might look like `/images/9ad157be-f32f-4770-b409-8c4650478f5b.png` .

Further details on how this is done for a Python-based Docker solution can be found in [Usage of sample submission](#usage-of-sample-submission) and [Creating your own submission](#creating-your-own-submission).

##### Output (`stdout`, `stderr`) to Container:

###### Solution output: `stdout`

Your solution must use `stdout` to output the result of your analysis for each line of input from `stdin`.

The output format per line of input of `stdin` must include:
* The probability that the meme is harmful with 4 decimal places of precision. We will refer to this as `proba`.
* An integer, where `1` is output if the meme is deemed harmful, and `0` if it is benign. We will refer to this as `label`.

Both predictions must be separated by a single tab character (`\t`), and terminated with a single new line character (`\n`).

Examples of implementation for the formatting of one line of output in Python can be seen below.

```
# Example 1:
output = f"{proba:.4f}\t{label}\n"

# Example 2 (more C-like)
output = "%.4f\t%d\n" % (proba, label)

sys.stdout.write(output)
```

Below shows an example of how `stdout` will look like after having processed (in this case) 5 lines of input from `stdin`:

```
0.8232	1
0.7665	1
0.3241	0
0.1015	0
0.9511	1
```

Further details on how this is done for a Python-based Docker solution can be found in [Usage of sample submission](#usage-of-sample-submission) and [Creating your own submission](#creating-your-own-submission).

Remember that there has to be one output format conforming line in `stdout` for every input line from `stdin`. Please do not attempt to skip any.

**_Failure to do so may result in inaccurate scoring of your results._**

###### Logging output: `stderr`

Your solution must use `stderr` for the writing of any logs to assist you in determining any programming errors within your solution. Logs have an implied file size limit to prevent abuse. Failure to keep within this limit through excessive logging will result in an error in your solution.

Further details on how this is done for a Python-based Docker solution can be found in [Usage of sample submission](#usage-of-sample-submission) and [Creating your own submission](#creating-your-own-submission).

**_Non-compliance may result in premature termination of your solution with a Resource Limit Exceeded error._**

Logs may be obtained only on a case-by-case basis. Requests can be made over at the discussion board, but the fulfilment of the request shall be at the discretion of the organisers.


#### Performance Metric Details

The performance metrics used are Area Under the Curve of the Receiver Operating Characteristic (**_AUROC_**) and **_accuracy_**. Both metrics will be displayed on the leaderboard.

1. The `proba` output is used to calculate **_AUROC_** and used to determine your ranking on the leaderboard.
1. The `label` output is used to calculate **_accuracy_**, and used as secondary metric in the event of a tie.


#### Docker Container Details

##### Max Docker Container Size
Your solution upon saving [using docker save](#compress-your-docker-container-to-targz-format-using-docker-save) must not exceed the maximum file size of 25 GiB.

##### Max Docker Container Runtime
Your solution must not exceed 2.5 hours of runtime to process around 1700 images.

##### Submitted Docker Container Isolation
All submitted Docker containers are executed in a network isolated environment where there is no internet connectivity, nor access to any other external resources or data beyond what the container has.

As such, your solution must have all necessary modules, model weights, and other non-proprietary dependencies pre-packaged in your Docker container.

**_Non-compliance will result in your Docker container facing issues/error when in operation._**

## Example: Usage of sample submission
### Pre-condition: Create the isolated Docker network
Before trying out the [sample submission](#usage-of-sample-submission) or [creating your own submission](#creating-your-own-submission), you will need to create a local Docker network to simulate the environment setup for the execution of solutions.

Run the following command to create your own isolated Docker network. If it is already created, as indicated by the output of `docker network ls`, you can skip this step.

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
git clone https://github.com/AISG-Technology-Team/AISG-Online-Safety-Challenge-Submission-Guide.git
```

### Change into the sample submission (`sample_submission`) directory

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

Please ensure you are in the parent directory of `sample_submission` before executing the following command. The `$(pwd)` command in the `--mount` option yields the current working directory. The test is successful if no error messages are seen and a `stdout.csv` is created in the `local_test/test_output` directory.

Alter the options for `--cpus`, `--gpus`, `--memory` to suit the system you are using to test.

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
    python3 sample_submission/main.py \
        1>local_test/test_output/stdout.csv \
        2>local_test/test_output/stderr.csv
```

### (Optional) Adding own images
You can add a few more custom images (of the PNG format with file extension `.png`) into `local_test/test_images`. After doing that, you can regenerate the `stdin.csv` located in `local_test/test_stdin` using the following command.

```
cd utils

# Using the default location for the test_images and output_folder for storing stdin.csv
python3 gen_input.py --img_folder ../local_test/test_images --output_folder ../local_test/test_stdin
```

You can then re-run the [Test sample Docker container locally](#test-sample-docker-container-locally)

### Compress your sample container to `.tar.gz` format using [`docker save`](https://docs.docker.com/engine/reference/commandline/save/)

```
docker save sample_container:latest | gzip > sample_container.tar.gz
```

### Upload container

The final step would be to submit the compressed Docker container file (`sample_container.tar.gz` in this example) on to the challenge platform, but since this is only the sample with no actual logic, we will *not* do so.

Please note that if you do submit this sample, it will still take up one count of your submission quota.


## Example: Creating your own submission

The process of creating your own submission would be very similar to using the aforementioned sample submission.

### Create a project directory and navigate into it

```
mkdir Online-Safety-Challenge && cd Online-Safety-Challenge
```

### Create a main file

The main file has to be able to interact with standard streams such as `stdin`, `stdout`, and `stderr`.

In general, the main file should have the following characteristics:

1. Read the PNG images from the file paths obtained from `stdin` (one file path per input line);
1. Predict the probability that the image is a harmful meme, up to 4 decimal places (`proba` as referred to in the [Submission Specification Guidelines](#submission-specification-guidelines));
1. Decide if the image is a harmful meme (`1`), or a benign meme (`0`) (`label` as referred to in the [Submission Specification Guidelines](#submission-specification-guidelines));
1. Output a single line with to `stdout` for each line of `stdin` conforming to the [Submission Specification Guidelines](#submission-specification-guidelines);
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

#### 3. Add test images (PNG format with file extension `.png`) into `test_images` directory

#### 4. Generate the input file (`.csv`).

You can use the following script `utils/gen_input.py` in this guide to generate the `stdin.csv` which will be used as the source for `stdin`.

```
# Using the default location for the test_images and output_folder for storing stdin.csv
python3 gen_input.py --image_folder ../local_test/test_images --output_folder ../local_test/test_stdin
```

The script will create a `stdin.csv` file within `local_test/test_stdin` which will be used as the source of input for `stdin` for your Docker container.

#### 5. Test your container using [`docker run`](https://docs.docker.com/engine/reference/run/)

Please ensure you are in the parent directory before executing the following command. The `$(pwd)` command in the `--mount` option yields the current working directory. The test is successful if no error messages are seen and a `stdout.csv` is created in the `local_test/test_output` directory.

Alter the options for `--cpus`, `--gpus`, `--memory` to suit the system you are using to test.

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
        your_container \
 1>local_test/test_output/stdout.csv \
 2>local_test/test_output/stderr.csv
```

### Compress your Docker container to `.tar.gz` format using [`docker save`](https://docs.docker.com/engine/reference/commandline/save/)

```
docker save your_container:latest | gzip > your_container.tar.gz
```

### Upload your container

Submit your `your_container.tar.gz` file onto the [challenge platform](https://ospc.aisingapore.org/). Please note that when you do this, it will take up one count of your submission quota.
