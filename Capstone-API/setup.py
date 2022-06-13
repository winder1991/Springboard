from distutils.core import setup


def readme():
    """Import the README.md Markdown file and try to convert it to RST format."""
    try:
        import pypandoc
        return pypandoc.convert_text('README.md', 'rst',format='md')
    except(IOError, ImportError):
        with open('README.md') as readme_file:
            return readme_file.read()


setup(
    name='ComEnergyForecast',
    version='0.1',
    description='commercial building energy forecast',
    long_description=readme(),
    classifiers=[
        'Programming Language :: Python :: 3.8.13',
    ],
    # Substitute <github_account> with the name of your GitHub account
    url='',
    author='Frank Zhang',  # Substitute your name
    author_email='zhft19@gmail.com',  # Substitute your email
    license='',
    packages=['ComEnergyForecast'],
    install_requires=[
      	'pypandoc>=1.4',
        'pytest>=4.3.1',
        'pytest-runner>=4.4',
        'click>=7.0'
    ],
    setup_requires=['pytest-runner'],
    # tests_require=['pytest'],
    # entry_points='''
    #     [console_scripts]
    #     titanic_analysis=titanic.command_line:titanic_analysis
    # '''
)