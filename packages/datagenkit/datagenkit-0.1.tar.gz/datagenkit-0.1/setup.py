from setuptools import setup, find_packages

setup(
    name="datagenkit",
    version="0.1",
    description="A Python package for generating diverse and enriched image datasets using traditional, neural style transfer, and patch mixing augmentations.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Jayavardhan-7/DataGenKit-',
    author='Jayavardhan', 
    author_email='jayavardhanperala@gmail.com', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Image Processing',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Development Status :: 3 - Alpha',
    ],
    keywords='image augmentation, dataset generation, neural style transfer, cutmix, mixup, computer vision, deep learning',

    packages=find_packages(),
    install_requires=[
        "gradio",
        "albumentations",
        "torch",
        "torchvision",
        "scikit-image",
        "numpy",
        "opencv-python",
    ],
    python_requires='>=3.8', # Specify minimum Python version
    entry_points={
        "console_scripts": [
            "datagenkit=main:main",
        ],
    },
)