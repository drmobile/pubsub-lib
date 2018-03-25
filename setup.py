from setuptools import setup, find_packages

setup(
    name='soocii-pubsub-lib',
    version='0.1',
    url='https://github.com/drmobile/pubsub-broker',
    license='Apache Software License',
    author='Soocii',
    author_email='service@soocii.me',
    description='Library for Soocii back-end services to integrate with Google Cloud Pub/Sub service.',
    packages=find_packages(exclude=['tests']),
    long_description=open('README.md').read(),
    zip_safe=False)
