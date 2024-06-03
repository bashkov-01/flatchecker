import os
import math
import numpy as np
import matplotlib

from .forms import DiagnoseForm

matplotlib.use('Agg')  # Use the non-interactive Agg backend
from matplotlib import pyplot as plt
from django.utils import timezone

from matplotlib.image import imread
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError, transaction
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from ultralytics import YOLO

# Load YOLO model
model = YOLO('/Users/sraperanosan/PycharmProjects/PRIT/runs/segment/train4/weights/best.pt')

def index(request):
    return render(request, 'main/main.html')

def results(request):
    diag_list = Diagnose.objects.all().order_by('id')
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        diagnose_id = request.POST.get('diagnose_id')
        diagnose = get_object_or_404(Diagnose, id=diagnose_id)
        return JsonResponse({
            'id': diagnose.id,
            'date_time': diagnose.date_time.strftime("%d.%m.%Y"),
            'note': diagnose.note,
            'diagnose': diagnose.diagnose,
            'photo_after': diagnose.photo_before.url if diagnose.photo_before else None,
            'patient_fio': get_object_or_404(PPatient, id=diagnose.patient_id).name +
            get_object_or_404(PPatient, id=diagnose.patient_id).second_name +
            get_object_or_404(PPatient, id=diagnose.patient_id).last_name,
        })
    return render(request, 'main/results.html',{'diag_list': diag_list})

def login(request):
    return render(request, 'main/login.html')

def find_img_file(filename, directory, extensions=None):
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    filename_without_extension = os.path.splitext(filename)[0]
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file == filename_without_extension + ext for ext in extensions):
                return os.path.join(root, file)
    return None

def find_txt_file(filename, directory):
    filename_without_extension = os.path.splitext(filename)[0]
    filename_txt = filename_without_extension + ".txt"
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == filename_txt:
                return os.path.join(root, file)
    return None

def to_pixel_coordinates(coordinates, image_width, image_height):
    pixel_coordinates = {}
    for class_id, points in coordinates.items():
        pixel_points = []
        for point in points:
            x_pixel = int(point[0] * image_width)
            y_pixel = int(point[1] * image_height)
            pixel_points.append((x_pixel, y_pixel))
        pixel_coordinates[class_id] = pixel_points
    return pixel_coordinates

def length_square(X, Y):
    x_diff = X[0] - Y[0]
    y_diff = X[1] - Y[1]
    return x_diff * x_diff + y_diff * y_diff

def calculate_angle(A, B, C):
    a2 = length_square(B, C)
    b2 = length_square(A, C)
    c2 = length_square(A, B)
    a = math.sqrt(a2)
    b = math.sqrt(b2)
    c = math.sqrt(c2)
    alpha = math.acos((b2 + c2 - a2) / (2 * b * c))
    betta = math.acos((a2 + c2 - b2) / (2 * a * c))
    gamma = math.acos((a2 + b2 - c2) / (2 * a * b))
    alpha = alpha * 180 / math.pi
    betta = betta * 180 / math.pi
    gamma = gamma * 180 / math.pi
    return betta

def run_diagnosis_script(request):
    if request.method == 'POST':
        form = DiagnoseForm(request.POST, request.FILES)
        if form.is_valid():
            diagnose = form.save(commit=False)
            diagnose.date_time = timezone.now()  # Set the current date and time
            diagnose.save()
        photo_before = request.FILES.get('photo_before')
        if photo_before:
            image_path = default_storage.save(photo_before.name, ContentFile(photo_before.read()))
            images = os.path.join(default_storage.location, image_path)
            model.predict(images, save=True, save_txt=True, conf=0.5, imgsz=640)
            filename = os.path.basename(images)
            file_txt = find_txt_file(filename, "/Users/sraperanosan/PycharmProjects/PRIT/FlatChecker/runs/segment/")
            file_img = imread(images)
            coordinates = {}
            with open(file_txt, "r") as file:
                for line in file:
                    line = line.strip().split()
                    class_label = int(line[0])
                    points = [(float(line[i]), float(line[i + 1])) for i in range(1, len(line), 2)]
                    coordinates.update({class_label: points})

            image_height, image_width, _ = file_img.shape
            pixel_coordinates = to_pixel_coordinates(coordinates, image_width, image_height)
            lowest_points = [max(points, key=lambda p: p[1]) for points in pixel_coordinates.values()]
            x_coords = [point[0] for point in lowest_points]
            y_coords = [point[1] for point in lowest_points]

            a = (x_coords[0], y_coords[0])
            b = (x_coords[1], y_coords[1])
            c = (x_coords[2], y_coords[2])

            angle = calculate_angle(a, b, c)
            radius = 30
            theta = np.linspace(0, 2 * np.pi, 100)
            x_circle = b[0] + radius * np.cos(theta)
            y_circle = b[1] + radius * np.sin(theta)

            if angle <= 130:
                text = "Нормальная стопа"
            elif 131 <= angle <= 140:
                text = "Первая степень плоскостопия"
            elif 141 <= angle <= 155:
                text = "Вторая степень плоскостопия"
            else:
                text = "Третья степень плоскостопия"

            # Plotting the image
            plt.imshow(file_img)
            plt.plot(x_circle, y_circle, color='green', label=f'Окружность, угол: {angle:.2f} градусов')
            plt.plot(x_coords + [x_coords[0]], y_coords + [y_coords[0]], color='blue')
            plt.scatter(x_coords, y_coords, color='red', label='Самые нижние точки')
            plt.legend()
            plt.xlabel('X')
            plt.ylabel('Y')
            plt.title(text)
            img_path = 'main/static/main/img/' + filename
            plt.savefig(img_path)
            plt.close()
            return JsonResponse({'diagnosis': text, 'photo': filename})
        else:
            return JsonResponse({'error': 'No photo provided'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

from django.shortcuts import render, redirect
from django.db import transaction, IntegrityError
from .models import UUser, PPatient, Diagnose

def save_results(request):
    if request.method == 'POST':
        user_full_name = request.POST.get('user_full_name').split()
        patient_full_name = request.POST.get('patient_full_name').split()
        date_of_birth = request.POST.get('date_of_birth')
        date_time = request.POST.get('date_time')
        note = request.POST.get('note')
        diagnose_text = request.POST.get('diagnose')
        photo_before = request.FILES.get('photo_before')
        photo_after = request.FILES.get('photo_after')

        if (user_full_name and len(user_full_name) == 3) and (patient_full_name and len(patient_full_name) == 3):
            try:
                with transaction.atomic():
                    # Create or get user
                    user, user_created = UUser.objects.get_or_create(
                        name=user_full_name[0],
                        second_name=user_full_name[1],
                        last_name=user_full_name[2]
                    )

                    # Create or get patient
                    patient, patient_created = PPatient.objects.get_or_create(
                        name=patient_full_name[0],
                        second_name=patient_full_name[1],
                        last_name=patient_full_name[2],
                        defaults={'date_of_birth': date_of_birth}
                    )

                    # Save diagnose
                    diagnose = Diagnose(
                        user=user,
                        patient=patient,
                        date_time=date_time,
                        note=note,
                        diagnose=diagnose_text,
                        photo_before=photo_before,
                        photo_after=photo_after
                    )
                    diagnose.save()

                return redirect('results')
            except IntegrityError as e:
                return render(request, 'main/main.html', {
                    'error': f"Database error occurred: {e}"
                })
        else:
            return render(request, 'main/main.html', {
                'error': 'Invalid form submission. Please check the entered data.'
            })
    else:
        return redirect('results')
