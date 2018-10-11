from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name='dataradeh',
    version='0.0.1',
    description='Data IO, Wrangling, Etc.',
    long_description=readme,
    author='ScreenshopIt Dev Team',
    author_email='ScreenshopIt Dev Team Email',
    packages=['dataradeh', 'dataradeh.io', 'dataradeh.processing'],
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ]
)