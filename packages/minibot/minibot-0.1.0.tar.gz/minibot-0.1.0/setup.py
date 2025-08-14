from setuptools import setup, find_packages

setup(
    name='minibot',
    version='0.1.0',
    description='Librería de utilerías para automatizaciones RPA con Microsoft Graph y otras herramientas.',
    author='Raul Sanz',
    author_email='mail@rulosanz.com',
    packages=find_packages(),  # Encuentra automáticamente todos los submódulos
    include_package_data=True,
    install_requires=[
        'msal>=1.0.0',
        'requests>=2.0.0',
        'python-dotenv>=1.0.0',
        'pandas>=1.0.0',
        'openpyxl>=3.0.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)
