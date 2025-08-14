from setuptools import find_packages, setup

setup(
    name="flask_restful_resource_new",
    version="0.3.5",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Flask==2.3.3",  # 支持Python 3.12的版本
        "Flask-RESTful==0.3.10",
        "schema==0.7.5",  # 兼容3.12的更新版本
        "marshmallow==3.20.1",  # 主要更新，3.x系列支持3.12
        "requests==2.31.0",
        "kazoo==2.10.0",
        # mongo相关（保持注释，按需安装）
        # "marshmallow-mongoengine==0.10.0",
        # "flask-mongoengine==1.0.0",
        # sql相关
        # "Flask-SQLAlchemy==3.1.1",
        # "flask-marshmallow==1.2.0",
        # "marshmallow-sqlalchemy==0.29.0",
    ],
)