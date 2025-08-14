from setuptools import setup, find_packages
 

with open('README.md', 'r') as f:
    description = f.read()
setup(
    name= "aco_tsp", version='0.1',packages=find_packages(),
    install_requires=['numpy>=2.2.6'],
     long_description=description,
     long_description_content_type='text/markdown'
)