import os.path

from setuptools import setup, find_packages
from pathlib import Path
import re

# ========== Configuration Variables ==========
# Basic package info
ROOT_DIR = Path(__file__).absolute().parent
PACKAGE_NAME = Path(__file__).absolute().parent.name.split("_")[-1].split("-")[-1]

AUTHOR = "lqxnjk"
AUTHOR_EMAIL = "lqxnjk@qq.com"
DESCRIPTION = "A Python package for intelligent information bagging system"
LICENSE = "MIT"
PYTHON_REQUIRES = ">=3.7"
URL = f"https://github.com/lqxnjk/{PACKAGE_NAME}"
PROJECT_URLS = {
    'Bug Reports': f'{URL}/issues',
    'Source': URL,
}

# Package discovery
PACKAGE_EXCLUDES = ['tests*', 'docs*', 'examples*']

# Classifiers
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 3.7",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Libraries",
    "Topic :: Scientific/Engineering",
]

# Keywords
KEYWORDS = ["ii", "etls", "lqxnjk", "data"]

# Package data
PACKAGE_DATA = {
    PACKAGE_NAME: ['data/*.json', 'data/*.csv'],
}
# Entry points
ENTRY_POINTS = {
    'hello': [
        f'{PACKAGE_NAME}_version = {PACKAGE_NAME}.__init__:version',
    ],
}


# ========== Dynamic Value Functions ==========
def get_long_description():
    """Read README.md content as long description."""
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()


def get_version():
    """Read version from package __init__.py file."""
    init_file = f"./{PACKAGE_NAME}/__init__.py"
    if not os.path.exists(init_file):
        init_file = f"./demo/__init__.py"
    with open(init_file, 'r', encoding='utf-8') as f:
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read(), re.M)
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


def get_requirements():
    """Read requirements from requirements.txt."""
    with open(ROOT_DIR / 'requirements.txt', 'r', encoding='utf-8') as f:
        return [
            line.strip() for line in f
            if line.strip()
               and not line.startswith('#')
               and not line.startswith('--')
        ]


REQUIREMENTS = get_requirements()

# Optional dependencies
EXTRAS_REQUIRE = {
    ':python_version < "3.8"': ['typing-extensions'],
    'dev': [
        # 'pytest>=6.0',
        # 'pytest-cov>=2.0',
        # 'flake8>=3.9',
        # 'mypy>=0.910',
        # 'sphinx>=4.0',
    ],
    'plot': [
        # 'matplotlib>=3.0',
        # 'seaborn>=0.11',
    ],
    'gpu': [
        # 'cupy>=10.0'
    ],
    'all': [f'{PACKAGE_NAME}[dev]', f'{PACKAGE_NAME}[plot]']
}

# ========== Setup Configuration ==========
setup(
    name=PACKAGE_NAME,
    version=get_version(),
    packages=find_packages(exclude=PACKAGE_EXCLUDES),
    install_requires=REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
    include_package_data=True,
    package_data=PACKAGE_DATA,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url=URL,
    project_urls=PROJECT_URLS,
    classifiers=CLASSIFIERS,
    python_requires=PYTHON_REQUIRES,
    entry_points=ENTRY_POINTS,
    license=LICENSE,
    keywords=KEYWORDS,
)


# ========== Pyproject.toml Generation ==========
def generate_pyproject_toml():
    """Generate pyproject.toml from extracted variables."""
    # Format project URLs for TOML
    urls_toml = "\n".join(
        f'{key.replace(" ", "-").lower()} = "{value}"'
        for key, value in PROJECT_URLS.items()
    )

    # Format extras_require for TOML
    extras_toml = []
    for key, deps in EXTRAS_REQUIRE.items():
        if key.startswith(':python_version'):
            # Handle conditional dependencies
            condition = key.split('"')[1]
            extras_toml.append(
                f'python_version_lt_{condition.replace(".", "_")} = {deps}'
            )
        else:
            extras_toml.append(f'{key} = {deps}')
    extras_toml_str = "\n".join(extras_toml)
    PACKAGE_DATA_STR = "{" + ",\n".join([f'"{k}" = {v}' for k, v in PACKAGE_DATA.items()]) + "}"
    pyproject_content = f"""[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{PACKAGE_NAME}"
version = "{get_version()}"
description = "{DESCRIPTION}"
readme = "README.md"
requires-python = "{PYTHON_REQUIRES}"
authors = [
    {{ name = "{AUTHOR}", email = "{AUTHOR_EMAIL}" }},
]
license = {{ text = "{LICENSE}" }}
keywords = {KEYWORDS}
classifiers = {CLASSIFIERS}
dependencies = {REQUIREMENTS}

[project.urls]
homepage = "{URL}"
{urls_toml}

[project.optional-dependencies]
{extras_toml_str}

[tool.setuptools]
packages = {find_packages(exclude=PACKAGE_EXCLUDES)}
package-data = {PACKAGE_DATA_STR}
include-package-data = true

[tool.setuptools.dynamic]
version = {{ attr = "{PACKAGE_NAME}.__version__" }}
readme = {{ file = ["README.md"] }}
"""

    with open("pyproject.toml", "w", encoding="utf-8") as f:
        f.write(pyproject_content)
    print("pyproject.toml generated successfully!")

# generate_pyproject_toml()
