from setuptools import setup

setup(
    name="reel2bits",
    version="0.1",
    license="AGPL",
    python_requires=">=3.6",
    long_description=open("../README.md").read(),
    url="http://dev.sigpipe.me/DashieV3/reel2bits",
    author="Dashie",
    author_email="dashie@sigpipe.me",
    install_requires=[
        "Flask==1.1.1",
        "SQLAlchemy==1.3.10",
        "WTForms==2.2.1",
        "WTForms-Alchemy==0.16.9",
        "SQLAlchemy-Searchable==1.1.0",
        "SQLAlchemy-Utils==0.34.2",
        "Bootstrap-Flask==1.0.10",
        "Flask-Mail==0.9.1",
        "Flask-Migrate==2.4.0",
        "Flask-Uploads==0.2.1",
        "bcrypt==3.1.7",
        "pydub==0.23.1",
        "psycopg2-binary==2.8.1",
        "mutagen==1.42.0",
        "unidecode==1.1.1",
        "Flask_Babelex==0.9.3",
        "texttable==1.6.1",
        "python-slugify==3.0.4",
        "python-magic==0.4.15",
        "redis==3.3.10",
        "celery==4.3.0",
        "flask-accept==0.0.6",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest==5.2.1", "pytest-cov==2.8.1", "jsonschema==3.1.1"],
)
