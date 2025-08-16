from setuptools import setup, find_packages

setup(
    name="omgxbeyler",
    version="1.0.0",
    author="Recep",
    author_email="mrecepdeniz5454@gmail.com",
    description="Kolay kullanımlı OMG Python kütüphanesi, WAV dosyalarını oynatma ve örnekler içerir.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kullanici/omg",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.0.0",
        "requests>=2.0.0"
    ],
    include_package_data=True,
    package_data={
        "omg": [
            "oynat/kategori/hayvanlar/*.wav",
            "oynat/kategori/milyoner/*.wav",
            "oynat/kategori/omgOzel/*.wav"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

