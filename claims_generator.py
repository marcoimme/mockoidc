"""
Utilità per generare claims dinamici dall'email dell'utente
"""
import hashlib
import uuid


def generate_claims_from_email(email: str) -> dict:
    """
    Genera claims OIDC dinamicamente da una email.
    
    Args:
        email: Email dell'utente
        
    Returns:
        Dictionary con tutti i claims necessari
    """
    from config import DYNAMIC_CLAIMS_CONFIG
    
    # Parsing dell'email per estrarre nome
    local_part = email.split('@')[0] if '@' in email else email
    
    # Estrai given_name e family_name dalla parte locale
    # Supporta formati: nome.cognome, nome_cognome, nomecognome123
    parts = local_part.replace('_', '.').replace('-', '.').split('.')
    
    if len(parts) >= 2:
        given_name = parts[0].capitalize()
        family_name = ' '.join(p.capitalize() for p in parts[1:])
    else:
        # Se c'è una sola parte, prova a separare numeri
        name_without_numbers = ''.join(c for c in parts[0] if not c.isdigit())
        if len(name_without_numbers) > 3:
            # Prova a dividere a metà
            mid = len(name_without_numbers) // 2
            given_name = name_without_numbers[:mid].capitalize()
            family_name = name_without_numbers[mid:].capitalize()
        else:
            given_name = name_without_numbers.capitalize()
            family_name = "User"
    
    # Nome completo
    name = f"{given_name} {family_name}".strip()
    if not name or name == "User":
        name = email.split('@')[0].capitalize()
    
    # Genera ID univoci ma deterministici dalla email (stesso email = stesso ID)
    email_hash = hashlib.sha256(email.encode()).hexdigest()
    
    # Usa i primi 32 caratteri dell'hash per creare un UUID deterministico
    oid = str(uuid.UUID(email_hash[:32]))
    sub = oid  # sub e oid sono uguali in Azure AD
    
    # Genera anche tid deterministico dalla domain
    domain = email.split('@')[1] if '@' in email else 'localhost'
    domain_hash = hashlib.sha256(domain.encode()).hexdigest()
    tid = str(uuid.UUID(domain_hash[:32]))
    
    # Costruisci i claims
    claims = {
        "sub": sub,
        "oid": oid,
        "tid": tid,
        "name": name,
        "given_name": given_name,
        "family_name": family_name,
        "email": email,
        "upn": email,
        "preferred_username": email,
        "roles": DYNAMIC_CLAIMS_CONFIG.get("default_roles", ["User"]),
        "groups": DYNAMIC_CLAIMS_CONFIG.get("default_groups", ["default-group"]),
    }
    
    return claims


def generate_deterministic_uuid(seed: str) -> str:
    """
    Genera un UUID deterministico da una stringa seed.
    Stessa seed = stesso UUID.
    
    Args:
        seed: Stringa da cui generare l'UUID
        
    Returns:
        UUID string
    """
    hash_value = hashlib.sha256(seed.encode()).hexdigest()
    return str(uuid.UUID(hash_value[:32]))
