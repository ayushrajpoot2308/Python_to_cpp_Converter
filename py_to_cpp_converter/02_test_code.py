# Multiply function
def multiply(a, b):
    return a * b

# Assign values
num1 = 6
num2 = 7

# Call function
product = multiply(num1, num2)

# Print result
print("Product is", product)

# Conditional
if product > 40:
    print("High value")
else:
    print("Low value")

# While loop
w = 1
while w <= 3:
    print("While loop value:", w)
    w = w + 1

# For loop with range
for i in range(4):
    print("Index from range:", i)

# List and for-each
marks = [80, 90, 75]
for m in marks:
    print("Mark:", m)

# More expressions
total = num1 + num2 + product
print("Total sum is", total)
