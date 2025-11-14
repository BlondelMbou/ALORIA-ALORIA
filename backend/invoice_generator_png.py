"""
Générateur de factures au format PNG - Design moderne et compact
ALORIA AGENCY
"""

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

def generate_invoice_png(invoice_data: dict, output_path: str) -> str:
    """
    Génère une facture moderne au format PNG
    
    Args:
        invoice_data: Dict contenant les données de la facture
        output_path: Chemin complet du fichier PNG à créer
    
    Returns:
        str: Chemin du fichier généré
    """
    # Dimensions compactes (800x600px)
    width = 800
    height = 600
    
    # Couleurs ALORIA (bleu nuit + orange)
    bg_color = (15, 23, 42)  # Bleu nuit #0F172A
    white = (255, 255, 255)
    orange = (251, 146, 60)  # Orange #FB923C
    gray = (148, 163, 184)  # Gris #94A3B8
    light_bg = (30, 41, 59)  # #1E293B
    
    # Créer l'image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Charger les polices (utiliser polices système par défaut)
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        # Fallback si les polices ne sont pas disponibles
        font_title = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # === HEADER ===
    # Logo/Nom entreprise
    draw.text((40, 30), "ALORIA", fill=orange, font=font_title)
    draw.text((40, 70), "AGENCY", fill=white, font=font_medium)
    
    # Ligne de séparation
    draw.rectangle([(40, 110), (width - 40, 113)], fill=orange)
    
    # === FACTURE INFO (Droite) ===
    draw.text((width - 280, 30), "FACTURE", fill=white, font=font_large)
    draw.text((width - 280, 65), f"N° {invoice_data['invoice_number']}", fill=gray, font=font_small)
    draw.text((width - 280, 85), f"Date: {invoice_data['date']}", fill=gray, font=font_small)
    
    # === CLIENT INFO (Encadré) ===
    y_pos = 140
    # Encadré client
    draw.rectangle([(40, y_pos), (width - 40, y_pos + 80)], fill=light_bg, outline=orange, width=2)
    
    draw.text((60, y_pos + 15), "CLIENT", fill=orange, font=font_medium)
    draw.text((60, y_pos + 45), invoice_data['client_name'], fill=white, font=font_medium)
    
    # === DÉTAILS PAIEMENT (Encadré) ===
    y_pos = 245
    draw.rectangle([(40, y_pos), (width - 40, y_pos + 120)], fill=light_bg, outline=gray, width=1)
    
    draw.text((60, y_pos + 15), "DESCRIPTION", fill=white, font=font_medium)
    
    # Description du service
    desc_text = invoice_data.get('description', 'Services d\'immigration')
    if len(desc_text) > 50:
        desc_text = desc_text[:47] + "..."
    draw.text((60, y_pos + 45), desc_text, fill=gray, font=font_small)
    
    # Méthode de paiement
    draw.text((60, y_pos + 70), f"Methode: {invoice_data['payment_method']}", fill=gray, font=font_small)
    
    # Date de paiement
    payment_date = invoice_data.get('created_at', '')
    if payment_date:
        try:
            dt = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
            payment_date_str = dt.strftime("%d/%m/%Y")
        except:
            payment_date_str = invoice_data['date']
    else:
        payment_date_str = invoice_data['date']
    draw.text((60, y_pos + 90), f"Paye le: {payment_date_str}", fill=gray, font=font_small)
    
    # === MONTANT (Encadré orange) ===
    y_pos = 390
    draw.rectangle([(40, y_pos), (width - 40, y_pos + 100)], fill=orange, outline=orange, width=2)
    
    draw.text((60, y_pos + 20), "MONTANT TOTAL", fill=white, font=font_medium)
    
    # Grand montant
    amount_text = f"{invoice_data['amount']:,.0f} {invoice_data['currency']}"
    draw.text((60, y_pos + 50), amount_text, fill=white, font=font_large)
    
    # === FOOTER ===
    y_pos = 510
    draw.text((40, y_pos), "ALORIA AGENCY - Bureau de Douala, Cameroun", fill=gray, font=font_small)
    draw.text((40, y_pos + 20), "Tel: +237 6XX XX XX XX | Email: contact@aloria-agency.com", fill=gray, font=font_small)
    draw.text((40, y_pos + 40), f"Facture generee le {datetime.now().strftime('%d/%m/%Y a %H:%M')}", fill=gray, font=font_small)
    
    # === WATERMARK ===
    draw.text((width - 150, height - 30), "PAYE", fill=(orange[0], orange[1], orange[2], 128), font=font_large)
    
    # Créer le dossier si nécessaire
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Sauvegarder l'image
    img.save(output_path, 'PNG', quality=95)
    
    return output_path
