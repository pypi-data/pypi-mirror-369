from setuptools import setup,find_packages

setup(
    name='aplicacion_ventas_hc',
    version='0.1.0',
    author='HC',
    author_email='hcovas2017@gmail.com',
    description='Paquete para administracion de ventas, precios, descuentos, impuestos',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/curso_python_cce/gestor/aplicacionventas',
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.7', 
    classifiers=[
        'Programming Language :: Python :: 3',
        #'License :: LicenseRef-My-Custom-License',
        'Operating System :: OS Independent'
    ],
)
