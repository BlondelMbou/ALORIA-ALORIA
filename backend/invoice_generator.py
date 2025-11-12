"""
Module de génération de factures PDF pour ALORIA AGENCY
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import io

def generate_invoice_pdf(payment_data, client_data):
    """
    Générer une facture PDF pour un paiement
    
    Args:
        payment_data: dict contenant les infos du paiement (amount, invoice_number, created_at, etc.)
        client_data: dict contenant les infos du client (full_name, email, phone, etc.)
    
    Returns:
        BytesIO: Buffer contenant le PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Style personnalisé pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#FF6B35'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Style pour les informations
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        fontName='Helvetica-Bold'
    )
    
    # En-tête avec logo/nom de l'agence
    header = Paragraph("<b>ALORIA AGENCY</b>", title_style)
    elements.append(header)
    
    tagline = Paragraph(
        "<i>Votre Partenaire Immigration Canada & France</i>",
        ParagraphStyle('Tagline', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#1E293B'), alignment=TA_CENTER, spaceAfter=20)
    )
    elements.append(tagline)
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Titre FACTURE
    invoice_title = Paragraph(
        f"<b>FACTURE N° {payment_data.get('invoice_number', 'N/A')}</b>",
        ParagraphStyle('InvoiceTitle', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#1E293B'), alignment=TA_CENTER, spaceAfter=20)
    )
    elements.append(invoice_title)
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Informations de l'agence et du client côte à côte
    info_data = [
        [
            Paragraph("<b>ALORIA AGENCY</b><br/>Agence d'Immigration<br/>Email: contact@aloria-agency.com<br/>Tél: +237 XXX XXX XXX", info_style),
            Paragraph(f"<b>FACTURÉ À:</b><br/>{client_data.get('full_name', 'N/A')}<br/>Email: {client_data.get('email', 'N/A')}<br/>Tél: {client_data.get('phone', 'N/A')}", info_style)
        ]
    ]
    
    info_table = Table(info_data, colWidths=[3*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(info_table)
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Date de facturation
    created_date = payment_data.get('created_at', datetime.now().isoformat())
    if isinstance(created_date, str):
        try:
            created_date = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
        except:
            created_date = datetime.now()
    
    date_para = Paragraph(
        f"<b>Date:</b> {created_date.strftime('%d/%m/%Y')}",
        ParagraphStyle('DateStyle', parent=styles['Normal'], fontSize=10, alignment=TA_RIGHT, spaceAfter=20)
    )
    elements.append(date_para)
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Tableau des services
    currency = payment_data.get('currency', 'CFA')
    amount = float(payment_data.get('amount', 0))
    description = payment_data.get('description', 'Service d\'immigration')
    
    service_data = [
        ['DESCRIPTION', 'QUANTITÉ', 'PRIX UNITAIRE', 'MONTANT'],
        [description, '1', f'{amount:,.0f} {currency}', f'{amount:,.0f} {currency}']
    ]
    
    service_table = Table(service_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    service_table.setStyle(TableStyle([
        # En-tête
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        
        # Contenu
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        
        # Grille
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(service_table)
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Total
    total_data = [
        ['', '', 'SOUS-TOTAL:', f'{amount:,.0f} {currency}'],
        ['', '', '<b>TOTAL À PAYER:</b>', f'<b>{amount:,.0f} {currency}</b>']
    ]
    
    total_table = Table(total_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (2, 1), (-1, 1), 2, colors.HexColor('#FF6B35')),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#FF6B35')),
    ]))
    elements.append(total_table)
    
    elements.append(Spacer(1, 0.4*inch))
    
    # Statut du paiement
    status = payment_data.get('status', 'pending')
    status_color = colors.green if status == 'confirmed' else colors.orange
    status_text = 'PAYÉ' if status == 'confirmed' else 'EN ATTENTE'
    
    status_para = Paragraph(
        f"<b>STATUT: {status_text}</b>",
        ParagraphStyle('StatusStyle', parent=styles['Normal'], fontSize=12, textColor=status_color, alignment=TA_CENTER, spaceAfter=20)
    )
    elements.append(status_para)
    
    # Informations de paiement
    payment_method = payment_data.get('payment_method', 'N/A')
    payment_info = Paragraph(
        f"<b>Mode de paiement:</b> {payment_method}",
        ParagraphStyle('PaymentInfo', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, spaceAfter=10)
    )
    elements.append(payment_info)
    
    if status == 'confirmed' and payment_data.get('confirmed_at'):
        confirmed_date = payment_data.get('confirmed_at')
        if isinstance(confirmed_date, str):
            try:
                confirmed_date = datetime.fromisoformat(confirmed_date.replace('Z', '+00:00'))
                confirmed_para = Paragraph(
                    f"<b>Date de confirmation:</b> {confirmed_date.strftime('%d/%m/%Y à %H:%M')}",
                    ParagraphStyle('ConfirmedInfo', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, spaceAfter=20)
                )
                elements.append(confirmed_para)
            except:
                pass
    
    elements.append(Spacer(1, 0.5*inch))
    
    # Notes et conditions
    notes = Paragraph(
        "<b>Notes:</b><br/>Merci pour votre confiance en ALORIA AGENCY. Cette facture est générée automatiquement et constitue un justificatif de paiement officiel.<br/><br/>"
        "<b>Conditions:</b> Tous les paiements sont non remboursables sauf stipulation contraire dans le contrat de service.",
        ParagraphStyle('NotesStyle', parent=styles['Normal'], fontSize=9, textColor=colors.grey, spaceAfter=20)
    )
    elements.append(notes)
    
    # Pied de page
    footer = Paragraph(
        "<i>ALORIA AGENCY - Votre réussite est notre mission</i>",
        ParagraphStyle('FooterStyle', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    )
    elements.append(footer)
    
    # Construire le PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer

