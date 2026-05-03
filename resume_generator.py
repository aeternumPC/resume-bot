"""
Генератор резюме: PDF (красивый) + текст для Telegram
"""

import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def generate_text_resume(data: dict) -> str:
    """Генерирует текстовое резюме для Telegram (Markdown)"""
    name = data.get('name', '')
    profession = data.get('profession', '')
    experience = data.get('experience', '')
    skills = data.get('skills', '')
    education = data.get('education', '')
    contacts = data.get('contacts', '')

    text = f"""
📋 *РЕЗЮМЕ*
━━━━━━━━━━━━━━━━━━━━

👤 *{name}*
💼 {profession}

━━━━━━━━━━━━━━━━━━━━
📞 *КОНТАКТЫ*
{contacts}

━━━━━━━━━━━━━━━━━━━━
🏢 *ОПЫТ РАБОТЫ*
{experience}

━━━━━━━━━━━━━━━━━━━━
⚡ *НАВЫКИ*
{skills}

━━━━━━━━━━━━━━━━━━━━
🎓 *ОБРАЗОВАНИЕ*
{education}

━━━━━━━━━━━━━━━━━━━━
_Создано с помощью @ResumeBot_
"""
    return text.strip()


def generate_pdf(data: dict) -> str:
    """Генерирует красивое PDF резюме, возвращает путь к файлу"""
    name = data.get('name', 'Резюме')
    profession = data.get('profession', '')
    experience = data.get('experience', '')
    skills = data.get('skills', '')
    education = data.get('education', '')
    contacts = data.get('contacts', '')

    # Временный файл
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = tmp.name
    tmp.close()

    # Цвета
    DARK_BLUE = colors.HexColor('#1a237e')
    ACCENT = colors.HexColor('#3949ab')
    LIGHT_GRAY = colors.HexColor('#f5f5f5')
    TEXT_COLOR = colors.HexColor('#212121')
    MUTED = colors.HexColor('#757575')

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )

    styles = getSampleStyleSheet()

    style_name = ParagraphStyle(
        'Name',
        fontSize=26,
        textColor=colors.white,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    style_profession = ParagraphStyle(
        'Profession',
        fontSize=13,
        textColor=colors.HexColor('#c5cae9'),
        fontName='Helvetica',
        alignment=TA_CENTER,
        spaceAfter=0,
    )
    style_section = ParagraphStyle(
        'Section',
        fontSize=12,
        textColor=ACCENT,
        fontName='Helvetica-Bold',
        spaceBefore=14,
        spaceAfter=4,
    )
    style_body = ParagraphStyle(
        'Body',
        fontSize=10,
        textColor=TEXT_COLOR,
        fontName='Helvetica',
        leading=16,
        spaceAfter=4,
    )
    style_contacts = ParagraphStyle(
        'Contacts',
        fontSize=10,
        textColor=MUTED,
        fontName='Helvetica',
        leading=16,
    )

    story = []

    # --- Шапка (цветной блок через таблицу) ---
    header_data = [[
        Paragraph(name, style_name),
    ], [
        Paragraph(profession, style_profession),
    ]]
    header_table = Table(header_data, colWidths=[170*mm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_BLUE),
        ('TOPPADDING', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 14),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [DARK_BLUE]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    def section(title, content):
        story.append(Paragraph(title.upper(), style_section))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6))
        story.append(Paragraph(content.replace('\n', '<br/>'), style_body))

    # Контакты
    story.append(Paragraph("КОНТАКТЫ", style_section))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6))
    story.append(Paragraph(contacts.replace('\n', '<br/>'), style_contacts))

    # Опыт
    section("Опыт работы", experience)

    # Навыки — красиво разбиваем по запятой
    skills_list = [s.strip() for s in skills.split(',') if s.strip()]
    skills_text = "  •  ".join(skills_list)
    section("Навыки", skills_text)

    # Образование
    section("Образование", education)

    # Футер
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED))
    story.append(Paragraph(
        "<i>Создано с помощью Resume Bot</i>",
        ParagraphStyle('Footer', fontSize=8, textColor=MUTED, alignment=TA_CENTER, spaceBefore=6)
    ))

    doc.build(story)
    return pdf_path
