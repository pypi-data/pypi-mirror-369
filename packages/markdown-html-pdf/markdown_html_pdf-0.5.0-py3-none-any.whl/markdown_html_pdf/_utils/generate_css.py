from pygments.formatters import HtmlFormatter

# Gera o CSS para o estilo padrão
formatter = HtmlFormatter(style="github-dark")
css = formatter.get_style_defs(".highlight")

print("CSS do Pygments:")
print("=" * 50)
print(css)
print("=" * 50)

# Salva em um arquivo
with open("pygments.css", "w") as f:
    f.write(css)

print(f"CSS salvo em pygments.css ({len(css)} caracteres)")
