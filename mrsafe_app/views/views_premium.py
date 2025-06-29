from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.utils.timezone import now
from django.urls import reverse
import qrcode
from io import BytesIO
import base64
from ..models import (
  
    PremiumProfile, CoinActivity, 
)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import PremiumProfile,  CustomUser
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model


CustomUser = get_user_model()  # ✅ Ensure we get the correct user model


import qrcode
from PIL import Image
import base64
from io import BytesIO
from django.templatetags.static import static
from django.contrib.staticfiles import finders

def generate_premium_qr(premium_code):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(premium_code)
    qr.make(fit=True)

    # ✅ Tiffany on dark
    qr_img = qr.make_image(fill_color="#00FFE7", back_color="#0A0F2C").convert("RGBA")

    # ✅ Center logo overlay
    logo_path = finders.find("images/quizai-logo.png")
    if logo_path:
        logo = Image.open(logo_path).convert("RGBA")
        qr_width, qr_height = qr_img.size
        logo_size = int(qr_width * 0.2)
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

        # Paste at center
        pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
        qr_img.paste(logo, pos, logo)

    # Convert to base64
    buffer = BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{qr_image_base64}"


import uuid
@login_required
def premium_dashboard(request):
    if not request.user.is_premium:
        messages.warning(request, "🚫 Premium access required to view this page.")
        return redirect("mrsafe_app:premium_membership")

    # ✅ Get or create the premium profile for the logged-in trainer
    
   

    premium_profile, created = PremiumProfile.objects.get_or_create(user=request.user)
    if not premium_profile.premium_code:
        premium_profile.premium_code = str(uuid.uuid4()).split('-')[0].upper()  # e.g., '9A7D5F'
        premium_profile.save()

    premium_code = premium_profile.premium_code
    premium_qr_url = generate_premium_qr(premium_code)


    # ✅ Trainer is the logged-in user
    trainer = request.user

    # ✅ Fetch the first group (or adjust to get specific groups if needed)
    group = TraineeGroup.objects.filter(trainer=trainer).first()  # Use .first() to avoid errors if no group exists

    # ✅ Fetch linked trainees (from LinkedUser model)

    linked_trainees = CustomUser.objects.filter(linked_user__premium_users=trainer.premiumprofile).distinct()
    # ✅ Exclude trainees already in the group (only if a group exists)

    available_trainees = CustomUser.objects.filter(linked_user__premium_users=trainer.premiumprofile )


    # ✅ Fetch quizzes created by the trainer
    trainer_quizzes = Quiz.objects.filter(created_by=trainer)
    

    # ✅ Fetch quiz results for trainees linked to the trainer
    if group:
        trainee_results = QuizResult.objects.filter(user__in=group.trainees.all())
    else:
        trainee_results = QuizResult.objects.filter(user__in=linked_trainees)

    # ✅ Fetch groups where the trainer is assigned
    groups = TraineeGroup.objects.filter(trainer=trainer)

    # ✅ Fetch active and completed competitions
    active_competitions = Competition.objects.filter(trainer=trainer, winner__isnull=True)
    completed_competitions = Competition.objects.filter(trainer=trainer, winner__isnull=False)

    # ✅ Return data to template
    return render(request, "mrsafe_app/premium/premium_dashboard.html", {
        "premium_qr_url": premium_qr_url,
        "premium_code": premium_code,
        "trainer_quizzes": trainer_quizzes,
        "available_trainees": available_trainees,  # ✅ Shows trainees correctly now
        "trainee_results": trainee_results,
        "groups": groups,
        "active_competitions": active_competitions,
        "completed_competitions": completed_competitions,
          # To loop in table if needed
    })



    
#upgrade_membership______________________________________________________________________________
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def upgrade_membership(request):
    """Upgrade the user's membership to premium."""
    user = request.user
    if not user.is_premium:
        user.is_premium = True
        user.save()
        messages.success(request, "Congratulations! You are now a premium member!")
    return redirect("mrsafe_app:premium_dashboard")  # Redirect back to the dashboard




#########################################################################################

    
    ##################################################################################
# mrsafe_app/views/premium.py
from datetime import timedelta
from django.utils.timezone import now
from django.shortcuts import render, redirect
from django.urls import reverse
from ..models import PremiumProfile, PremiumPlan, UserProfile


def premium_membership(request):
    """
    Premium membership dashboard.
    Redirects unauthenticated visitors to the login page.
    """
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")

    # ── from here on we are guaranteed a user ──────────────────
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    premium_profile, _ = PremiumProfile.objects.get_or_create(user=user)

    # status update
    if premium_profile.end_date and now() > premium_profile.end_date:
        premium_profile.is_active = False
        profile.is_premium = False
    else:
        premium_profile.is_active = True
        profile.is_premium = True
        profile.premium_end_date = premium_profile.end_date

    premium_profile.save(update_fields=["is_active"])
    profile.save(update_fields=["is_premium", "premium_end_date"])

    context = {
        "profile": profile,
        "plans": PremiumPlan.objects.filter(is_active=True).order_by("duration_days"),
        "is_premium": profile.is_premium,
        "premium_expires": premium_profile.end_date,
        "trial_used": premium_profile.trial_used,
        "is_logged_in": True,  # still used in template logic
    }
    return render(request, "mrsafe_app/premium/premium_membership.html", context)

@login_required
def activate_trial(request):
    user = request.user
    premium_profile, _ = PremiumProfile.objects.get_or_create(user=user)

    if premium_profile.trial_used:
        messages.warning(request, "⛔ You have already used your trial.")
        return redirect('mrsafe_app:premium_membership')

    if premium_profile.end_date and premium_profile.end_date > now():
        messages.warning(request, "⛔ You already have an active premium membership.")
        return redirect('mrsafe_app:premium_membership')

    premium_profile.end_date = now() + timedelta(days=7)
    premium_profile.trial_used = True
    premium_profile.is_active = True
    premium_profile.save()

    messages.success(request, "✅ Trial activated for 7 days!")
    return redirect('mrsafe_app:premium_membership')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from mrsafe_app.models import PremiumPlan, PremiumProfile
from django.utils import timezone

@login_required
def premium_membership_view(request):
    user = request.user
    
    # Get or create premium profile using the correct related_name
    profile = user.premium_profile  # Using the defined related_name
    
    # Check trial eligibility (no start date and trial not used)
    trial_eligible = (not profile.start_date and 
                     not profile.trial_used and 
                     not profile.is_active)
    
    # Activate trial if eligible
    if trial_eligible:
        try:
            profile.activate_premium(
                plan_name="trial", 
                duration_days=3, 
                coin_bonus=50
            )
            messages.success(request, "🎉 Your 3-day free trial has been activated!")
        except Exception as e:
            messages.error(request, f"Could not activate trial: {str(e)}")
    
    # Get active premium plans (excluding trial if user already used it)
    plans = PremiumPlan.objects.filter(is_active=True)
    if profile.trial_used:
        plans = plans.exclude(name="trial")
    
    # Calculate days remaining if premium is active
    days_remaining = 0
    if profile.is_active and profile.end_date:
        days_remaining = (profile.end_date - timezone.now()).days
    
    return render(request, "mrsafe/premium/premium_membership.html", {
        "is_premium": profile.is_premium_active(),  # Use the method for accurate status
        "premium_expires": profile.end_date,
        "days_remaining": max(0, days_remaining),  # Ensure no negative values
        "plans": plans,
        "current_plan": profile.plan,
        "trial_used": profile.trial_used,
    })
    
    
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from ..models import PremiumPlan, PremiumProfile

@login_required
def subscribe_premium(request, plan):
    user = request.user
    premium_profile, _ = PremiumProfile.objects.get_or_create(user=user)

    # Restrict stacking beyond 365 days
    if premium_profile.end_date and (premium_profile.end_date - now()).days >= 365:
        messages.warning(request, "⛔ Your premium already covers 365+ days.")
        return redirect('mrsafe_app:premium_membership')

    premium_plan = get_object_or_404(PremiumPlan, name=plan, is_active=True)

    # ✅ Save plan to session for final checkout confirmation
    request.session['selected_premium_plan_id'] = premium_plan.id
    return redirect('mrsafe_app:premium_checkout')



@login_required
def premium_checkout(request):
    plan_id = request.session.get("selected_premium_plan_id")
    if not plan_id:
        return redirect("mrsafe_app:premium_membership")

    premium_plan = get_object_or_404(PremiumPlan, id=plan_id)

    profile = PremiumProfile.objects.filter(user=request.user).first()
    already_max_premium = False

    if profile and profile.end_date:
        remaining_days = (profile.end_date.date() - now().date()).days
        already_max_premium = remaining_days >= 400

    return render(request, "mrsafe_app/premium/premium_checkout.html", {
        "plan": premium_plan,
        "already_max_premium": already_max_premium,
    })
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now
from datetime import timedelta
import logging

from ..models import PremiumProfile, PremiumPlan
@login_required
def complete_premium_checkout(request):
    user = request.user
    now_time = now()

    # Get or create the premium profile
    profile, _ = PremiumProfile.objects.get_or_create(user=user)
    plan_id = request.session.get("selected_premium_plan_id")
    plan = get_object_or_404(PremiumPlan, id=plan_id, is_active=True)

    # Trial logic
    if plan.name == 'trial':
        if profile.trial_used or (profile.plan and profile.plan.name != 'trial'):
            messages.warning(request, "⛔ Trial already used or not available after a paid plan.")
            return redirect('mrsafe_app:premium_membership')

        profile.end_date = now_time + timedelta(days=plan.duration_days)
        profile.trial_used = True
        profile.is_active = True
        profile.plan = plan
        profile.save()

        messages.success(request, "Trial activated successfully!")
        return redirect('mrsafe_app:premium_membership')

    # Paid plan logic — stack from current expiry
    base_date = profile.end_date if profile.end_date and profile.end_date > now_time else now_time
    new_expiry = base_date + timedelta(days=plan.duration_days)

    profile.end_date = new_expiry
    profile.plan = plan
    profile.is_active = True
    profile.trial_used = True  # block future trial
    profile.save()

    messages.success(request, f"Premium upgraded to {plan.name.title()} until {new_expiry.strftime('%Y-%m-%d')}")
    return redirect('mrsafe_app:premium_membership')


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.timezone import now, timedelta
from django.db.models import F
from django.contrib.auth.decorators import login_required



@csrf_exempt
@login_required
def google_pay_callback(request):
    if request.method == "POST":
        user = request.user
        plan_name = request.POST.get("plan")  # e.g. 'weekly', 'monthly', 'annual'

        plan_obj = PremiumPlan.objects.filter(name=plan_name, is_active=True).first()
        if not plan_obj:
            return JsonResponse({"error": "Invalid or inactive plan."}, status=400)

        # Update or create premium profile
        profile, _ = PremiumProfile.objects.get_or_create(user=user)
        profile.start_date = now()
        profile.end_date = now() + timedelta(days=plan_obj.duration_days)
        profile.is_active = True
        profile.plan = plan_name
        profile.auto_renewal = True
        profile.save()

        # Add coins to user balance
        balance, _ = UserCoinBalance.objects.get_or_create(user=user)
        balance.balance = F('balance') + plan_obj.coin_bonus
        balance.save()

        # Create a notification
        Notification.objects.create(
            user=user,
            message=f"🎉 Your {plan_name} premium membership is now active! You received {plan_obj.coin_bonus} bonus coins."
        )

        return JsonResponse({"status": "success", "message": "Membership activated."})

    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def cancel_premium(request):
    profile = PremiumProfile.objects.get(user=request.user)
    profile.auto_renewal = False
    profile.save()
    messages.success(request, "✅ Auto-renewal has been disabled. Your membership will expire on its end date.")
    return redirect("mrsafe_app:profile")

def check_auto_renewals():
    for profile in PremiumProfile.objects.filter(is_active=True, auto_renewal=True):
        if profile.end_date and profile.end_date <= timezone.now():
            # Assume payment logic handled separately
            try:
                activate_premium(profile.user, profile.plan)
                send_notification(profile.user, "✅ Your premium membership has been renewed.")
            except:
                profile.is_active = False
                profile.save()
                send_notification(profile.user, "⚠️ Premium renewal failed. Your membership expired.")



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from ..models import PremiumPlan
from ..forms import PremiumPlanForm
@staff_member_required
def add_premium_plan(request):
    if request.method == "POST":
        form = PremiumPlanForm(request.POST)
        if form.is_valid():
            try:
                plan = form.save(commit=False)
                print(f"Saving plan with data: {form.cleaned_data}")  # Debug print
                plan.save()
                messages.success(request, "Plan created successfully!")
                return redirect('mrsafe_app:premium_membership')
            except Exception as e:
                print(f"Error saving plan: {str(e)}")  # Debug print
                messages.error(request, f"Error saving plan: {str(e)}")
        else:
            print(f"Form errors: {form.errors}")  # Debug print
            messages.error(request, "Please correct the errors below")
    else:
        form = PremiumPlanForm()
    
    return render(request, 'mrsafe/admin/add_premium_plan.html', {
        'form': form,
        'debug_data': form.errors if request.method == "POST" else None
    })