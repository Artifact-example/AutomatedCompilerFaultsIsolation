# Supplementary code for paper: Automated Compiler Faults Isolation: How Far We Have Progressed?

## Table of Contents
- Install
- Usage
- Result

## Description

```114551.c```

This test case is extracted from the GCC Bugzilla, with the bug ID [114551](https://gcc.gnu.org/bugzilla/show_bug.cgi?id=114551). It exhibits different behaviors at optimization levels -O2 and -O3. At the -O2 level, the executable produces no output, whereas at the -O3 level, it outputs "Segmentation fault."

```CompilerExplorer-post.py```

This script calls the godbolt API to get the behavior of a given program on the corresponding compiler release version.

```bisect.py```

This script uses git bisect to determine the specific commit of the compiler that introduced the corresponding bug.

```install-basic-gcc-revisions.py```

This script is used to install basic gcc revision such as gcc-15.0.0, gcc-14.0.0, gcc-13.0.0, gcc-12.0.0 and so on.

## Usage

We take the ```114551.c``` file as an example to demonstrate the usage of our artifact. To investigate a specific bug, our process involves the following steps:
- We employ ```CompilerExplorer-post.py``` to identify the GCC releases that exhibit the bug.
- From the identified releases, we select the two closest release versions, the former contains this bug and the latter does not contain this bug.
- Finally, we use ```bisect.py```to pinpoint the exact commit that induced this bug.

## Result

The ```bisect.py``` script will output the hash id of which commit induced the bug.
