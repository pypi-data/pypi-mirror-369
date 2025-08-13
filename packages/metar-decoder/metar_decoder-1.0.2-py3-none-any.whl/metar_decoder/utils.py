import re
import difflib

def clean_metar_string(metar: str) -> str:
    """
    Limpia una cadena que puede contener múltiples METAR/SPECI concatenados,
    devolviendo solo el METAR principal. Conserva el bloque RMK completo
    y solo corta si aparece un nuevo METAR real (estación+fecha+viento).
    """
    parts = metar.strip().split()
    if len(parts) < 3:
        return metar.strip()

    # Patrones locales (autosuficientes)
    STATION_RE  = re.compile(r"^[A-Z]{4}$")          # p.ej., SPMS
    DATETIME_RE = re.compile(r"^\d{6}Z$")            # p.ej., 082200Z
    WIND_RE     = re.compile(r"^(?:VRB|\d{3})\d{2,3}(?:G\d{2,3})?(?:KT|MPS)$")

    def looks_like_metar_start(idx: int) -> bool:
        """Devuelve True si parts[idx:idx+3] es 'STATION DATETIME WIND'."""
        return (
            idx + 2 < len(parts) and
            STATION_RE.match(parts[idx]) and
            DATETIME_RE.match(parts[idx+1]) and
            WIND_RE.match(parts[idx+2])
        )

    # Identificar inicio válido
    start = None
    for i in range(len(parts)):
        # Caso con prefijo "METAR"/"SPECI"
        if parts[i] in ("METAR", "SPECI") and looks_like_metar_start(i + 1):
            start = i + 1
            break
        # Caso directo "STATION DATETIME WIND"
        if looks_like_metar_start(i):
            start = i
            break
    if start is None:
        # No se encontró forma reconocible
        return metar.strip()

    # Siguiente inicio válido (otro METAR) o final
    end = len(parts)
    j = start + 3
    while j < len(parts):
        if parts[j] in ("METAR", "SPECI") and looks_like_metar_start(j + 1):
            end = j
            break
        if looks_like_metar_start(j):
            end = j
            break
        j += 1

    cleaned = " ".join(parts[start:end])

    # Tomar = como fin del mensaje
    eq_idx = cleaned.find("=")
    if eq_idx != -1:
        cleaned = cleaned[:eq_idx].rstrip()

    return cleaned

def corregir_cavok(part):
    part = part.strip()
    if len(part) in (4, 5):
        if difflib.SequenceMatcher(None, part.upper(), 'CAVOK').ratio() > 0.7:
            return 'CAVOK'
    return part

def corregir_nube(part):
    part = part.strip()
    nube_tipos = ['FEW', 'SCT', 'BKN', 'OVC', 'VV']
    if len(part) >= 6 and part[-3:].isdigit():
        base = part[:-3].upper()
        similitudes = {tipo: difflib.SequenceMatcher(None, base, tipo).ratio() for tipo in nube_tipos}
        mejor = max(similitudes, key=similitudes.get)
        if similitudes[mejor] > 0.7:
            return mejor + part[-3:]
    return part

def corregir_rmk(part):
    part = part.strip()
    if len(part) >= 3:
        if difflib.SequenceMatcher(None, part.upper(), 'RMK').ratio() > 0.6:
            return 'RMK'
    return part

def corregir_vrb(part):
    part = part.strip()

    if not re.search(r"\d{2,3}(?:G\d{2,3})?(?:KT|MPS)$", part.upper()):
        return part
    
    variantes = ['VRB', 'VBR', 'VRRB', 'VVBR', 'VAR', 'VR']
    for variante in variantes:
        if difflib.SequenceMatcher(None, part.upper(), variante).ratio() > 0.7:
            return 'VRB'
    return part

def corregir_partes_metar(parts):
    """Corrige errores comunes en partes del METAR."""
    if isinstance(parts, str):
        parts = parts.strip().split()
    corregidos = []
    for part in parts:
        part = corregir_cavok(part)
        part = corregir_nube(part)
        part = corregir_rmk(part)
        part = corregir_vrb(part)
        corregidos.append(part)
    return " ".join(corregidos)

def extraer_temperaturas_extremas(metar: str):
    """Extrae temperaturas máximas/mínimas a partir de etiquetas comunes."""
    result = {}
    patrones = [
        (r'\b(?:TX|TMAX|T\.MAX|T\.X|TMX|MX)\s*[:=]?\s*(M?-?\d{1,2}(?:[.,]\d)?)\b', 'tmax_c_custom'),
        (r'\b(?:TN|TMIN|T\.MIN|T\.N|TMN|MN)\s*[:=]?\s*(M?-?\d{1,2}(?:[.,]\d)?)\b', 'tmin_c_custom')
    ]

    for pattern, key in patrones:
        match = re.search(pattern, metar, re.IGNORECASE)
        if match:
            raw = match.group(1).replace("M", "-").replace(",", ".")
            try:
                result[key] = float(raw)
            except ValueError:
                continue

    return result
