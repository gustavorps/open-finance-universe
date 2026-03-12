import sys

module = sys.modules[__name__]
print(f"{module.__package__} package")
