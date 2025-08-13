"""
Example Python file for testing vibe_python
"""

# Simple calculations
x = 10
y = 20
result = x + y
print(f"The sum of {x} and {y} is {result}")

# List operations
numbers = [1, 2, 3, 4, 5]
squared = [n**2 for n in numbers]
print(f"Original numbers: {numbers}")
print(f"Squared numbers: {squared}")

# Function definition and call
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

fact_5 = factorial(5)
print(f"Factorial of 5 is {fact_5}")

# Exception handling
try:
    division = 10 / 2
    print(f"10 / 2 = {division}")
    
    # This will not cause an error
    safe_division = 10 / 1
    print(f"10 / 1 = {safe_division}")
except ZeroDivisionError:
    print("Cannot divide by zero!")

print("Example execution completed successfully!")