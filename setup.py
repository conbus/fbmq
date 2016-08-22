import re
from distutils.core import setup


long_description = ''

try:
    import subprocess
    import pandoc

    process = subprocess.Popen(
        ['which pandoc'],
        shell=True,
        stdout=subprocess.PIPE,
        universal_newlines=True
    )

    pandoc_path = process.communicate()[0]
    pandoc_path = pandoc_path.strip('\n')

    pandoc.core.PANDOC_PATH = pandoc_path

    doc = pandoc.Document()
    doc.markdown = open('README.md').read()

    long_description = doc.rst
except:
    pass

# Get the version
version_regex = r'__version__ = ["\']([^"\']*)["\']'
with open('fbmq/__init__.py', 'r') as f:
    text = f.read()
    match = re.search(version_regex, text)

    if match:
        VERSION = match.group(1)
    else:
        raise RuntimeError("No version number found!")


setup(name='fbmq',
      version=VERSION,
      description='A Python Library For Using The Facebook Messenger Platform API',
      long_description=long_description,
      url='https://github.com/conbus/fbmq',
      author='kimwz',
      author_email='kimwz.kr@gmail.com',
      license='MIT',
      packages=['fbmq'],
      install_requires=['requests>=2.0', 'flask'],
      keywords='Facebook Messenger Platform Chatbot',
      )
