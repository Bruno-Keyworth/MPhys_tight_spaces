import os
import matplotlib.pyplot as plt
import numpy as np

# Path to your folder
folder_path = '/Volumes/Transcend/2025-26 MPhys Project/ball5/200mbar'

# Lists to hold the data
indices = []
decimal_values = []

# Iterate through all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".tiff"):
        # Example filename: 00000001_000000000095FDC4.tiff
        name, _ = os.path.splitext(filename)
        index_str, hex_str = name.split("_")

        # Convert to int
        index = int(index_str)
        decimal_value = int(hex_str, 16)  # Convert hexadecimal to decimal

        indices.append(index)
        decimal_values.append(decimal_value)

# Sort by index, just in case
indices, decimal_values = zip(*sorted(zip(indices, decimal_values)))

min_val = min(decimal_values)
new_decimal_values = [v - min_val for v in decimal_values]

# Plot
plt.plot(new_decimal_values, indices, marker='o')
plt.ylabel("Photo Number")
plt.xlabel("Time (ms)")
plt.title("Index vs Converted Hexadecimal Value")
plt.grid(True)
plt.savefig('../plots/frame_rate.png', dpi=300)
plt.show()