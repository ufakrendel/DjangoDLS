from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# метод по рисованию на исходном файле. Возвращается копия с прямоугольниками и подписями
# на вход подается результат с детектора и порог выше которого отрисовываем границы
def draw_rectangle(file_name, predict_result, score_thr = 0.8):
    base_image = Image.open(file_name).convert('RGBA')
    base_image.load()
    draw = ImageDraw.Draw(base_image)

    fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', int(base_image.size[1] / 30) )
    txt_draw = Image.new('RGBA', base_image.size, (255, 255, 255, 0))
    dtxt = ImageDraw.Draw(txt_draw)

    for res in predict_result:
        if res.score < score_thr:
            continue

        r = res.box
        draw.line([r[0], r[1], r[2], r[1]], fill='red', width=4)
        draw.line([r[0], r[1], r[0], r[3]], fill='red', width=4)
        draw.line([r[2], r[1], r[2], r[3]], fill='red', width=4)
        draw.line([r[0], r[3], r[2], r[3]], fill='red', width=4)

        dtxt.text((r[0] + 10, r[1] + 10), str(res.label_text) + ', {:.2%}'.format(res.score), font=fnt, fill='red')

    base_image = Image.alpha_composite(base_image, txt_draw)

    file_path = Path(file_name)
    file_wo_ext = file_path.stem
    new_name = file_path.name.replace(file_wo_ext, file_wo_ext+'_bordered')

    new_filename = Path.joinpath(file_path.parents[0], new_name)

    base_image.convert('RGB').save(new_filename)
    return new_name
