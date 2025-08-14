version = '2025.8.14'

requirements = [
    'jupyter',
    'checkmarkandcross',
    'matplotlib==3.10.3',
    'numpy==2.3.0',
    'pandas==2.3.0',
    'plotly==6.1.2',
    'pyreadstat==1.2.9',
]

if __name__ == '__main__':
    from setuptools import setup, find_packages
    setup(
        name='tui_rvds',
        version=version,
        author='Eric Tröbs',
        author_email='eric.troebs@tu-ilmenau.de',
        description='everything you need for our jupyter notebooks',
        long_description='everything you need for our jupyter notebooks',
        long_description_content_type='text/markdown',
        url='https://dbgit.prakinf.tu-ilmenau.de/lectures/ringvorlesung-data-science',
        project_urls={},
        package_dir={'': 'src'},
        packages=find_packages(where='src'),
        python_requires='>=3.12',
        install_requires=requirements
    )
