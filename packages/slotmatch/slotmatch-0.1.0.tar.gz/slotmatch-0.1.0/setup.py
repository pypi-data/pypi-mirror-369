from setuptools import setup, find_packages

setup(
    name='slotmatch',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Extract structured key-value pairs from unstructured LLM output using regex, fuzzy matching, and schema validation.',
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',
    url='https://huggingface.co/GenAIDevTOProd',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[],
)