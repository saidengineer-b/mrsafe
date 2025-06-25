from django.shortcuts import render
from django.core.files.storage import FileSystemStorage

def safety_image_test(request):
    uploaded_image_url = None

    if request.method == "POST" and request.FILES.get("safety_image"):
        image_file = request.FILES["safety_image"]
        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        uploaded_image_url = fs.url(filename)

    return render(request, "safety_image_test.html", {
        "uploaded_image_url": uploaded_image_url,
    })
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage

def inspect(request):
    uploaded_image_url = None

    if request.method == "POST" and request.FILES.get("safety_image"):
        image_file = request.FILES["safety_image"]
        fs = FileSystemStorage(location="media/uploads", base_url="/media/uploads/")
        filename = fs.save(image_file.name, image_file)
        uploaded_image_url = fs.url(filename)

    return render(request, "mrsafe/inspect/inspect.html", {
        "uploaded_image_url": uploaded_image_url,
    })

