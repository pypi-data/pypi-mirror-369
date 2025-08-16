from pathlib import Path
from datetime import date
import re

CAMADAS = 'doc_gua, view, prism';

#region PASTAS E ARQUIVOS
pasta_atual = Path(__file__).parent
pasta_destino = pasta_atual/'static/css'
pasta_origem = pasta_atual.parent/'origem/css'
pasta_base = pasta_origem/'base'
pasta_utils = pasta_origem/'utils'

arquivo_destino = pasta_destino/'guarana.css'
arquivos_base = sorted(list(pasta_base.glob('*')))
arquivos_utils = list(pasta_utils.glob('*'))
# endregion


# TEXTO A SER USADO
texto = f'/*{date.today().strftime("%d/%m/%Y")}*/\n'

# TEXTO DO ESTILO.CSS
regex_layers = r'(\s*@layer\s+.*?)(\s*);'
estilo_original = pasta_origem/'estilo.css'

for arquivo in arquivos_base:
    texto += f'\n{arquivo.read_text()}\n'

for arquivo in arquivos_utils:
    texto += f'\n{arquivo.read_text()}\n'

    
texto += re.sub(regex_layers, r'\1' + f', {CAMADAS}' + r';', estilo_original.read_text())
texto = texto.replace('/* IMPORTS */\n@import url(ARQUIVO_BASE);\n', '')

arquivo_destino.write_text(texto)

# COPIA JS
arquivo_js_destino = pasta_atual/'static/js/guarana.js'
arquivo_js_origem = pasta_atual.parent/'origem/js/guarana.js'

arquivo_js_destino.write_text(arquivo_js_origem.read_text())
