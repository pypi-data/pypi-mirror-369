from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tux-gpt",
    version="0.1.7",
    description=(
        "An interactive terminal tool using GPT, "
        "with web search capabilities."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Fábio Berbert de Paula",
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=[
        'openai>=0.27.0',
        'prompt-toolkit>=3.0.0',
        'rich>=10.0.0'
    ],
    extras_require={
        'dev': [
            'pytest',
            'mypy',
            'flake8',
        ],
    },
    entry_points={
        'console_scripts': [
            'tux-gpt=tux_gpt.tux_gpt:main'
        ]
    }
)
