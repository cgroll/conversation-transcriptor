from setuptools import find_packages, setup

setup(
    name='src',
    packages=find_packages(),
    version='0.1.0',
    py_modules=['click_app'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'from_wav = click_app:click_wav_to_transcript',
            'from_url = click_app:click_url_to_transcript',
            'url_to_notion = click_app:click_url_to_notion',
        ],
    },
    description='Some speech-to-text python experiments',
    author='Christian Groll',
    license='MIT',
)
