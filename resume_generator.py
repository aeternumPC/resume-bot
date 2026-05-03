"""
Генератор резюме: PDF (красивый) + текст для Telegram
Исправлена поддержка кириллицы через DejaVu шрифты
"""

import os
import tempfile
import urllib.request
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


FONT_DIR = "/tmp/fonts"
FONT_REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

FONT_URLS = {
    FONT_REGULAR: "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf",
    FONT_BOLD: "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf",
}

def ensure_fonts():
    os.makedirs(FONT_DIR, exist_ok=True)
    for path, url in FONT_URLS.items():
        if not os.path.exists(path):
            urllib.request.urlretrieve(url, path)
    try:
        pdfmetrics.registerFont(TTFont("DejaVu", FONT_REGULAR))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", FONT_BOLD))
    except Exception:
        pass


def generate_text_resume(data: dict) -> str:
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
_Создано с помощью @your_resume_helper_bot
"""
    return text.strip()


def generate_pdf(data: dict) -> str:
    ensure_fonts()

    name = data.get('name', 'Резюме')
    profession = data.get('profession', '')
    experience = data.get('experience', '')
    skills = data.get('skills', '')
    education = data.get('education', '')
    contacts = data.get('contacts', '')

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf_path = tmp.name
    tmp.close()

    DARK_BLUE = colors.HexColor('#1a237e')
    ACCENT = colors.HexColor('#3949ab')
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

    def make_style(name_, font='DejaVu', size=10, color=TEXT_COLOR, align=TA_LEFT, bold=False, space_before=0, space_after=4, leading=16):
        return ParagraphStyle(
            name_,
            fontName='DejaVu-Bold' if bold else font,
            fontSize=size,
            textColor=color,
            alignment=align,
            spaceBefore=space_before,
            spaceAfter=space_after,
            leading=leading,
        )

    s_name       = make_style('Name', size=24, color=colors.white, align=TA_CENTER, bold=True, leading=28)
    s_profession = make_style('Prof', size=13, color=colors.HexColor('#c5cae9'), align=TA_CENTER, leading=18)
    s_section    = make_style('Sec',  size=11, color=ACCENT, bold=True, space_before=14, space_after=4)
    s_body       = make_style('Body', size=10, color=TEXT_COLOR, space_after=4)
    s_contacts   = make_style('Cont', size=10, color=MUTED, space_after=4)
    s_footer     = make_style('Foot', size=8,  color=MUTED, align=TA_CENTER, space_before=6)

    story = []

    header_data = [
        [Paragraph(name, s_name)],
        [Paragraph(profession, s_profession)],
    ]
    header_table = Table(header_data, colWidths=[170*mm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_BLUE),
        ('TOPPADDING',    (0, 0), (-1, 0),  14),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 14),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    def section(title, content, contact=False):
        story.append(Paragraph(title.upper(), s_section))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6))
        story.append(Paragraph(content.replace('\n', '<br/>'), s_contacts if contact else s_body))

    section("Контакты", contacts, contact=True)
    section("Опыт работы", experience)

    skills_list = [s.strip() for s in skills.split(',') if s.strip()]
    section("Навыки", "  •  ".join(skills_list))
    section("Образование", education)

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED))
    story.append(Paragraph("<i>Создано с помощью Resume Bot</i>", s_footer))

    doc.build(story)
    return pdf_path
