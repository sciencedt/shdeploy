""" Setup for shdeploy """
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	requirements = f.readlines()

long_description = 'Package to support AWS Cloudformation Pipeline. works as a wrapper for few awscli commands.'

setup(
		name='shdeploy',
		version='1.0.0',
		author='Surendra Shukla',
		author_email='surendra.shukla29@gmail.com',
		url='https://github.com/sciencedt/shdeploy',
		description='Package to support AWS Cloudformation Pipeline. works as a wrapper for few awscli commands.',
		long_description=long_description,
		long_description_content_type="text/markdown",
		license='MIT',
		packages=find_packages(),
		entry_points={
			'console_scripts': [
				'shdeploy = cli:main'
			]
		},
		classifiers=[
			"Programming Language :: Python :: 3",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
		],
		keywords='Package to support AWS Cloudformation Pipeline. works as a wrapper for few awscli commands.',
		install_requires=requirements,
		zip_safe=False
)
