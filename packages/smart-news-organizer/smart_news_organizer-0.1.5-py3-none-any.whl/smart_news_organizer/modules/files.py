#!/usr/bin/python3

import re
import subprocess
import sys
import shutil

def open_with_graphical_editor(file_path):
    if sys.platform.startswith('win'):
        subprocess.Popen(['notepad', file_path])
    
    elif sys.platform.startswith('darwin'):
        subprocess.Popen(['open', '-a', 'TextEdit', file_path])
    
    elif sys.platform.startswith('linux'):
        # Tenta abrir com editores gráficos comuns
        for editor in ['gedit', 'kate', 'mousepad', 'xed', 'leafpad', 'pluma', 'code']:  # 'code' é VS Code
            if shutil.which(editor):
                subprocess.Popen([editor, file_path])
                break
    else:
        print("Nenhum editor gráfico encontrado.")


def detect_formats(texto):
    """Retorna um dicionário com a probabilidade de o texto pertencer a cada formato"""

    formatos = {
        "HTML": 0,
        "Markdown": 0,
        "TXT": 0  # Será usado como complemento caso outros formatos tenham baixa contagem
    }

    # Padrões para cada formato
    padroes = {
        "HTML": [
            r"<\s*(html|body|p|a|b|div|span|h[1-6]|br|img|table|tr|td|th)[^>]*>"
        ],
        "Markdown": [
            r"(^|\n)(#+\s)",  # Títulos (#)
            r"(^|\n)(\* |\- |\d+\.)",  # Listas (*, -, 1.)
            r"(\*\*.*?\*\*|\*.*?\*)",  # Ênfase (**bold**, *italic*)
            r"(\[.*?\]\(.*?\))",  # Links [text](url)
            r"(\!\[.*?\]\(.*?\))"  # Imagens ![alt](url)
        ]
    }

    # Contar ocorrências de cada padrão
    for formato, regex_list in padroes.items():
        for regex in regex_list:
            ocorrencias = len(re.findall(regex, texto, re.MULTILINE))
            formatos[formato] += ocorrencias

    # Se nenhum formato for identificado, assume-se TXT como 100%
    total_ocorrencias = sum(formatos.values())
    if total_ocorrencias == 0:
        formatos["TXT"] = 1.0
    else:
        # Normaliza os valores para serem probabilidades (soma 1.0)
        for formato in formatos:
            formatos[formato] /= total_ocorrencias

    return formatos
