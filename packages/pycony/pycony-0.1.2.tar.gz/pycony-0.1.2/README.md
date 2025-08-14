# pyCony
pyCony is a small utility package for python projects debugging, reverse engineering and tracing 

## Installation
```shell
pip install pyCony  
#    OR 
pip install pip install git+https://github.com/rzbhatti/pyCony.git
```
## Usage
```python
from pycony import *
```


## Functions
- open_console()
- print_stack(depth=None)
- pickle_args(n, pkl_sufix=None, file_path=None)
- load_pickled_args(file_path)
- open_console_print_stack(depth=None)
- **[Optional]** set_trace() --> https://docs.python.org/3/library/pdb.html

# Example 1
```python 
from pycony import open_console_show_stack_depth

def my_function(arg):
    value = arg * 5
    print(f"Inside my_function with value: {value}")
    open_console_print_stack(depth=2)
    print("Back in my_function")

my_function(10)
```

# Example 2

```shell
python test/test.py 
```
### ouput

```shell
Inside outer_function, local_outer: 15
Inside inner_function, local_inner: 30
=========================  Interactive Console: Stack  =========================
  1. Function: outer_function
     Arguments:
       x = 10
       local_outer = 15
================================================================================
  2. Function: inner_function
     Arguments:
       y = 15
       z = 2
       local_inner = 30
================================================================================
Use Ctrl+D (or quit()) to exit and resume program flow.
 Use pickle_args(n, file_path) to dump the args
>>> 
now exiting InteractiveConsole...
Back in inner_function
Back in outer_function
Program finished.
```




