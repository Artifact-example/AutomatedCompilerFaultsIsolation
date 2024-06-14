# Supplementary code for paper: Automated Compiler Faults Isolation: How Far We Have Progressed?

## Table of Contents

* [Description](#description)
* [Usage](#usage)
* [Result](#result)

## Description

This test case is extracted from the GCC Bugzilla, with the bug ID [114551](https://gcc.gnu.org/bugzilla/show_bug.cgi?id=114551). It exhibits different behaviors at optimization levels `-O2` and `-O3`. At the `-O2` level, the executable behaves as expected, whereas at the `-O3` level, the executable leads to a `Segmentation fault`. The provided artifacts include the source file `114551.c`.

We take the bug-triggering test program `114551.c` as an example to demonstrate the usage of our artifact. To investigate a specific bug, our process involves the following steps:

* We employ `CompilerExplorer-post.py` to identify the GCC releases that exhibit the bug.
* From the identified releases, we select the two closest release versions, the former contains this bug and the latter does not contain this bug.
* Finally, we use `bisect.py`to pinpoint the exact commit that induced this bug.

## Usage

1. The Python script in `install-basic-gcc-revisions.py` installs basic gcc branch revisions such as gcc-15.0.0, gcc-14.0.0, gcc-13.0.0, gcc-12.0.0 and gcc-11.0.0 in local machine. 


```sh
python3 install-basic-gcc-revisions.py

```

2. The Python script in `CompilerExplorer-post.py` uses the Compiler-Explorer REST API to examine whether those compiler versions pass or fail on the bug-triggering test program. The following command will examine each of the list compiler versions will pass on the bug-triggering test program of `114551.c`: 

```sh
python3 CompilerExplorer-post.py

```

3. The Python script in `bisect.py` uses the git bisect to determine the specific commit of the compiler that introduced the corresponding bug. The following command will perform a binary search to identify the corresponding bug-inducing commit for bug [114551](https://gcc.gnu.org/bugzilla/show_bug.cgi?id=114551):


```sh
python3 bisect.py

```

## Result

By running `python3 bisect.py`, you can identify the specific commit hash responsible for the Segmentation fault at the -O3 optimization level for the bug described in GCC Bugzilla ID 114551.
