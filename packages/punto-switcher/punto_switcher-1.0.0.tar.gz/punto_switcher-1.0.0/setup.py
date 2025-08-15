from setuptools import setup, find_packages
import os
import sys
import shutil

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

# Получаем список дополнительных файлов
extra_files = package_files('punto_switcher/assets')

# Пути для данных
data_files = [
    ('share/applications', ['punto_switcher/assets/punto-switcher.desktop']),
    ('share/icons/hicolor/48x48/apps', ['punto_switcher/assets/icon.png']),
]

setup(
    name="punto_switcher",
    version="1.0.0",
    packages=find_packages(),
    package_data={
        'punto_switcher': extra_files,
    },
    data_files=data_files,
    include_package_data=True,
    install_requires=[
        'pyperclip>=1.8.0',
        'pynput>=1.7.0',
        'pyenchant>=3.2.0',
        'pygame>=2.0.0',
    ],
    entry_points={
        'console_scripts': [
            'punto-switcher = punto_switcher.main:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Keyboard layout autocorrector for Linux/X11",
    license="MIT",
    keywords="keyboard layout switcher autocorrect linux",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
)

# Добавляем автозапуск только при реальной установке (не при разработке)
if 'install' in sys.argv and not any(arg.startswith('--editable') for arg in sys.argv):
    try:
        autostart_dir = os.path.expanduser('~/.config/autostart/')
        os.makedirs(autostart_dir, exist_ok=True)

        # Получаем путь к установленному .desktop файлу
        installed_desktop = None
        for prefix in [sys.prefix, '/usr/local', '/usr']:
            test_path = os.path.join(prefix, 'share/applications/punto-switcher.desktop')
            if os.path.exists(test_path):
                installed_desktop = test_path
                break

        if installed_desktop:
            shutil.copy2(
                installed_desktop,
                os.path.join(autostart_dir, 'punto-switcher.desktop')
            )
            print("\nPunto Switcher добавлен в автозагрузку")
    except Exception as e:
        print(f"\nНе удалось добавить в автозагрузку: {e}")
