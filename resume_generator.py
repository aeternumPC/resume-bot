"""
Генератор резюме: PDF (красивый) + текст для Telegram
"""

import os
import tempfile
import urllib.request
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = "/tmp/fonts"
FONT_REGULAR = os.path.join(FONT_DIR, "DejaVuSans.ttf")
FONT_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

FONT_URLS = {
    FONT_REGULAR: "https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-fonts-ttf-2.37.tar.bz2",
}

def ensure_fonts():
    os.makedirs(FONT_DIR, exist_ok=True)
    
    if not os.path.exists(FONT_REGULAR):
        # Скачиваем напрямую с sourceforge
        urllib.request.urlretrieve(
            "https://sourceforge.net/projects/dejavu/files/dejavu/2.37/dejavu-fonts-ttf-2.37.tar.bz2/download",
            "/tmp/dejavu.tar.bz2"
        )
        import tarfile
        with tarfile.open("/tmp/dejavu.tar.bz2", "r:bz2") as tar:
            for member in tar.getmembers():
                if member.name.endswith("DejaVuSans.ttf"):
                    member.name = "DejaVuSans.ttf"
                    tar.extract(member, FONT_DIR)
                elif member.name.endswith("DejaVuSans-Bold.ttf"):
                    member.name = "DejaVuSans-Bold.ttf"
                    tar.extract(member, FONT_DIR)

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

    return f"""📋 *РЕЗЮМЕ*
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
_Создано с помощью @your_resume_helper_bot_""".strip()


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
        pdf_path, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm, bottomMargin=20*mm
    )

    def ms(name_, bold=False, size=10, color=TEXT_COLOR, align=TA_LEFT, sb=0, sa=4, leading=16):
        return ParagraphStyle(name_, fontName='DejaVu-Bold' if bold else 'DejaVu',
            fontSize=size, textColor=color, alignment=align,
            spaceBefore=sb, spaceAfter=sa, leading=leading)

    s_name    = ms('N', bold=True, size=24, color=colors.white, align=TA_CENTER, leading=28)
    s_prof    = ms('P', size=13, color=colors.HexColor('#c5cae9'), align=TA_CENTER, leading=18)
    s_sec     = ms('S', bold=True, size=11, color=ACCENT, sb=14, sa=4)
    s_body    = ms('B', size=10, color=TEXT_COLOR)
    s_contact = ms('C', size=10, color=MUTED)
    s_footer  = ms('F', size=8, color=MUTED, align=TA_CENTER, sb=6)

    story = []

    ht = Table([[Paragraph(name, s_name)], [Paragraph(profession, s_prof)]], colWidths=[170*mm])
    ht.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK_BLUE),
        ('TOPPADDING', (0,0), (-1,0), 14),
        ('BOTTOMPADDING', (0,-1), (-1,-1), 14),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(ht)
    story.append(Spacer(1, 10))

    def section(title, content, contact=False):
        story.append(Paragraph(title.upper(), s_sec))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6))
        story.append(Paragraph(content.replace('\n', '<br/>'), s_contact if contact else s_body))

    section("Контакты", contacts, contact=True)
    section("Опыт работы", experience)
    section("Навыки", "  •  ".join([s.strip() for s in skills.split(',') if s.strip()]))
    section("Образование", education)

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED))
    story.append(Paragraph("<i>Создано с помощью Resume Bot</i>", s_footer))

    doc.build(story)
    return pdf_path
