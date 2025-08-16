import io
from setuptools import setup, find_packages

with io.open("README.md", encoding="utf-8") as f:
	long_description = f.read()

setup(
	name="lumiML",
	version="0.1.0",
	description="A data preprocessing and cleaning toolkit for machine learning. Still under active development.",
	long_description=long_description,
	long_description_content_type="text/markdown",
	author="Moon",
	url="https://github.com/Cod4L/lumiML",
	packages=find_packages(),
	install_requires=[
		"pandas",
		"numpy",
		"scikit-learn",
		"tensorflow",
		"opencv-python",
		"seaborn",
		"matplotlib",
		"joblib",
		"scipy",
	],
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Intended Audience :: Developers",
		"Topic :: Scientific/Engineering :: Information Analysis",
	],
	python_requires=">=3.7",
)
