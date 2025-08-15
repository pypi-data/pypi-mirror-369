from setuptools import setup


with open("README.md") as f:
    readme = f.read()

setup(
    name="vpype-singlestroke",
    version="0.2.0",
    description="vpype plugin to convert closed paths to single-stroke open paths",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Dominik Lang",
    url="https://github.com/d-n-l-lab/singlestroke",
    packages=["singlestroke"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Topic :: Multimedia :: Graphics",
        "Environment :: Plugins",
    ],
    setup_requires=["wheel"],
    install_requires=[
        "vpype>=1.9,<2.0",
        "click",
        "numpy",
    ],
    entry_points='''
            [vpype.plugins]
            singlestroke=singlestroke.singlestroke:singlestroke
        ''',
)
