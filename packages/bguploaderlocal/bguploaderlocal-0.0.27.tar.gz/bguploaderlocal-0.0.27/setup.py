from setuptools import setup, find_packages

setup(
	name='bguploaderlocal',
	version='0.0.27',
	packages=find_packages(),
	install_requires=['requests','urllib3<2','rich'],
	entry_points={
		'console_scripts': [
			'bguploaderlocal=bguploaderlocal.cli:run',
		],
	},
	author='pathik-appachhi',
	description='CLI to upload JUnit .xml files.',
	python_requires='>=3.6',
)