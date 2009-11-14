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
  packages=['miyamoto', 'miyamoto.test'],
  data_files=[('miyamoto/static', ['miyamoto/static/styles.css']),
              ('miyamoto/template', ['miyamoto/template/index.html'])],
  scripts=['bin/miyamoto'],
)
