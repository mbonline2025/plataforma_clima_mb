from setuptools import setup

APP = ['main.py']
OPTIONS = {
    'argv_emulation': True,
    'includes': ['streamlit'],
    'packages': ['streamlit', 'pandas', 'sklearn', 'umap', 'textblob', 'sentence_transformers'],
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
