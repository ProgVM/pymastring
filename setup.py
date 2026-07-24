from setuptools import setup, Extension, find_packages

fastmath_module = Extension(
    'pymastring._fastmath',
    sources=['src/pymastring/_fastmath.c'],
    extra_compile_args=['-O3']
)

setup(
    name='pymastring',
    version='1.2.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    ext_modules=[fastmath_module],
)
