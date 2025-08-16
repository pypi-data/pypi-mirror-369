from dateutil import parser
from datetime import datetime, timedelta

def normalizar_data(data_str):
    try:
        dt = parser.parse(data_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Erro ao converter data: {data_str} -> {e}")
        return data_str
        
def get_datetime(data):
    try:
        return parser.parse(data.published)
    except Exception:
        return parser.parse("1900-01-01 00:00:00") 
        



def is_less_than(entry, horas):
    """
    Retorna True se a data de publicação/atualização do entry for inferior a 'horas' atrás.
    
    Parâmetros:
    - entry: um item de feedparser (dict-like)
    - horas: número de horas para comparar

    Retorna:
    - True se a data for inferior a 'horas' atrás, False caso contrário.
    """
    
    time_struct = entry.get('published_parsed') or entry.get('updated_parsed')
    
    if time_struct:
        data_entry = datetime(*time_struct[:6])
        agora = datetime.utcnow()
        return (agora - data_entry) < timedelta(hours=horas)
    
    # Se não houver data, retornamos False
    return False
