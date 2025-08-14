from pycony import open_console

if __name__ == "__main__":
    global_value = "Global Value"

    def inner_function(y, z=3):
        local_inner = y * z
        print(f"Inside inner_function, local_inner: {local_inner}")
        open_console("inner_function")
        print("Back in inner_function")

    def outer_function(x):
        local_outer = x + 5
        open_console("outer_function before inner_function")
        print(f"Inside outer_function, local_outer: {local_outer}")
        inner_function(local_outer, z=2)
        open_console("outer_function after inner_function")
        print("Back in outer_function")

    outer_function(10)
    print("Program finished.")
