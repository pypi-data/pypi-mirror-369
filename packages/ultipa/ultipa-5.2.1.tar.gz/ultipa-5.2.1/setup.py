from setuptools import setup, find_packages

APP = ['ultipa']
DATA_FILES = []
OPTIONS = {}

def readMe():
    try:
        ret = open("./ReadMe.md", encoding="utf-8").read()
    except Exception as e:
        return ""
    return ret

setup(
    app=APP,
    name="ultipa",
    metaversion="",
    version="5.2.1",
    python_requires='>=3.9,<3.13',
    packages=find_packages(),  # 常用,要熟悉 :会自动查找当前目录下的所有模块(.py文件) 和包(包含__init___.py文件的文件夹)
    # scripts = ['say_hello.py'],
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=[
				'grpcio==1.62.3',
                'grpcio-tools==1.62.3',
                'protobuf==4.25.3',
                'google==3.0.0',
                'schedule==1.2.2',
                'prettytable==3.9.0',
                'treelib==1.7.1',
                'tzdata==2024.2',
                'tzlocal==5.2',
                'pytz==2025.2',
                'requests==2.32.3',
                'future==1.0.0',
                'python-dateutil==2.8.2',
                ],  # 常用
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst',"printer"],
        # And include any *.msg files found in the 'hello' package, too:
        'hello': ['*.msg'],
    },
    # metadata for upload to PyPI
    author="Ultipa",
    author_email="support@ultipa.com",
    description="Pure Python Ultipa Driver",
    license="PSF",
    keywords="ultipa sdk,ultipa graph",
    url="https://www.ultipa.com/document/ultipa-drivers/python-installation",  # project home page, if any
    long_description=readMe(),
    long_description_content_type='text/markdown',
    # could also include long_description, download_url, classifiers, etc.
)