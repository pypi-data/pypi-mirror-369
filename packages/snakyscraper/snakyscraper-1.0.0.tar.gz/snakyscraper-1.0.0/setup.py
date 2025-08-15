from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='snakyscraper',
    version='1.0.0',
    license='MIT',
    description="SnakyScraper is a lightweight and Pythonic web scraping toolkit built on top of BeautifulSoup and Requests. It provides an elegant interface for extracting structured HTML and metadata from websites with clean, direct outputs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Rio Dev',
    author_email='my.riodev.net@gmail.com',
    url='https://github.com/riodevnet/snakyscraper',
    packages=['snakyscraper'],
    keywords = ['snakyscraper', 'scraping', 'scraper'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests",
        "beautifulsoup4",
        "lxml"
    ],
)
