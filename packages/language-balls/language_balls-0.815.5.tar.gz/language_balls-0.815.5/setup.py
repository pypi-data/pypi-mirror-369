from setuptools import setup, find_packages

setup(
    name="language-balls",
    version="0.815.5",
    description="Animated language balls moving at different periods",
    author="Emrah Diril",
    author_email="emrah@diril.org",
    packages=["language_balls"],
    package_data={"language_balls": ["logos.jpeg"]},
    install_requires=[
        "dearpygui==1.11.1",
    ],
    entry_points={
        "console_scripts": [
            "language-balls=language_balls:main",
        ],
    },
    python_requires=">=3.9",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)