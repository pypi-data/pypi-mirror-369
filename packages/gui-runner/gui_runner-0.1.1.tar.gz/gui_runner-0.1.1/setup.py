from setuptools import setup, find_packages

setup(
    name="gui-runner",
    version="0.1.1",
    description="Configurable GUI runner for Python/Node.js scripts",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author="985ch",
    url="https://github.com/985ch/gui-runner",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'gui-runner = gui_runner.main:main',  # 修改为指向包内的模块
        ],
    },
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)