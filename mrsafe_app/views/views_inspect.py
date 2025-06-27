import base64
import re
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from django.utils.timezone import now
from django.core.files.storage import FileSystemStorage
from ..forms import HazardForm, RecommendationForm


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def parse_markdown_sections(markdown_text):
    sections = []
    raw_sections = [s.strip() for s in markdown_text.split("##") if s.strip()]

    bullet_pattern = re.compile(r"^(\s*[-*•]|\s*\d+\.)\s+")

    for section in raw_sections:
        lines = section.splitlines()
        title = lines[0].strip() if lines else "Untitled"
        body_lines = lines[1:] if len(lines) > 1 else []

        bullet_points = []
        for line in body_lines:
            if bullet_pattern.match(line.strip()):
                clean_bullet = bullet_pattern.sub("", line.strip())
                bullet_points.append(clean_bullet)

        sections.append({
            "title": title,
            "bullets": bullet_points,
        })

    return sections


@csrf_exempt
def safety_image_test(request):
    context = {}

    if not settings.OPENAI_API_KEY:
        context["error"] = "OpenAI API key is missing"
        return render(request, "mrsafe_app/inspect.html", context)

    if request.method == "POST" and request.FILES.get("photo"):
        image_file = request.FILES["photo"]
        try:
            if image_file.size > 5 * 1024 * 1024:
                raise ValueError("Image size exceeds 5MB")

            fs = FileSystemStorage(location="media/uploads", base_url="/media/uploads/")
            filename = fs.save(image_file.name, image_file)
            uploaded_url = fs.url(filename)
            context["photo_url"] = uploaded_url

            with fs.open(filename, "rb") as img:
                base64_img = base64.b64encode(img.read()).decode("utf-8")

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
                                    "url": f"data:image/{image_file.content_type.split('/')[-1]};base64,{base64_img}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.3,
            )

            analysis = response.choices[0].message.content
            clean_analysis = analysis.replace("```markdown", "").replace("```", "").strip()
            sections = parse_markdown_sections(clean_analysis)
            context["sections"] = sections

            # Prepare forms from parsed sections
            hazard_forms = []
            recommendation_forms = []

            for section in sections:
                title = section["title"].lower()
                for bullet in section["bullets"]:
                    if "severity" in bullet.lower():
                        # Try to extract severity and OSHA using patterns
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
            context["safety_score"] = calculate_safety_score(clean_analysis)

        except ValueError as ve:
            context["error"] = f"Validation Error: {str(ve)}"
        except Exception as e:
            context["error"] = f"Analysis Error: {str(e)}"
            if settings.DEBUG:
                import traceback
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
