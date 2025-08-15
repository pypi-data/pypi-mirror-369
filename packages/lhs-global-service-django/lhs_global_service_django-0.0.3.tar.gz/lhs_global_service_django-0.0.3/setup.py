from setuptools import setup, find_packages

setup(
    name='lhs_global_service_django',
    version='0.0.3',
    description='A global logging and service utilities package for Python projects, designed for seamless integration with Django applications. Developed by Lighthouse Info System Pvt Ltd., this package provides robust logging, configuration, and service management tools to enhance reliability and maintainability in Django-based projects.',
    author='Rohit Jagtap',
    author_email='rohit.jagtap@lighthouseindia.com',
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-dotenv',
        'cx_Oracle',  
    ],
    python_requires='>=3.9',
    url='https://github.com/NAT-TEAM-LIGHTHOUSE/Python-Projects/tree/python_global_django_pkg',  
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)