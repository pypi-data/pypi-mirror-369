import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="umnet_scripts",
    version="1.1.0",
    author="University of Michigan",
    author_email="amylieb@umich.edu",
    description="Python tools for interacting with UMnet's network tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.umich.edu/its-inf-net/umnet-scripts",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "dnspython",
        "regex",
        "psycopg2-binary",
        "sqlalchemy>=1.4",
        "pynetbox",
        "oracledb",
        "ncclient",
        "python-decouple",
        "requests",
        "urllib3",
        "gspread",
        "oauth2client",
        "fabric",
        "invoke<2.1",
        "f5-sdk",
    ],
    python_requires=">=3.6",
    scripts=[
        "bin/equipdb_rancid_audit.py",
        "bin/get_al_port_data.py",
        "bin/equipdb_gsheet_backup.py",
    ],
)
