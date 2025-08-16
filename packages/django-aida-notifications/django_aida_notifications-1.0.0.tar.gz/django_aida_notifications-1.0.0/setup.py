from setuptools import find_packages, setup

with open('README.md', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='django-aida-notifications',
    version='1.0.0',
    author='AIDA Notifications Contributors',
    author_email='support@aida-notifications.org',
    description='A comprehensive Django notification extension with email (via Anymail) and SMS (via Twilio) support',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hmesfin/aida-notifications',
    packages=find_packages(exclude=['tests*']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Telephony',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    install_requires=[
        'Django>=3.2,<6.0',
        'django-anymail>=8.0',
        'twilio>=7.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-django>=4.0',
            'pytest-cov>=3.0',
            'ruff>=0.1.0',
            'mypy>=0.950',
            'django-stubs>=1.12.0',
            'pre-commit>=3.0',
        ],
        'redis': [
            'redis>=4.0',
            'django-redis>=5.0',
        ],
        'celery': [
            'celery>=5.0',
        ],
    },
    include_package_data=True,
    package_data={
        'aida_notifications': [
            'templates/**/*.html',
            'static/**/*',
            'migrations/*.py',
        ],
    },
    zip_safe=False,
)
