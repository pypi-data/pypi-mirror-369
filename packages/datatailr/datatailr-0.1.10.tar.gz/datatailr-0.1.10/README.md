<div style="text-align: center;">
  <a href="https://www.datatailr.com/" target="_blank">
    <img src="https://s3.eu-west-1.amazonaws.com/datatailr.com/assets/datatailr-logo.svg" alt="Datatailr Logo" />
  </a>
</div>

---

**Datatailr empowers your team to streamline analytics and data workflows
from idea to production without infrastructure hurdles.**

# What is Datatailr?

Datatailr is a platform that simplifies the process of building and deploying data applications.

It makes it easier to run and maintain large-scale data processing and analytics workloads.

## What is this package?
This is the Python package for Datatailr, which allows you to interact with the Datatailr platform.

It provides the tools to build, deploy, and manage batch jobs, data pipelines, services and analytics applications.

Datatailr manages the underlying infrastructure so your applications can be deployed in an easy, secure and scalable way.

## Installation

### Installing the `dt` command line tool
Before you can use the Datatailr Python package, you need to install the `dt` command line tool.
**[INSTALLATION INSTRUCTIONS FOR DATATAILR GO HERE]**

### Installing the Python package
You can install the Datatailr Python package using pip:
```bash
pip install datatailr
```

### Testing the installation
```python
import datatailr

print(datatailr.__version__)
print(datatailr.__provider__)
```


## Quickstart
The following example shows how to create a simple data pipeline using the Datatailr Python package.

```python
from datatailr.scheduler import batch, Batch

@batch()
def func_no_args() -> str:
    return "no_args"


@batch()
def func_with_args(a: int, b: float) -> str:
    return f"args: {a}, {b}"

with Batch(name="MY test DAG", local_run=True) as dag:
    for n in range(2):
        res1 = func_no_args().alias(f"func_{n}")
        res2 = func_with_args(1, res1).alias(f"func_with_args_{n}")
```

Running this code will create a graph of jobs and execute it.
Each node on the graph represents a job, which in turn is a call to a function decorated with `@batch()`.

___
Visit [our website](https://www.datatailr.com/) for more!
