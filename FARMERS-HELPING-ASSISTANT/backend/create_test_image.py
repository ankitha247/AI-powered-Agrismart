# create_test_image.py
from PIL import Image
import os

# Create a simple test image
img = Image.new('RGB', (100, 100), color='green')
img.save('test.jpg')
print("✅ Created test.jpg")