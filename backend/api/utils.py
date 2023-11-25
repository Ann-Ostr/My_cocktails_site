from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas


def draw_shopping_cart(response, ingredients):
    begin_position_x, begin_position_y = 30, 730
    canvas = Canvas(response, pagesize=A4)
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))
    canvas.setFont('DejaVuSerif', 14)
    canvas.setTitle('СПИСОК ПОКУПОК')
    canvas.drawString(begin_position_x,
                      begin_position_y + 40, 'Список покупок: ')
    canvas.setFont('DejaVuSerif', 10)
    for number, item in enumerate(ingredients, start=1):
        if begin_position_y < 100:
            begin_position_y = 730
            canvas.showPage()
            canvas.setFont('DejaVuSerif', 12)
        canvas.drawString(begin_position_x,
                          begin_position_y,
                          f'№{number}: {item["name"]} - '
                          f'{item["total"]}'
                          f'{item["unit"]}')
        begin_position_y -= 30
    canvas.showPage()
    canvas.save()
