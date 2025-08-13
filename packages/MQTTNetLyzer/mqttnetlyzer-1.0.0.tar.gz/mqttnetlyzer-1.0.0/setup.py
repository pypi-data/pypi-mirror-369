from setuptools import setup, find_packages

with open(file="README.md", mode="r", encoding="utf8") as fh:
    long_description = fh.read()

setup(
    name='MQTTNetLyzer',
    version='1.0.0',
    author="Aditya Raj",
    author_email="adityaraj867604@gmail.com",
    description="The MQTT Layer Session Analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adityaraj218/MQTTNetLyzer",
    packages=find_packages(),
    include_package_data=True,
    license='GPLv3',
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "scapy==2.5.0",
    ],
    entry_points={
        'console_scripts': [
            'mqttnetlyzer=MQTTNetLyzer.main:main',
        ],
    },
)

