from setuptools import setup, find_packages

setup(
    name='scam_cgm',
    version='0.1.0',
    description='A Python package for SCAM CGM analysis',
    author='Kaveri',  
    author_email='neelikaveri3@gmail.com',  # ← replace with your email
    url='https://github.com/Kaveri1950/scam_cgm',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
