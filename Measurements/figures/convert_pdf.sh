find . -name "*.pdf" | xargs -I {} sh -c 'pdftoppm -png -r 300 {} > {}.png'
