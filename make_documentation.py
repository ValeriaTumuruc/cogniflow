from pathlib import Path
from PIL import Image, ImageDraw
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A5
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx import Document
from docx.shared import Inches, Pt

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'documentation';OUT.mkdir(exist_ok=True)
BASE='https://valeriatumuruc.github.io/cogniflow/'
pdfmetrics.registerFont(TTFont('Barlow',str(ROOT/'assets/Barlow-Regular.ttf')))
pdfmetrics.registerFont(TTFont('BarlowBold',str(ROOT/'assets/Barlow-Bold.ttf')))
green=HexColor('#14342B');linen=HexColor('#ECEBE4');peach=HexColor('#D06B47')
links={}
for source in ['flyer_library','flyer_campus','student_group']:
 url=BASE+'?utm_source='+source+'&utm_medium='+('qr' if source.startswith('flyer') else 'social')+'&utm_campaign=phase4'
 links[source]=url
 widget=QrCodeWidget(url,barLevel='M');widget.qr.make();modules=widget.qr.modules
 n=len(modules);scale=12;quiet=4
 im=Image.new('RGB',((n+quiet*2)*scale,)*2,'white');draw=ImageDraw.Draw(im)
 for y,row in enumerate(modules):
  for x,on in enumerate(row):
   if on:draw.rectangle(((x+quiet)*scale,(y+quiet)*scale,(x+quiet+1)*scale-1,(y+quiet+1)*scale-1),fill='#14342B')
 im.save(OUT/(source+'-qr.png'))
c=Canvas(str(OUT/'Cogniflow flyers.pdf'),pagesize=A5)
for source in ['flyer_library','flyer_campus']:
 w,h=A5;c.setFillColor(linen);c.rect(0,0,w,h,fill=1,stroke=0)
 c.setFillColor(green);c.setFont('BarlowBold',24);c.drawString(32,h-48,'cogniflow')
 c.setFillColor(peach);c.rect(32,h-72,44,5,fill=1,stroke=0)
 c.setFillColor(green);c.setFont('BarlowBold',42)
 for i,line in enumerate(['Your next break','belongs in','the plan.']):c.drawString(32,h-137-i*43,line)
 c.setFont('Barlow',15)
 for i,line in enumerate(['Help us explore healthier study habits.','See our Figma prototype and discover','a study companion with room for you.']):c.drawString(32,h-285-i*20,line)
 c.drawImage(str(OUT/(source+'-qr.png')),32,88,width=124,height=124)
 c.setFont('BarlowBold',19);c.drawString(174,181,'Scan to explore')
 c.setFont('Barlow',13)
 for i,line in enumerate(['For higher-education','students aged 18+.','A concept in development.']):c.drawString(174,155-i*18,line)
 c.setFont('Barlow',12);c.drawString(32,59,'valeriatumuruc.github.io/cogniflow/')
 c.setFont('Barlow',10);c.drawString(32,34,'Team 6 · Digital Startup project');c.drawRightString(w-32,34,source.replace('flyer_','').capitalize()+' QR')
 c.showPage()
c.save()
(OUT/'recruitment-links.txt').write_text('\n'.join(k+': '+v for k,v in links.items()),encoding='utf8')
d=Document();s=d.sections[0];s.top_margin=s.bottom_margin=Inches(.7);s.left_margin=s.right_margin=Inches(.8)
style=d.styles['Normal'];style.font.name='Arial';style.font.size=Pt(10);style.paragraph_format.space_after=Pt(7)
for name in ['Title','Heading 1','Heading 2']:
 d.styles[name].font.name='Arial';d.styles[name].font.color.rgb=__import__('docx').shared.RGBColor.from_string('14342B')
d.styles['Title'].font.color.rgb=__import__('docx').shared.RGBColor(0,0,0)
d.styles['Subtitle'].font.color.rgb=__import__('docx').shared.RGBColor(0,0,0)
d.styles['Subtitle'].font.italic=False
for st in d.styles:
 for border in st.element.xpath('.//w:pBdr'):
  border.getparent().remove(border)
d.add_paragraph('Documentation experiment 2',style='Title')
d.add_paragraph('Cogniflow landing page',style='Subtitle')
d.add_heading('Landing page and current status',1)
d.add_paragraph(BASE)
d.add_paragraph('Cogniflow is a study companion concept that brings study sessions and optional well-being check-ins together. The published page introduces the idea and invites higher-education students to join a testing list. The headline is “You’ve read that page three times. Take a breath.” It includes a description, a call-to-action and a signup form.')
d.add_paragraph('As of 27 November 2026, the public signup is not working because the hosted registration service has not been connected. We therefore cannot report completed registrations or a signup conversion rate. The refreshed local version uses a bold sans-serif font and includes a click-to-load preview of our Figma prototype. It has not yet replaced the published page. The prototype uses sample data and is not evidence of a functioning product.')
d.add_heading('How we plan to bring students to the page',1)
d.add_paragraph('We plan to place A5 flyers in permitted library and campus noticeboard areas after checking placement rules. Each flyer has a QR code linking to the landing page. The library and campus versions use different tagged links, so we can compare recruitment sources once measurement works. We will record the location, date, number of flyers and printing cost. No flyer distribution is claimed yet.')
d.add_paragraph('We also plan to share the page in relevant student groups, with moderator permission where required, and through student associations and personal invitations. Each channel will use its own tagged link. Posts will explain that this is a student project in development and invite people to explore the prototype and, once signup works, volunteer for feedback.')
d.add_heading('How we will measure engagement and interest',1)
d.add_paragraph('Once the selected service is connected and tested, we will record eligible unique visitors, call-to-action clickers and completed unique registrations in the same reporting window. Channel tags identify recruitment sources. We will calculate signup conversion as completed registrations from the measured visitor cohort divided by eligible unique visitors in that cohort, multiplied by 100. Signups outside that cohort will be reported separately.')
d.add_paragraph('Our proposed V2 criterion is at least 10% signup conversion from a minimum of 100 eligible unique visitors. We will exclude team tests, repeated submissions and obvious spam using a recorded rule. Visits without measurement consent will not enter the measured cohort; this creates a sampling limitation we will report. QR scans, button clicks and Figma opens are not completed registrations. We cannot infer payment, retention or improved health from this experiment.')
d.add_paragraph('Until the service is working, all traffic and signup outcomes remain unmeasured. After deployment, we will add actual dates, counts, exclusions, cost, findings and next steps.')
d.add_page_break();d.add_heading('Full layout of the published page',1)
d.add_paragraph('Captured from the public URL on 27 November 2026. This is the published version before the local typography and Figma-preview update.',style='Caption')
img=OUT/'landing-page-published-before-update.jpg'
if img.exists():
 width,height=Image.open(img).size
 d.add_picture(str(img),height=Inches(8.5))
for par in d.paragraphs:
 for border in par._p.xpath('.//w:pBdr'):
  border.getparent().remove(border)
d.save(OUT/'Documentation experiment 2.docx')
print('Created documentation, two A5 flyer pages, three QR codes and recruitment links.')
