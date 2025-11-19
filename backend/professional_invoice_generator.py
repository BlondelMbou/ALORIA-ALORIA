"""
Générateur de factures PDF professionnel pour ALORIA AGENCY
Utilise ReportLab pour créer des factures élégantes et conformes
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from datetime import datetime
import io


def generate_professional_invoice_pdf(invoice_data: dict) -> bytes:
    """
    Génère une facture PDF professionnelle
    
    Args:
        invoice_data: dict avec les clés:
            - invoice_number: str
            - client_name: str
            - client_email: str (optionnel)
            - client_phone: str (optionnel)
            - amount: float
            - currency: str
            - payment_method: str
            - description: str
            - created_at: str (ISO format)
            - status: str
    
    Returns:
        bytes: Contenu du PDF
    """
    buffer = io.BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           topMargin=2*cm, bottomMargin=2*cm,
                           leftMargin=2*cm, rightMargin=2*cm)
    
    # Container pour les éléments
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E3A8A'),  # Bleu nuit
        spaceAfter=30,
        alignment=1  # Centré
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=6
    )
    
    # ====================
    # EN-TÊTE - ALORIA AGENCY
    # ====================
    title = Paragraph("<b>ALORIA AGENCY</b>", title_style)
    elements.append(title)
    
    # Informations de l'agence
    agency_info = [
        "45 Avenue Victor Hugo",
        "75016 Paris, France",
        "Tél: +33 1 75 43 89 12",
        "Email: contact@aloria-agency.com",
        "SIRET: 123 456 789 00012"
    ]
    
    for line in agency_info:
        p = Paragraph(f"<font size=10>{line}</font>", normal_style)
        elements.append(p)
    
    elements.append(Spacer(1, 1*cm))
    
    # Ligne de séparation
    line_data = [['']]
    line_table = Table(line_data, colWidths=[17*cm])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#F97316'))  # Orange
    ]))
    elements.append(line_table)
    elements.append(Spacer(1, 0.5*cm))
    
    # ====================
    # TITRE FACTURE
    # ====================
    invoice_title = Paragraph(f"<b>FACTURE N° {invoice_data.get('invoice_number', 'N/A')}</b>", heading_style)
    elements.append(invoice_title)
    
    # Date de facturation
    created_at = invoice_data.get('created_at', datetime.now().isoformat())
    try:
        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        formatted_date = date_obj.strftime('%d/%m/%Y')
    except:
        formatted_date = created_at[:10]
    
    date_p = Paragraph(f"<b>Date:</b> {formatted_date}", normal_style)
    elements.append(date_p)
    
    # Statut
    status = invoice_data.get('status', 'En attente')
    status_color = '#10B981' if status.lower() == 'confirmed' else '#F59E0B'
    status_p = Paragraph(f"<b>Statut:</b> <font color='{status_color}'>{status.capitalize()}</font>", normal_style)
    elements.append(status_p)
    
    elements.append(Spacer(1, 1*cm))
    
    # ====================
    # INFORMATIONS CLIENT
    # ====================
    client_heading = Paragraph("<b>Informations Client</b>", heading_style)
    elements.append(client_heading)
    
    client_data = [
        ['Nom:', invoice_data.get('client_name', 'N/A')],
    ]
    
    if invoice_data.get('client_email'):
        client_data.append(['Email:', invoice_data.get('client_email')])
    
    if invoice_data.get('client_phone'):
        client_data.append(['Téléphone:', invoice_data.get('client_phone')])
    
    client_table = Table(client_data, colWidths=[4*cm, 13*cm])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(client_table)
    
    elements.append(Spacer(1, 1*cm))
    
    # ====================
    # DÉTAILS DE LA FACTURE
    # ====================
    details_heading = Paragraph("<b>Détails des Services</b>", heading_style)
    elements.append(details_heading)
    
    # Tableau des services
    service_data = [
        ['Description', 'Montant'],
        [
            invoice_data.get('description', 'Services d\'immigration et conseil'),
            f"{invoice_data.get('amount', 0):,.0f} {invoice_data.get('currency', 'CFA')}"
        ]
    ]
    
    service_table = Table(service_data, colWidths=[12*cm, 5*cm])
    service_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),  # Bleu nuit
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ]))
    elements.append(service_table)
    
    elements.append(Spacer(1, 0.5*cm))
    
    # ====================
    # TOTAL
    # ====================
    total_data = [
        ['MONTANT TOTAL', f"{invoice_data.get('amount', 0):,.0f} {invoice_data.get('currency', 'CFA')}"]
    ]
    
    total_table = Table(total_data, colWidths=[12*cm, 5*cm])
    total_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F97316')),  # Orange
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(total_table)
    
    elements.append(Spacer(1, 0.5*cm))
    
    # Méthode de paiement
    payment_method = invoice_data.get('payment_method', 'N/A')
    payment_p = Paragraph(f"<b>Méthode de paiement:</b> {payment_method}", normal_style)
    elements.append(payment_p)
    
    elements.append(Spacer(1, 1.5*cm))
    
    # ====================
    # PIED DE PAGE
    # ====================
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=1  # Centré
    )
    
    footer_text = """
    <b>Merci de votre confiance</b><br/>
    ALORIA AGENCY - Votre partenaire pour l'immigration<br/>
    <i>Cette facture est générée automatiquement et ne nécessite pas de signature</i>
    """
    footer = Paragraph(footer_text, footer_style)
    elements.append(footer)
    
    # Construire le PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer.getvalue()


if __name__ == "__main__":
    # Test
    test_data = {
        'invoice_number': 'ALO-20251119-TEST001',
        'client_name': 'Jean Dupont',
        'client_email': 'jean.dupont@example.com',
        'client_phone': '+33 6 12 34 56 78',
        'amount': 150000,
        'currency': 'CFA',
        'payment_method': 'Virement bancaire',
        'description': 'Services de conseil et accompagnement pour visa étudiant Canada',
        'created_at': '2025-11-19T10:30:00',
        'status': 'confirmed'
    }
    
    pdf_bytes = generate_professional_invoice_pdf(test_data)
    
    with open('test_facture.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print("✅ Facture de test générée: test_facture.pdf")
