from setuptools import setup

setup(
    name="LAGE",
    version="0.1.0",
    author="ALESSANDRO FAVILLA",
    description="New developer tool!",
    long_description=open("readme.txt", encoding="utf-8").read(),
    long_description_content_type="text/plain",  # Usa text/markdown se il file è in markdown
    py_modules=["LAGE"],  # lista, non stringa
    install_requires=["pytz"],
    python_requires=">=3.7",
)
