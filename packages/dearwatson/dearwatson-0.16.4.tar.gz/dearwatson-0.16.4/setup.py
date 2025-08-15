import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version = "0.16.4"
setuptools.setup(
    name="dearwatson", # Replace with your own username
    version=version,
    author="M. Dévora-Pajares",
    author_email="mdevorapajares@protonmail.com",
    description="Visual Vetting and Analysis of Transits from Space ObservatioNs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PlanetHunters/watson",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
    install_requires=[
                        'arviz==0.21.0', # Validation required (pytransit, from triceratops)
                        "bokeh==3.7.3", # TPFPlotter dependency
                        'configparser==5.0.1',
                        "extension-helpers==0.1",
                        "exoml==1.2.6",
                        "imageio==2.9.0",
                        "openai==1.30.1",
                        'pdf2image==1.16.2', #Triceratops
                        'pyparsing==2.4.7', # Matplotlib dependency
                        "pyyaml==6.0.1",
                        "pillow==11.2.1",
                        'pytransit==2.6.14', #Triceratops
                        "reportlab==4.4.0",
                        'setuptools>=41.0.0',
                        'triceratops==1.0.19'
    ]
)
