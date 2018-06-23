# Sample https://github.com/pypa/sampleproject

from setuptools import setup, find_packages

setup(
    name='soocii-pubsub-lib',
    version='1.4',
    url='https://github.com/drmobile/pubsub-broker',
    license='Apache Software License',
    author='Soocii',
    author_email='service@soocii.me',
    description='Library for Soocii back-end services to integrate with Google Cloud Pub/Sub service.',
    packages=find_packages(exclude=['tests', 'samples']),
    long_description=open('README.md').read(),
    zip_safe=False,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['six', 'google-cloud>=0.33.1', 'google-cloud-pubsub>=0.35.4'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install soocii-pubsub-lib[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={  # Optional
        'dev': ['docker', 'pytest', 'pycodestyle', 'pytest-cov', 'coveralls'],
    },
)
