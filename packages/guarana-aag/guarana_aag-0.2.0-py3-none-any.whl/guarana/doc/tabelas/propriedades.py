from ...config import *

propriedades_css = [
    {
        'nome': '--cor-erro',
        'tipo': 'cor',
        'heranca': 'não',
        'uso': ['variável de cor vermelha para indicar erros ou urgência.', '`--cor-txt: var(--cor-erro)`'],
        'categoria': 'fechada',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-ok",
        "tipo": "cor",
        "heranca": "não",
        "uso": ["variável de cor verde para indicar sucesso.", '`--cor-bg: var(--cor-ok)`'],
        'categoria': 'fechada',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-alerta",
        "tipo": "cor",
        "heranca": "não",
        "uso": ["variável de cor amarela para indicar alerta, aviso.", '`--cor-txt: var(--cor-alerta)`'],
        'categoria': 'fechada',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--sans",
        "tipo": "texto separado por vírgulas",
        "heranca": "não",
        "uso": ["valor padrão para fontes sem serifa. Use como completemento, da fonte que for usar, se for personalizar.", '`--fonte: var(--sans)`'],
        'categoria': 'fechada',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--serif",
        "tipo": "texto separado por vírgulas",
        "heranca": "não",
        "uso": ["valor padrão para fontes serifadas. Use como completemento, da fonte que for usar, se for personalizar.", '`--fonte: var(--serif)`'],
        'categoria': 'fechada',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-1",
        "tipo": "cor",
        "heranca": "não",
        "uso": ["variável de paleta de cores, a cor principal.", '`--cor-txt: var(--cor-1)`'],
        'categoria': 'aberta',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-2",
        "tipo": "cor",
        "heranca": "não",
        "uso": ["variável de paleta de cores, a cor secundária.", '`--cor-txt: var(--cor-2)`'],
        'categoria': 'aberta',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-3",
        "tipo": "cor",
        "heranca": "não",
        "uso": ["variável de paleta de cores, a cor terciária.", '`--cor-txt: var(--cor-3)`'],
        'categoria': 'aberta',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--rd",
        "tipo": "porcentagem / medida",
        "heranca": "sim",
        "uso": [f"variável para arredondar a borda. Diversos elementos em utilitários fazem uso dessa variável por padrão, de forma que ao alterar o valor inicial, vai alterar diversos elementos do {NOME}", '`border-radius: var(--rd)`'],
        'categoria': 'aberta',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--sombra",
        "tipo": "valores separados por espaço",
        "heranca": "sim",
        "uso": [f"variável para a sombra padrão. Diversos elementos em utilitários fazem uso dessa variável por padrão, de forma que ao alterar o valor inicial, vai alterar diversos elementos do {NOME}", '`box-shadow: var(--sombra)`'],
        'categoria': 'aberta',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--transicao",
        "tipo": "valores separados por espaço",
        "heranca": "sim",
        "uso": [f"variável para a transição padrão, sem indicar qual a nome afetada. Diversos elementos em utilitários fazem uso dessa variável por padrão, de forma que ao alterar o valor inicial, vai alterar diversos elementos do {NOME}", '`transition: var(--transicao)`'],
        'categoria': 'aberta',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-base",
        "tipo": "cor",
        "heranca": "-",
        "uso": ["variável usada em diversos elementos internos. Serve como base para que seja aplicado tons nos elementos e permitindo alterações rápidas em todo o componente alterando apenas essa variável.", '`--cor-bg: hsl(from var(--cor-base) h s calc(l * 1.25)`'],
        'categoria': 'root',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-secundaria",
        "tipo": "cor",
        "heranca": "-",
        "uso": ["variável usada em diversos elementos internos (menos usada que a `--cor-base`). Serve como base de cor secundária para que seja aplicado tons nos elementos e permitindo alterações rápidas em todo o componente alterando apenas essa variável.", '`--cor-txt: hsl(from var(--cor-sec) h calc(s - 10) calc(l * .25)`'],
        'categoria': 'root',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-bg",
        "tipo": "cor",
        "heranca": "-",
        "uso": ["variável usada em diversos elementos e tags, mesmo no reset, que já contam com `background-color` para essa cor, bastando alterar essa variável.", '`--cor-bg: red`'],
        'categoria': 'root',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--cor-txt",
        "tipo": "cor",
        "heranca": "-",
        "uso": ["variável usada em diversos elementos e tags, mesmo no reset, que já contam com `color` para essa cor, bastando alterar essa variável.", '`--cor-txt: hsl(0, 0%, 0%)`'],
        'categoria': 'root',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--modo",
        "tipo": "color-scheme",
        "heranca": "-",
        "uso": ["Variável usada no :root e em eventual tema para determinar qual o modo de cor usado. O root já faz uso de", '`color-scheme`', "bastando alterar o modo quando indicado. Veja mais em <a href='cores'>cores</a>", '`--modo: dark`'],
        'categoria': 'aberto',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--fonte",
        "tipo": "texto separado por vírgula",
        "heranca": "-",
        "uso": ["variável usada no `<body>` e já conta com`font-family` para essa essa fonte, bastando alterar essa variável. Caso algum elemento vá apresentar outra fonte, chamar o `font-family` normalmente e declare nova variável de fonte no `:root`.", '`--fonte: \'Roboto\', var(--sans)`'],
        'categoria': 'root',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--tema",
        "tipo": "texto",
        "heranca": "sim",
        "uso": ["variável usada no `:root` para indicar qual o tema de cores utilizado. Valor inicial: \"padrão\".", '`--tema: \"alto contraste\"`'],
        'categoria': 'root',
        'atualizada': '0.1.0'
    },
    {
        "nome": "--gap",
        "tipo": "porcentagem / medida",
        "heranca": "sim",
        "uso": ["variável usada nos utilitários para indicar qual a medida de gap de um container que seja flex ou grid. Valor inicial: 0.", '`--gap: 1rem`'],
        'categoria': 'aberta',
        'atualizada': '0.2.0'
    },
    {
        "nome": "--pd-i",
        "tipo": "porcentagem / medida",
        "heranca": "sim",
        "uso": ["Variável utilizada para o padding-inline (horizontal) de um utilitário que faça uso de padding. Valor inicial: 0.", '`--pd-i: 1em;`', '`padding-inline: var(--pd-i);`'],
        'categoria': 'aberta',
        'atualizada': '0.2.0'
    },
    {
        "nome": "--pd-b",
        "tipo": "porcentagem / medida",
        "heranca": "sim",
        "uso": ["Variável utilizada para o padding-block (vertical) de um utilitário que faça uso de padding. Valor inicial: 0.", '`--pd-h: 1em;`', '`padding-block: var(--pd-b);`'],
        'categoria': 'aberta',
        'atualizada': '0.2.0'
    },
    {
        "nome": "--mg-i",
        "tipo": "porcentagem / medida",
        "heranca": "sim",
        "uso": ["Variável utilizada para o margin-inline (horizontal) de um utilitário que faça uso de margem. Valor inicial: auto.", '`--mg-i: auto;`', '`margin-inline: var(--mg-i);`'],
        'categoria': 'aberta',
        'atualizada': '0.2.0'
    },
    {
        "nome": "--mg-b",
        "tipo": "porcentagem / medida",
        "heranca": "sim",
        "uso": ["Variável utilizada para o margin-block (vertical) de um utilitário que faça uso de margem. Valor inicial: 0.", '`--mg-h: 1rem 0;`', '`margin-block: var(--mg-b);`'],
        'categoria': 'aberta',
        'atualizada': '0.2.0'
    },
    {
        "nome": "--txt",
        "tipo": "porcentagem / medida",
        "heranca": "sim",
        "uso": ["Formata o tamanho da fonte do elemento. Valor inicial: 1em.", '`--txt: 1em;`'],
        'categoria': 'aberta',
        'atualizada': '0.2.0'
    },
    {
        'nome': '--borda',
        'tipo': 'medida e texto separado por espaço',
        'heranca': 'sim',
        'uso': ['Formata a borda'],
        'categoria': 'aberta',
        'atualizada': '0.2.0',
    },
    {
        'nome': '--borda-b',
        'tipo': 'porcentagem / medida',
        'heranca': 'sim',
        'uso': ['Define a espessura da borda no eixo bloco (horizontal)'],
        'categoria': 'aberta',
        'atualizada': '0.2.0',
    },
    {
        'nome': '--borda-i',
        'tipo': 'porcentagem / medida',
        'heranca': 'sim',
        'uso': ['Define a espessura da borda no eixo inline (vertical)'],
        'categoria': 'aberta',
        'atualizada': '0.2.0',
    },
    {
        'nome': '--cor-borda',
        'tipo': 'cor',
        'heranca': 'sim',
        'uso': ['Define a cor da borda'],
        'categoria': 'fechada',
        'atualizada': '0.2.0',
    },
    {
        'nome': '--cor-destaque',
        'tipo': 'cor',
        'heranca': 'sim',
        'uso': ['Uma variação de destaque de uma cor escolhida.', 'Lembre-se de redeclarar no seletor, caso você altere a `cor-base`'],
        'categoria': 'root',
        'atualizada': '0.2.0',
    },
    {
        'nome': '--cor-suave',
        'tipo': 'cor',
        'heranca': 'sim',
        'uso': ['Uma variação de suave de uma cor escolhida.', 'Lembre-se de redeclarar no seletor, caso você altere a `cor-base`'],
        'categoria': 'root',
        'atualizada': '0.2.0',
    },
    
]
