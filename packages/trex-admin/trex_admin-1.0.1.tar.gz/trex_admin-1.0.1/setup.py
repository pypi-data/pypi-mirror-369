import setuptools
from pip._vendor.pkg_resources import require

setuptools.setup(
     name='trex_admin',  
     version='1.0.1',
     author="Jack Lok",
     author_email="sglok77@gmail.com",
     description="TRex admin package",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     install_requires=[            
          'flask',
          'Jinja2',
          'MarkupSafe',
          'phonenumbers',
          'requests',
          'testfixtures',
          'flask-babel',
          'Flask-CORS',
          'trex-lib',
          'trex-model',
          'trex-mail',
          
      ]
 )




