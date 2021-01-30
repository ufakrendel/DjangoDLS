import json

from django.core.files import File
from django.core.files.storage import default_storage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
import redis
import pickle

from DLSClasses.RecognizeFileData import RecognizeFileData
from DLSClasses.RecognizeStatusEnum import RecognizeStatusEnum
from DjangoDLS.drawWorker import draw_rectangle

#инициализируем редис-сервис, используется для очереди
r = redis.Redis(db=0, charset='utf-8')


def index(request):
    #если POST, значит прилетел файл. Сохраняем его, создаем для него обертку и отправляем ее в Redis очередь
    if request.method == "POST":
        file = request.FILES['file']
        file_name = default_storage.save(file.name, file)
        file_url = default_storage.url(file_name)
        file_data: RecognizeFileData = RecognizeFileData(file_name=file_name, file_url=file_url)
        file_data.print_file()
        file_data_bytes = pickle.dumps(file_data)

        r.lpush('queue', file_data_bytes)
        return render(request, 'DjangoDLS/index.html', {'file_url': file_url, 'status': RecognizeStatusEnum.New, 'file_id': file_data.file_id, 'result': None})
    else:
    # Get - показываем заглавную страницу
        return render(request, "DjangoDLS/index.html")

# не используется, для целей Debug
@require_http_methods(['POST'])
def save_file(request):
    file = request.FILES['file']
    file_name = default_storage.save(file.name, file)

    file_url = default_storage.url(file_name)

    file_data: RecognizeFileData = RecognizeFileData(file_name=file_name, file_url=file_url)
    file_data.print_file()
    file_data_bytes = pickle.dumps(file_data)

    r.lpush('queue', file_data_bytes)
    return redirect('index', file_url=file_url)
    #return render(request, 'DjangoDLS/index.html', {'file_url': file_url, 'status': RecognizeStatusEnum.New})


# не используется, для целей Debug
@require_http_methods(['GET'])
def get_file(request, file):
    file_name = request.GET.get('filename', None)
    if file_name is not None:
        try:
            file: File = default_storage.open(file_name)
            file_url = default_storage.url(file_name)
        except Exception as e:
            return HttpResponse(str(e))

    if file is not None and file.size > 0:
        return render(request, 'DjangoDLS/index.html', {'file_url': file_url})
    else:
        return HttpResponse('Not Ok')

# Для проверки результатов с фронта. Если ничего нет, то возвращаем статус IN_WORK, до след. запроса...
# Если возвращаем статус 500 фронт сообщает об ошибке в обработке и опрос прекращается
# Если возвратились данные, то просто отсылаем статус. Там будет редирект на страницу с результатами.
def check_result(request, file_id):

    if file_id is None:
        return HttpResponse('No data', status=500)

    file_data: RecognizeFileData = get_file_data_by_id(file_id)

    if file_data is None:
        data = json.dumps(RecognizeStatusEnum.InWork)
    else:
        data = json.dumps(file_data.status)

    return JsonResponse(data, safe=False)


#после того как фронт получает статус ENDED редиректит сюда. Рисуем на файле прямоугольники и возвращаем на фронт
@require_http_methods(['GET'])
def get_file_by_id(request, file_id):
    #file_id = request.GET.get('file_id', None)

    if file_id is None:
        return HttpResponse('No data', status=404)

    file_data: RecognizeFileData = get_file_data_by_id(file_id)

    if file_data is None:
        return HttpResponse('No data', status=404)

    img_path = default_storage.path(file_data.file_name)
    bordered_img = draw_rectangle(img_path, file_data.result)

    bordered_url = default_storage.url(bordered_img)

    file_data.result.sort(key=lambda x: x.score, reverse=True)

    if file_data is not None:
        return render(request, 'DjangoDLS/index.html',
                      {'file_url': bordered_url, 'result': file_data.result})
        return HttpResponse('Not Ok')

# Пакуем данные для Redis
def pickle_file_data(file_data: RecognizeFileData):
    file_data_bytes = pickle.dumps(file_data)
    return file_data_bytes

# Получаем из Redis обработанные данные
def get_file_data_by_id(file_id):
    file_data_byte = r.get(file_id)
    if file_data_byte is None:
        return None

    file_data: RecognizeFileData = pickle.loads(file_data_byte)

    return file_data
