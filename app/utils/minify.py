"""
Minification et compression des assets CSS/JS
"""

import os
import re
from csscompressor import compress as css_compress


def minify_css(css_content):
    """Minifie du CSS"""
    return css_compress(css_content)


def minify_js(js_content):
    """Minifie du JavaScript (simple)"""
    # Supprimer commentaires
    js_content = re.sub(r'//.*?\n', '\n', js_content)
    js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)

    # Supprimer espaces multiples
    js_content = re.sub(r'\s+', ' ', js_content)

    return js_content.strip()


def compress_static_files():
    """Compresse tous les fichiers static"""
    static_dir = 'static'

    # CSS
    for root, dirs, files in os.walk(os.path.join(static_dir, 'css')):
        for file in files:
            if file.endswith('.css') and not file.endswith('.min.css'):
                filepath = os.path.join(root, file)

                with open(filepath, 'r', encoding='utf-8') as f:
                    css = f.read()

                minified = minify_css(css)

                # Sauvegarder version minifiée
                min_filepath = filepath.replace('.css', '.min.css')
                with open(min_filepath, 'w', encoding='utf-8') as f:
                    f.write(minified)

                print(f"✅ CSS minifié : {file}")

    # JS
    for root, dirs, files in os.walk(os.path.join(static_dir, 'js')):
        for file in files:
            if file.endswith('.js') and not file.endswith('.min.js'):
                filepath = os.path.join(root, file)

                with open(filepath, 'r', encoding='utf-8') as f:
                    js = f.read()

                minified = minify_js(js)

                min_filepath = filepath.replace('.js', '.min.js')
                with open(min_filepath, 'w', encoding='utf-8') as f:
                    f.write(minified)

                print(f"✅ JS minifié : {file}")


# Exécuter lors du déploiement
if __name__ == '__main__':
    compress_static_files()