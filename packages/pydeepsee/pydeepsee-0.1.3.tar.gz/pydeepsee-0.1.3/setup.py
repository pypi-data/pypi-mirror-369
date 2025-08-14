from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    description = f.read()
setup(
 name= 'pydeepsee',
 version='0.1.3',
 packages=find_packages(),
 install_requires=[
    "opencv-python>=4.5.0",
    "numpy>=1.21.0"
 ],
  long_description=description,
  long_description_content_type='text/markdown'
)