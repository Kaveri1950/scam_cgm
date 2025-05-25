from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='scam_cgm',
    version='0.1.0',  
    description='A Python package for SCAM CGM analysis',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Kaveri',  
    author_email='neelikaveri3@gmail.com',
    url='https://github.com/Kaveri1950/scam_cgm',
    packages=find_packages(include=['scam_cgm*']),
    include_package_data=True,            
    install_requires=[
        'numpy>=1.21.0', 
        'matplotlib>=3.5.0',
    ],
    python_requires='>=3.8', 
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords='astronomy astrophysics CGM',
    project_urls={
        'Bug Reports': 'https://github.com/Kaveri1950/scam_cgm/issues',
        'Source': 'https://github.com/Kaveri1950/scam_cgm',
    },
)
