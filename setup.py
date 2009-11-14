from distutils.core import setup

setup(
  name = "miyamoto",
  version="0.0.1",
  description="Twisted PubSubHubbub Hub",
  
  author="Jeff Lindsay",
  author_email="progrium@gmail.com",
  url="http://github.com/progrium/miyamoto/tree/master",
  download_url="http://github.com/progrium/miyamoto/tarball/master",
  classifiers=[
    ],
  packages=['miyamoto'],
  data_files=[('miyamoto', ['miyamoto/static/styles.css'])],
  scripts=['bin/miyamoto'],
)
