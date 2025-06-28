import base64
import os
import re
import traceback
from dotenv import load_dotenv

from django.conf import settings
from django.shortcuts import render, redirect
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from openai import OpenAI
from django.contrib.auth import get_user_model

from ..forms import HazardForm, RecommendationForm
from ..models import SafetyObservation

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def parse_markdown_sections(markdown_text):
    sections = []
    raw_sections = [s.strip() for s in markdown_text.split("##") if s.strip()]
    bullet_pattern = re.compile(r"^(\s*[-*•]|\s*\d+\.)\s+")

    for section in raw_sections:
        lines = section.splitlines()
        title = lines[0].strip() if lines else "Untitled"
        body_lines = lines[1:] if len(lines) > 1 else []
        bullet_points = [re.sub(bullet_pattern, "", line.strip()) for line in body_lines if bullet_pattern.match(line.strip())]
        sections.append({"title": title, "bullets": bullet_points})
    return sections



@csrf_exempt
def safety_image_test(request):
    context = {}

    if not settings.OPENAI_API_KEY:
        context["error"] = "OpenAI API key is missing"
        return render(request, "mrsafe/inspect/inspect.html", context)

    if request.method == "POST" and request.FILES.get("photo"):
        image_file = request.FILES["photo"]

        try:
            if image_file.size > 5 * 1024 * 1024:
                raise ValueError("Image size exceeds 5MB")

            # Save uploaded photo to media/uploads
            fs = FileSystemStorage(location="media/uploads", base_url="/media/uploads/")
            filename = fs.save(image_file.name, image_file)
            uploaded_url = fs.url(filename)
            context["photo_url"] = uploaded_url

            with fs.open(filename, "rb") as img:
                base64_img = base64.b64encode(img.read()).decode("utf-8")

            # Debug: content-type and input size
            content_type = image_file.content_type or "image/jpeg"
            image_ext = content_type.split("/")[-1]
            print("[DEBUG] Content-Type:", content_type)
            print("[DEBUG] Base64 Length:", len(base64_img))

            prompt = """
**Safety Inspection Analysis Request**

You are a senior workplace safety expert with 20+ years of field experience. You are analyzing the uploaded workplace photo. Provide your response using the following structured format:

---

### Hazard #1
- **Title**: [Short title of hazard]
- **Severity**: Low / Medium / High / Critical
- **Description**: [Detailed description of the hazard]
- **OSHA Reference**: [If applicable]

#### Recommendation
- **Action**: [Corrective action to eliminate the hazard]
- **PPE**: [Required PPE, if any]
- **Training**: [Required training, if any]
- **Engineering Control**: [Control measure, if any]
- **Timeline**: [Suggested resolution timeline]

---

Repeat the structure for each hazard found in the image. Do not list hazards or recommendations in separate sections. Always keep each hazard and its recommendation grouped.

Format your output in clean markdown as shown above.
"""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a workplace safety AI assistant."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image_ext};base64,{base64_img}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.3,
            )

            print("[DEBUG] GPT Response Object:", response)

            if not response.choices or not response.choices[0].message.content:
                raise ValueError("GPT response missing expected content.")

            analysis = response.choices[0].message.content
            clean_analysis = analysis.replace("```markdown", "").replace("```", "").strip()
            sections = parse_markdown_sections(clean_analysis)
            context["sections"] = sections

            # Extract hazard and recommendation summary
            hazard_lines = []
            reco_lines = []
            for section in sections:
                title = section["title"].strip()
                for bullet in section.get("bullets", []):
                    if "severity" in bullet.lower():
                        hazard_lines.append(f"{title}: {bullet}")
                    elif any(x in title.lower() for x in ["recommendation", "action"]):
                        reco_lines.append(f"{title}: {bullet}")

            # Save to DB
            user = request.user if request.user.is_authenticated else get_user_model().objects.filter(is_active=True).first()
            if not user:
                context["error"] = "No valid user found to assign observation."
                return render(request, "mrsafe/inspect/inspect.html", context)

            SafetyObservation.objects.create(
                photo=image_file,
                hazard_description="\n".join(hazard_lines),
                recommendations="\n".join(reco_lines),
                created_by=user
            )

            # Forms for UI
            hazard_forms = []
            recommendation_forms = []

            for section in sections:
                title = section["title"].lower()
                for bullet in section["bullets"]:
                    if "severity" in bullet.lower():
                        severity_match = re.search(r"severity:\s*(\w+)", bullet, re.I)
                        osha_match = re.search(r"osha.*?:\s*(.+)", bullet, re.I)
                        hazard_forms.append(HazardForm(initial={
                            "title": section["title"],
                            "description": bullet,
                            "severity": severity_match.group(1) if severity_match else "Medium",
                            "oshas": osha_match.group(1) if osha_match else "",
                        }))
                    elif any(k in title for k in ["recommendation", "action"]):
                        recommendation_forms.append(RecommendationForm(initial={
                            "title": section["title"],
                            "action": bullet
                        }))

            context["hazard_forms"] = hazard_forms
            context["recommendation_forms"] = recommendation_forms
            context["message"] = "✅ Safety observation successfully saved."

        except ValueError as ve:
            context["error"] = f"Validation Error: {str(ve)}"
        except Exception as e:
            context["error"] = f"Analysis Error: {str(e)}"
            if settings.DEBUG:
                context["error_details"] = traceback.format_exc()

    context["now"] = now()
    return render(request, "mrsafe/inspect/inspect.html", context)



def calculate_safety_score(analysis):
    """Calculate safety score based on hazard severity in analysis"""
    critical = analysis.count("Severity: Critical")
    high = analysis.count("Severity: High")
    medium = analysis.count("Severity: Medium")
    low = analysis.count("Severity: Low")
    
    score = 100 - (critical * 20 + high * 10 + medium * 5 + low * 2)
    return max(30, min(100, score))


# mrsafe_app/views/views_inspect.py



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
    


from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import redirect
import os
from django.conf import settings
from ..models import SafetyObservation  # adjust import if needed

@login_required
def save_observation(request):
    if request.method == 'POST':
        photo_url = request.POST.get('photo')
        hazard_description = request.POST.get('hazard_description', '')
        recommendations = request.POST.get('recommendations', '')

        if photo_url and photo_url.startswith('/media/'):
            photo_path = photo_url.replace('/media/', '')
            full_path = os.path.join(settings.MEDIA_ROOT, photo_path)

            try:
                with open(full_path, 'rb') as f:
                    file_content = ContentFile(f.read(), name=os.path.basename(photo_path))

                SafetyObservation.objects.create(
                    photo=file_content,
                    hazard_description=hazard_description,
                    recommendations=recommendations,
                    created_by=request.user  # ✅ correct field
                )

                return redirect('mrsafe_app:inspect_success')  # ensure this route exists

            except FileNotFoundError:
                print(f"[ERROR] File not found: {full_path}")

        return redirect('mrsafe_app:inspect')  # fallback
    return redirect('mrsafe_app:inspect')


from django.shortcuts import render

def inspect_success(request):
    return render(request, "mrsafe/inspect/success.html")

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..models import SafetyObservation

@login_required
def observation_list(request):
    observations = SafetyObservation.objects.filter(created_by=request.user).order_by('-detected_at')
    return render(request, "mrsafe/inspect/observation_list.html", {
        "observations": observations
    })
###################################################################################

####################site inspection##########################################
# views/site_inspection_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ..models import SiteInspection, SafetyObservation

@login_required
def inspection_list(request):
    inspections = SiteInspection.objects.filter(inspector=request.user).order_by('-date')
    return render(request, 'mrsafe/inspection/list.html', {
        'inspections': inspections
    })
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from ..models import SiteInspection, SafetyObservation

@login_required
def inspection_detail(request, inspection_id):
    # Ensure the user is the inspector of this SiteInspection
    inspection = get_object_or_404(SiteInspection, id=inspection_id, inspector=request.user)

    # Fetch related SafetyObservations and order by detection time
    observations = SafetyObservation.objects.filter(site_inspection=inspection).order_by('-detected_at')

    # Render the page with the new template and pass the inspection and observations context
    return render(request, 'mrsafe/inspect/inspection_detail.html', {
        'inspection': inspection,
        'observations': observations,
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import SiteInspectionForm  # make sure this form is defined
from ..models import SiteInspection
from django.urls import reverse


@login_required
def inspection_create(request):
    if request.method == 'POST':
        form = SiteInspectionForm(request.POST)
        if form.is_valid():
            inspection = form.save(commit=False)
            inspection.inspector = request.user
            inspection.save()
            return redirect('mrsafe_app:inspection_detail', inspection_id=inspection.id)


    else:
        form = SiteInspectionForm()
    return render(request, 'mrsafe/inspect/create.html', {'form': form})

from django.shortcuts import render, get_object_or_404
from ..models import SafetyObservation

def observation_detail(request, pk):
    # Fetch the SafetyObservation object
    obs = get_object_or_404(SafetyObservation, pk=pk)

    # Split the hazard description and recommendations
    hazard_lines = obs.hazard_description.split("\n") if obs.hazard_description else []
    reco_lines = obs.recommendations.split("\n") if obs.recommendations else []

    # Combine hazards and recommendations in a structured format
    hazards_and_recommendations = []
    for hazard, reco in zip(hazard_lines, reco_lines):
        hazards_and_recommendations.append({
            'hazard': hazard,
            'recommendation': reco
        })

    return render(request, "mrsafe/inspect/observation_detail.html", {
        "obs": obs,
        "hazards_and_recommendations": hazards_and_recommendations,
    })

import re
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import base64
import traceback

@csrf_exempt
def site_inspection_image_test(request, inspection_id):
    context = {}
    inspection = get_object_or_404(SiteInspection, id=inspection_id)

    if not settings.OPENAI_API_KEY:
        context["error"] = "OpenAI API key is missing"
        return render(request, "mrsafe/inspect/site_inspect.html", context)

    if request.method == "POST" and request.FILES.get("photo"):
        image_file = request.FILES["photo"]

        try:
            # Save uploaded image
            fs = FileSystemStorage(location="media/uploads", base_url="/media/uploads/")
            filename = fs.save(image_file.name, image_file)
            uploaded_url = fs.url(filename)
            context["photo_url"] = uploaded_url

            # Encode for GPT
            with fs.open(filename, "rb") as img:
                base64_img = base64.b64encode(img.read()).decode("utf-8")
            content_type = image_file.content_type or "image/jpeg"
            image_ext = content_type.split("/")[-1]

            # GPT prompt
            prompt = """
            **Site Inspection Safety Analysis Request**

            You are a senior workplace safety expert with 20+ years of field experience. You are analyzing the uploaded workplace photo related to a site inspection. Provide your response using the following structured format:

            ---

            ### Hazard #1
            - **Title**: [Short title of hazard]
            - **Severity**: Low / Medium / High / Critical
            - **Description**: [Detailed description of the hazard]
            - **OSHA Reference**: [If applicable]

            #### Recommendation
            - **Action**: [Corrective action to eliminate the hazard]
            - **PPE**: [Required PPE, if any]
            - **Training**: [Required training, if any]
            - **Engineering Control**: [Control measure, if any]
            - **Timeline**: [Suggested resolution timeline]

            ---

            Repeat the structure for each hazard found in the image. Do not list hazards or recommendations in separate sections. Always keep each hazard and its recommendation grouped.

            Format your output in clean markdown as shown above.
            """

            # GPT-4o call
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a workplace safety AI assistant."},
                    {"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/{image_ext};base64,{base64_img}",
                            "detail": "high"
                        }}
                    ]}
                ],
                max_tokens=1500,
                temperature=0.3,
            )

            if not response.choices or not response.choices[0].message.content:
                raise ValueError("AI response is empty.")

            # Clean up response
            analysis = response.choices[0].message.content
            clean_analysis = analysis.replace("```markdown", "").replace("```", "").strip()

            # Extract hazard and recommendation sections
            def extract_sections(text):
                hazard_sections = []
                recommendation_sections = []
                blocks = text.split('---')
                for block in blocks:
                    block = block.strip()
                    if not block:
                        continue
                    hazard_match = re.search(r"###\s*Hazard.*?\n(.*?)(?=####|$)", block, re.DOTALL)
                    reco_match = re.search(r"####\s*Recommendation.*?\n(.*)", block, re.DOTALL)
                    if hazard_match:
                        hazard_sections.append(hazard_match.group(1).strip())
                    if reco_match:
                        recommendation_sections.append(reco_match.group(1).strip())
                return "\n\n".join(hazard_sections), "\n\n".join(recommendation_sections)

            hazard_text, recommendation_text = extract_sections(clean_analysis)

            # Pass to template
            context["hazard_description"] = hazard_text or clean_analysis
            context["recommendations"] = recommendation_text or "Review the analysis above and extract the key action items."
            context["inspection_id"] = inspection.id

            return render(request, "mrsafe/inspect/preview_observation.html", context)

        except Exception as e:
            context["error"] = f"Error during processing: {e}"
            if settings.DEBUG:
                context["traceback"] = traceback.format_exc()

    return render(request, "mrsafe/inspect/site_inspect.html", context)


# views.py
@csrf_exempt
def site_inspection_start(request, inspection_id):
    # Fetch the SiteInspection object using the provided inspection_id
    inspection = get_object_or_404(SiteInspection, id=inspection_id)

    if request.method == "POST" and request.FILES.get("photo"):
        image_file = request.FILES["photo"]

        try:
            # Validate the image size (max 5MB)
            if image_file.size > 5 * 1024 * 1024:
                raise ValueError("Image size exceeds 5MB")

            # Save the uploaded photo
            fs = FileSystemStorage(location="media/uploads", base_url="/media/uploads/")
            filename = fs.save(image_file.name, image_file)
            uploaded_url = fs.url(filename)

            # Now, we redirect to the image analysis view
            return redirect('mrsafe_app:site_inspection_image_test', inspection_id=inspection.id)

        except ValueError as ve:
            context["error"] = f"Validation Error: {str(ve)}"
        except Exception as e:
            context["error"] = f"Error during photo processing: {str(e)}"
            if settings.DEBUG:
                context["error_details"] = traceback.format_exc()

    return render(request, 'mrsafe/inspect/start_inspection.html', {'inspection': inspection})

from django.shortcuts import render

def dashboard(request):
    # Your dashboard logic here
    return render(request, "mrsafe/inspect/dashboard.html")
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import redirect, get_object_or_404, render
from django.conf import settings
import os
from urllib.parse import unquote
from ..models import SafetyObservation, SiteInspection

@login_required
def safe_site_observation(request, inspection_id):
    if request.method == 'POST':
        photo_url = request.POST.get('photo_url')
        hazard_description = request.POST.get('hazard_description', '')
        recommendations = request.POST.get('recommendations', '')
        inspection = get_object_or_404(SiteInspection, id=inspection_id)

        if photo_url and photo_url.startswith('/media/'):
            photo_path = unquote(photo_url.replace('/media/', ''))
            full_path = os.path.join(settings.MEDIA_ROOT, photo_path)

            try:
                with open(full_path, 'rb') as f:
                    file_content = ContentFile(f.read(), name=os.path.basename(photo_path))

                SafetyObservation.objects.create(
                    photo=file_content,
                    hazard_description=hazard_description,
                    recommendations=recommendations,
                    created_by=request.user,
                    site_inspection=inspection
                )

                return redirect('mrsafe_app:inspection_detail', inspection_id=inspection.id)

            except FileNotFoundError:
                return render(request, "mrsafe/inspect/preview_observation.html", {
                    "error": f"File not found: {photo_url}",
                    "inspection_id": inspection.id,
                    "hazard_description": hazard_description,
                    "recommendations": recommendations,
                })

    return redirect('mrsafe_app:inspection_detail', inspection_id=inspection_id)
