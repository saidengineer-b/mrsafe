from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import activate, get_language
from django.views.decorators.csrf import csrf_exempt
from ..models import PremiumPlan , Category

from django.urls import reverse

from ..forms import (
     CustomUserCreationForm, EditProfileForm,
     StoreItemForm, CustomPasswordResetForm, EmailLoginForm, EditUserForm, 
)
from ..models import (
     StoreItem, StoreItem, Cart,
    CartItem,  CustomUser, PremiumProfile, 
    CoinActivity, CoinTransaction, AdActivity, TermsAndConditions,
    
)


from openai import OpenAI
import openai
import json
import logging
import braintree

# ✅ Check if the user is an admin
def is_admin(user):
    return user.is_staff
def is_arabic():
    """Detect if the current language is Arabic for RTL layout."""
    return get_language() == 'ar'

from django.db.models import Avg, Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import render




from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..models import SiteInspection, UserProfile

@login_required
def profile(request):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    

    # ✅ Get site inspections created by the user
    inspections = SiteInspection.objects.filter(inspector=request.user).order_by('-date')
    total_inspections = inspections.count()
    completed_inspections = inspections.filter(completed=True).count()

    # ✅ Get coin balance if used
    user_coins = getattr(user_profile, 'coin_balance', None)
    coin_balance = user_coins.balance if user_coins else 0

    context = {
        "user_profile": user_profile,
        "inspections": inspections,
        "total_inspections": total_inspections,
        "completed_inspections": completed_inspections,
        "coin_balance": coin_balance,
    }

    return render(request, "mrsafe/profile.html", context)


# ✅ User Registration View
# views.py (User Registration)

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from ..forms import CustomUserCreationForm
from ..models import CoinActivity, UserCoinBalance

def register(request):
    user_registered = False

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save the new user
            user = form.save()
            login(request, user)

            # Fetch the "register" coin activity and update the coin balance
            try:
                register_activity = CoinActivity.objects.get(name="register", is_active=True)

                # Get or create user's coin balance
                user_balance, created = UserCoinBalance.objects.get_or_create(user=user)
                user_balance.update_balance(register_activity.coin_amount, "earn", register_activity)
                user_balance.save()
                user_registered = True

            except CoinActivity.DoesNotExist:
                print("❌ The 'register' coin activity is not found or is inactive.")

            # Redirect or show confirmation
            return render(request, 'mrsafe/register.html', {
                'form': form,
                'user_registered': user_registered
            })
    else:
        form = CustomUserCreationForm()

    return render(request, 'mrsafe/register.html', {
        'form': form,
        'user_registered': user_registered
    })


#################################

from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum


@login_required
def my_stats(request):
    user = request.user

    # ✅ Quiz performance
    quiz_results = QuizResult.objects.filter(user=user)
    completed_quizzes = quiz_results.count()
    passed_tests = quiz_results.filter(passed=True).count()
    average_score = quiz_results.aggregate(total=Sum('score'))['total'] / completed_quizzes if completed_quizzes else 0

    # ✅ Coins and Points
    user_coins = UserCoinBalance.objects.filter(user=user).first()
    coin_balance = user_coins.balance if user_coins else 0
    total_points = UserPointBalance.objects.get_or_create(user=user)[0].total_points

    # ✅ Leaderboard rank
    leaderboard = (
        QuizResult.objects.values('user__username')
        .annotate(total_score=Sum('score'))
        .order_by('-total_score')
    )
    user_ranking = next((i for i, entry in enumerate(leaderboard, 1) if entry['user__username'] == user.username), "N/A")

    # ✅ Completed sessions (all lessons must have progress with non-empty completed_steps)
    completed_sessions = 0
    all_sessions = MasterItSession.objects.all()

    for session in all_sessions:
        lessons = session.lessons.all()
        all_completed = True
        for lesson in lessons:
            try:
                progress = LessonProgress.objects.get(user=user, lesson=lesson)
                if not progress.completed_steps:  # empty list = not completed
                    all_completed = False
                    break
            except LessonProgress.DoesNotExist:
                all_completed = False
                break
        if all_completed:
            completed_sessions += 1

    return render(request, 'mrsafe_app/my_stats.html', {
        'completed_quizzes': completed_quizzes,
        'passed_tests': passed_tests,
        'average_score': round(average_score, 1),
        'coin_balance': coin_balance,
        'total_points': total_points,
        'user_ranking': user_ranking,
        'completed_sessions': completed_sessions,
    })


# ✅ Edit Profile View
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('mrsafe_app:profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'mrsafe/edit_profile.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = EmailLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('mrsafe_app:home')  # Redirect to home after login
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = EmailLoginForm()

    return render(request, 'mrsafe_app/login.html', {'form': form})


from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def logout_view(request):
    logout(request)
    messages.success(request, "👋 You have been successfully logged out.")
    return redirect('mrsafe_app:login')  # 🔁 change to your login view name


# reset passward  code details---------------------------------------------------------------#

@login_required(login_url='mrsafe_app:login')  # ✅ no app namespace





@login_required
def home(request):
    # ✅ Check premium access (if using is_premium directly)
    if not request.user.is_premium:
        messages.warning(request, "This feature is for premium users only.")
        return redirect('mrsafe_app:store')

    # ✅ Placeholder: Load any premium dashboard data you want
    return render(request, 'mrsafe_app/home.html', {
        "user": request.user,
        # Add dashboard stats if needed
    })


class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')  # Redirect after successful form submission


from django.contrib import messages

def password_reset_done(request):
    messages.success(request, "We've sent you an email with instructions to reset your password.")
    return render(request, 'registration/password_reset_done.html')

#store ITEM______________________________________________________________________________
from django.shortcuts import render
from ..models import StoreItem

def store_home(request):
    items = StoreItem.objects.all()  # Fetch all store items
    return render(request, 'store/store_home.html', {'items': items})


# ✅ Add Item View
def add_item(request):
    if request.method == 'POST':
        form = StoreItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Item added successfully!")
            return redirect('mrsafe_app:store')  # Redirect to the store page after adding
        else:
            messages.error(request, "⚠️ Error adding item. Please check the form.")
    else:
        form = StoreItemForm()
    return render(request, 'store/add_item.html', {'form': form})

# ✅ Edit Item View
def edit_item(request, item_id):
    item = get_object_or_404(StoreItem, id=item_id)
    if request.method == 'POST':
        form = StoreItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Item updated successfully!")
            return redirect('mrsafe_app:store')
        else:
            messages.error(request, "⚠️ Error updating item. Please check the form.")
    else:
        form = StoreItemForm(instance=item)
    return render(request, 'store/edit_item.html', {'form': form, 'item': item})

# ✅ Delete Item View (Optional)
def delete_item(request, item_id):
    item = get_object_or_404(StoreItem, id=item_id)
    if request.method == 'POST':
        item.delete()
        messages.success(request, "🗑️ Item deleted successfully!")
        return redirect('mrsafe_app:store')
    return render(request, 'store/delete_item_confirm.html', {'item': item})

#___________________________________________________________________________________________

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from ..models import (
    CustomUser, StoreItem, CoinActivity, CoinTransaction,
    AdActivity, PremiumPlan
)


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    ✅ Mr. Safe Admin Dashboard: View statistics, manage users, courses, store, and premium plans.
    """
    total_users = CustomUser.objects.count()
    
    total_items = StoreItem.objects.count()

    premium_plans = PremiumPlan.objects.all()
    users = CustomUser.objects.all().order_by('-date_joined')[:10]
    
    store_items = StoreItem.objects.all().order_by('-id')[:10]

    coin_activities = CoinActivity.objects.all()
    transactions = CoinTransaction.objects.all().order_by('-timestamp')
    ad_activities = AdActivity.objects.all()
    

    # Normalize activity types
    for activity in coin_activities:
        activity.activity_type = activity.activity_type.strip().lower()

    context = {
        "total_users": total_users,
        
        "total_items": total_items,
        "users": users,
        
        "store_items": store_items,
        "coin_activities": coin_activities,
        "transactions": transactions,
        "ad_activities": ad_activities,
        "premium_plans": premium_plans,  }     
    
    return render(request, "mrsafe/admin/admin_dashboard.html", context)


@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    """
    ✅ Admin can edit user details, upgrade membership, update profile photo, and modify user coin balance.
    """
    selected_user = get_object_or_404(CustomUser, id=user_id)
    user_balance, created = UserCoinBalance.objects.get_or_create(user=selected_user)  # ✅ Ensure balance record exists

    if request.method == "POST":
        form = EditUserForm(request.POST, request.FILES, instance=selected_user, user=selected_user)

        if form.is_valid():
            selected_user = form.save(commit=False)

            # ✅ Handle Profile Photo Manually
            if "profile_photo" in request.FILES:
                selected_user.profile_photo = request.FILES["profile_photo"]

            # ✅ Fetch coin balance correctly
            coin_balance = form.cleaned_data.get("coin_balance")
            if coin_balance is not None:
                user_balance.balance = coin_balance
                user_balance.save()

            selected_user.save()
            messages.success(request, "✅ User updated successfully!")
            return redirect("mrsafe_app:admin_dashboard")
    else:
        form = EditUserForm(instance=selected_user, user=selected_user)

    return render(request, "mrsafe_app/admin/edit_user.html", {"form": form, "selected_user": selected_user, "user_balance": user_balance})


####################################################################################



################################################################################

@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    """
    ✅ Admin can delete users from the system.
    """
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.success(request, "🚨 User deleted successfully!")
    return redirect("mrsafe_app:admin_dashboard")

# ✅ Course Management
@login_required
@user_passes_test(is_admin)
def create_course(request):
    """
    ✅ Admin can add a new course.
    """
    if request.method == "POST":
        title = request.POST.get("title")
        Course.objects.create(title=title)
        messages.success(request, "✅ Course added successfully!")
        return redirect("admin_dashboard")

    return render(request, "mrsafe_app/course_form.html")

@login_required
@user_passes_test(is_admin)
def edit_course(request, course_id):
    """
    ✅ Admin can edit course details.
    """
    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        course.title = request.POST.get("title")
        course.save()
        messages.success(request, "✅ Course updated successfully!")
        return redirect("admin_dashboard")

    return render(request, "mrsafe_app/course_edit.html", {"course": course})

@login_required
@user_passes_test(is_admin)
def delete_course(request, course_id):
    """
    ✅ Admin can delete a course.
    """
    course = get_object_or_404(Course, id=course_id)
    course.delete()
    messages.success(request, "🚨 Course deleted successfully!")
    return redirect("admin_dashboard")

# ✅ Store Management
@login_required
@user_passes_test(is_admin)
def add_store_item(request):
    """
    ✅ Admin can add a store item.
    """
    if request.method == "POST":
        title = request.POST.get("title")
        price = request.POST.get("price")
        StoreItem.objects.create(title=title, price=price)
        messages.success(request, "✅ Store item added successfully!")
        return redirect("admin_dashboard")

    return render(request, "mrsafe_app/store_form.html")

@login_required
@user_passes_test(is_admin)
def edit_store_item(request, item_id):
    """
    ✅ Admin can edit store items.
    """
    item = get_object_or_404(StoreItem, id=item_id)

    if request.method == "POST":
        item.title = request.POST.get("title")
        item.price = request.POST.get("price")
        item.save()
        messages.success(request, "✅ Store item updated successfully!")
        return redirect("admin_dashboard")

    return render(request, "mrsafe_app/store_edit.html", {"item": item})

@login_required
@user_passes_test(is_admin)
def delete_store_item(request, item_id):
    """
    ✅ Admin can delete a store item.
    """
    item = get_object_or_404(StoreItem, id=item_id)
    item.delete()
    messages.success(request, "🚨 Store item deleted successfully!")
    return redirect("admin_dashboard")
#________________________________________________________________________

def add_to_cart(request, item_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to add items to the cart.")
        return redirect('login')

    item = get_object_or_404(StoreItem, id=item_id)

    # Add item to user's cart (Assuming Cart model exists)
    cart_item, created = Cart.objects.get_or_create(user=request.user, item=item)

    if created:
        messages.success(request, f"{item.name} added to cart!")
    else:
        messages.info(request, f"{item.name} is already in your cart.")

    return redirect('mrsafe_app:store')
#__________________________________________________________________________________________________

#_______________________________________________________________________________________

@login_required
def enter_premium_code(request):
    """Users enter a premium user's code to link themselves."""
    if request.method == "POST":
        code = request.POST.get("premium_code")
        try:
            premium_user = PremiumProfile.objects.get(premium_code=code)
            linked_user, created = LinkedUser.objects.get_or_create(user=request.user)
            linked_user.premium_user = premium_user
            linked_user.save()
            messages.success(request, "✅ Successfully linked to the premium user!")
        except PremiumProfile.DoesNotExist:
            messages.error(request, "🚫 Invalid premium code! Please check with your premium user.")

    return render(request, "mrsafe_app/enter_premium_code.html")


def remove_linked_user(request, trainee_id):  # ✅ CORRECT
    linked_user = get_object_or_404(LinkedUser, user_id=trainee_id)
    trainer_profile = request.user.premium_profile

    # ✅ Remove the trainer from the linked user's premium_users field
    if trainer_profile in linked_user.premium_users.all():
        linked_user.premium_users.remove(trainer_profile)  # ✅ Just remove the trainer
        messages.success(request, "Trainee removed from your linked users.")
    else:
        messages.error(request, "You don't have permission to remove this user.")

    return redirect("premium_dashboard")  # ✅ Redirect to dashboard

#_______________________________________________________________________________________

#____________________________________________________________________________

@login_required
def join_trainer(request):
    """
    ✅ Allows a trainee to enter a Premium Code and link to multiple trainers.
    """
    if request.method == "POST":
        premium_code = request.POST.get("premium_code")

        try:
            # ✅ Find the trainer with the matching premium code
            trainer_profile = PremiumProfile.objects.get(premium_code=premium_code)

            # ✅ Get or create a LinkedUser entry for the trainee
            linked_user, created = LinkedUser.objects.get_or_create(user=request.user)

            # ✅ Add the trainer to the trainee’s linked trainers
            linked_user.premium_users.add(trainer_profile)

            messages.success(request, f"✅ You are now linked to {trainer_profile.user.username} as a trainee!")

        except PremiumProfile.DoesNotExist:
            messages.error(request, "❌ Invalid Premium Code! Please try again.")

    return redirect('mrsafe_app:profile')  # ✅ Redirect back to profile page

    return redirect("manage_groups")

@login_required
def manage_groups(request):
    """
    ✅ Displays all groups created by the trainer.
    ✅ Allows adding or removing trainees from groups.
    """
    trainer = request.user
    groups = TraineeGroup.objects.filter(trainer=trainer)
    trainees = CustomUser.objects.filter(linked_user__premium_users=trainer.premium_profile)

    return render(request, "mrsafe_app/manage_groups.html", {"groups": groups, "trainees": trainees})

@login_required
def update_group(request, group_id):
    """
    ✅ Allows trainers to add or remove trainees from a group.
    """
    group = get_object_or_404(TraineeGroup, id=group_id, trainer=request.user)
    if request.method == "POST":
        selected_trainees = request.POST.getlist("trainee_ids")
        group.trainees.set(CustomUser.objects.filter(id__in=selected_trainees))
        messages.success(request, f"Group '{group.name}' updated successfully!")

    return redirect("manage_groups")


@login_required
def delete_group(request, group_id):
    """
    ✅ Safely delete a group WITHOUT deleting trainees.
    """
    group = get_object_or_404(TraineeGroup, id=group_id, trainer=request.user)

    # ✅ Remove all references to this group from trainees
    TraineeGroupMembership.objects.filter(group=group).delete()

    # ✅ Now delete the group safely
    group.delete()

    messages.success(request, f"Group '{group.name}' has been successfully deleted!")
    return redirect("premium_dashboard")  # Redirect back to dashboard

#_______________________________________________________________________________________

@login_required
def create_group(request):
    """
    ✅ Allows trainers to create trainee groups.
    ✅ Trainers can select trainees when creating a group.
    ✅ Prevents duplicate group names for the same trainer.
    """
    trainer = request.user

    if request.method == "POST":
        group_name = request.POST.get("group_name")
        selected_trainees = request.POST.getlist("trainee_ids")  # ✅ Get selected trainees

        # ✅ Prevent duplicate group names
        if TraineeGroup.objects.filter(name=group_name, trainer=trainer).exists():
            messages.error(request, "A group with this name already exists.")
            return redirect("mrsafe_app:premium_dashboard")

        # ✅ Create the group
        new_group = TraineeGroup.objects.create(name=group_name, trainer=trainer)

        # ✅ Add trainees to the group
        trainees = CustomUser.objects.filter(id__in=selected_trainees)
        new_group.trainees.set(trainees)

        messages.success(request, f"Group '{group_name}' created successfully with {trainees.count()} members!")
        return redirect("mrsafe_app:premium_dashboard")

    trainees = CustomUser.objects.filter(linked_user__premium_users=trainer.premium_profile)  # ✅ Get trainer’s trainees
    return render(request, "mrsafe_app/create_group.html", {"trainees": trainees})
#____________________________________________________________________________________________
@login_required
def add_members_to_group(request, group_id):
    """
    ✅ Allows trainers to add trainees to a group before assigning quizzes.
    """
    trainer = request.user
    group = get_object_or_404(TraineeGroup, id=group_id, trainer=trainer)

    # ✅ Fetch trainees that belong to the trainer but are not yet in the group
    available_trainees = CustomUser.objects.filter(linked_user__premium_users=trainer.premium_profile).exclude(id__in=group.trainees.all())

    if request.method == "POST":
        selected_trainees = request.POST.getlist("trainee_ids")  # ✅ Get selected trainees
        trainees_to_add = CustomUser.objects.filter(id__in=selected_trainees)
        group.trainees.add(*trainees_to_add)

        messages.success(request, f"Successfully added {trainees_to_add.count()} members to {group.name}!")
        return redirect("premium_dashboard")

    return render(request, "mrsafe_app/add_members_to_group.html", {"group": group, "trainees": available_trainees})
#_____________________________________________________________________________________________

@login_required
def assign_quiz_group(request, group_id):
    """
    ✅ Trainers can assign quizzes to all members of a group.
    """
    trainer = request.user
    group = get_object_or_404(TraineeGroup, id=group_id, trainer=trainer)

    # ✅ Fetch trainees using the correct membership model
    trainees = CustomUser.objects.filter(group_memberships__group=group)

    # ✅ Fetch quizzes created by trainer
    available_quizzes = Quiz.objects.filter(created_by=trainer)

    if request.method == "POST":
        selected_quizzes = request.POST.getlist("quiz_ids")  # ✅ Get selected quizzes

        if not selected_quizzes:
            messages.error(request, "Please select at least one quiz.")
            return redirect("assign_quiz_group", group_id=group_id)

        for quiz_id in selected_quizzes:
            quiz = get_object_or_404(Quiz, id=quiz_id, created_by=trainer)

            # ✅ Assign quiz to each trainee in the group
            for trainee in trainees:
                if quiz in trainee.assigned_quizzes.all():
                    continue  # ✅ Skip if already assigned

                trainee.assigned_quizzes.add(quiz)  # ✅ Assign quiz to trainee
                quiz.assigned_users.add(trainee)  # ✅ Ensure quiz tracks assigned users

        messages.success(request, f"Successfully assigned quizzes to all members of Group '{group.name}'!")
        return redirect("premium_dashboard")  # Redirect back to dashboard

    return render(request, "mrsafe_app/assign_quiz.html", {
        "group": group,
        "quizzes": available_quizzes,
    })

#____________________________________________________________________________________
#__________________________________________________________________



#_______________________________________________________________________________________

@login_required
def create_competition(request):
    """
    ✅ Trainer creates a new competition between two groups.
    ✅ Automatically assigns the quiz to all trainees in both groups.
    """
    trainer = request.user
    groups = TraineeGroup.objects.filter(trainer=trainer)
    quizzes = Quiz.objects.filter(created_by=trainer)

    if request.method == "POST":
        group_one_id = request.POST.get("group_one")
        group_two_id = request.POST.get("group_two")
        quiz_id = request.POST.get("quiz")

        if group_one_id == group_two_id:
            messages.error(request, "You cannot select the same group for both sides.")
            return redirect("create_competition")

        group_one = get_object_or_404(TraineeGroup, id=group_one_id, trainer=trainer)
        group_two = get_object_or_404(TraineeGroup, id=group_two_id, trainer=trainer)
        quiz = get_object_or_404(Quiz, id=quiz_id, created_by=trainer)

        # ✅ Create the competition
        competition = Competition.objects.create(
            trainer=trainer,
            group_one=group_one,
            group_two=group_two,
            quiz=quiz,
            active_group=group_one  # ✅ Group One starts first
        )

        # ✅ Assign the quiz to all trainees in both groups
        for trainee in group_one.trainees.all():
            trainee.assigned_quizzes.add(quiz)

        for trainee in group_two.trainees.all():
            trainee.assigned_quizzes.add(quiz)

        messages.success(request, f"Competition created: {group_one.name} vs {group_two.name}!")
        return redirect("mrsafe_app:competitions_list")

    return render(request, "mrsafe_app/premium/create_competition.html", {"groups": groups, "quizzes": quizzes})

@login_required
def competitions_list(request):
    """
    ✅ Display ongoing and completed competitions.
    """
    trainer = request.user
    competitions = Competition.objects.filter(trainer=trainer)

    return render(request, "mrsafe_app/premium/competitions_list.html", {"competitions": competitions})

@login_required
def calculate_winner(request, competition_id):
    """
    ✅ Determine the winning group based on the Competition model's own scores.
    """
    competition = get_object_or_404(Competition, id=competition_id, trainer=request.user)

    # Compare the scoreboard fields (each capped at 10 in competition_live logic)
    if competition.group_one_score > competition.group_two_score:
        competition.winner = competition.group_one
    elif competition.group_two_score > competition.group_one_score:
        competition.winner = competition.group_two
    else:
        competition.winner = None  # Draw

    competition.save()

    # Show a success message, referencing the winner or a draw
    winner_name = competition.winner.name if competition.winner else 'Draw'
    messages.success(request, f"Competition result updated: {winner_name}")
    return redirect("mrsafe_app:competitions_list")

#__________________________________________________________________________

@login_required
def start_competition(request, competition_id):
    """
    ✅ Starts the competition & assigns the quiz to all members of both groups.
    """
    competition = get_object_or_404(Competition, id=competition_id, trainer=request.user)

    # ✅ Assign the quiz to all trainees in both groups
    group_one_trainees = competition.group_one.trainees.all()
    group_two_trainees = competition.group_two.trainees.all()
    all_trainees = group_one_trainees | group_two_trainees  # Combine both groups

    for trainee in all_trainees:
        trainee.assigned_quizzes.add(competition.quiz)

    # ✅ Set active group and start index
    competition.current_question_index = 0
    competition.active_group = competition.group_one
    competition.save()

    messages.success(request, f"Competition Started! {competition.group_one.name} goes first.")
    return redirect("mrsafe_app:competition_live", competition_id=competition.id)

#_______________________________________________________________________________________________

@login_required
def competition_live(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id, trainer=request.user)
    questions = competition.quiz.questions.all()
    total_questions = questions.count()

    # If all questions are answered, redirect to results
    if competition.current_question_index >= total_questions:
        return redirect("mrsafe_app:competition_results", competition_id=competition.id)

    current_question = questions[competition.current_question_index]
    active_group = competition.active_group

    if request.method == "POST":
        selected_answer = request.POST.get("selected_answer")
        correct_choice = current_question.choices.filter(is_correct=True).first()

        if not correct_choice:
            messages.error(request, "Error: No correct answer found for this question.")
            return redirect("cmrsafe_app:ompetition_live", competition_id=competition.id)

        is_correct = (selected_answer == correct_choice.text)

        # Update each trainee's QuizResult (if you still want that logic)
        for trainee in active_group.trainees.all():
            quiz_result, created = QuizResult.objects.get_or_create(
                user=trainee, quiz=competition.quiz, defaults={"score": 0}
            )
            if is_correct:
                quiz_result.score += 1
                quiz_result.save()

        # ✅ Also update the competition’s group scores
        if is_correct:
            if active_group == competition.group_one:
                competition.group_one_score += 2
                if competition.group_one_score > 10:
                    competition.group_one_score = 10
            else:
                competition.group_two_score += 2
                if competition.group_two_score > 10:
                    competition.group_two_score = 10

        # Switch Active Group (Group A ➡ Group B and vice versa)
        competition.active_group = (
            competition.group_two
            if competition.active_group == competition.group_one
            else competition.group_one
        )

        competition.current_question_index += 1
        competition.save()

        return redirect("mrsafe_app:competition_live", competition_id=competition.id)

    return render(request, "mrsafe_app/premium/competition_live.html", {
        "competition": competition,
        "current_question": current_question,
        "active_group": active_group,
    })
#______________________________________________________________________

@login_required
def competition_results(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id, trainer=request.user)

    # Each team has a max of 10 points (5 questions × 2 points each)
    group_one_score = competition.group_one_score  # 0 to 10
    group_two_score = competition.group_two_score  # 0 to 10

    # Calculate percentage for the progress bars
    group_one_percentage = (group_one_score / 10) * 100
    group_two_percentage = (group_two_score / 10) * 100


    # ✅ Determine the winner
    if group_one_score > group_two_score:
        competition.winner = competition.group_one
    elif group_two_score> group_one_score:
        competition.winner = competition.group_two
    else:
        competition.winner = None  # Draw

    competition.save()


    return render(request, "mrsafe_app/premium/competition_results.html", {
        "competition": competition,
        "group_one_score": group_one_score,
        "group_two_score": group_two_score,
        "group_one_percentage": group_one_percentage,
        "group_two_percentage": group_two_percentage,
    })

#______________________________________________________________________________________________


# Set OpenAI API key from Django settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Debugging: Check if API Key is correctly loaded
print("[DEBUG] Checking OpenAI API Key...")  # Confirms this part of the script runs
if openai.api_key:
    print("[DEBUG] OpenAI API Key:", openai.api_key[:5] + "...")
else:
    print("[ERROR] OpenAI API Key is missing or not loaded!")

logger = logging.getLogger(__name__)

@login_required
def generate_quiz_ai(request):
    if request.method == 'POST':
        user = request.user  # ✅ Get the logged-in user
        data = json.loads(request.body)
        topic = data.get("topic", "general knowledge")
        num_questions = data.get("num_questions", 5)

        # ✅ Define AI Quiz Cost
        COINS_REQUIRED = 10  # Example cost per AI quiz

        # ✅ Check User's Coin Balance
        user_balance = UserCoinBalance.objects.get_or_create(user=user)[0]
        if user_balance.coins < COINS_REQUIRED:
            return JsonResponse({"error": "❌ Not enough coins! Earn more by playing quizzes."}, status=400)

        prompt = (
            f"Generate {num_questions} multiple-choice questions about {topic}. "
            "Each question should have 4 answer choices (A, B, C, D) and specify the correct answer. "
            "Return a JSON response with this structure:\n"
            '{"questions": [{"question": "What is the capital of France?", '
            '"options": {"A": "Paris", "B": "London", "C": "Berlin", "D": "Madrid"}, '
            '"correct_answer": "A"}]}'
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "You are a quiz generator."},
                          {"role": "user", "content": prompt}],
                max_tokens=1500,  # ✅ Ensure enough tokens for full response
                temperature=0.5
            )

            response_text = response["choices"][0]["message"]["content"]
            print(f"✅ AI Response:\n{response_text}")  # ✅ Debugging: Check AI output

            try:
                data = json.loads(response_text)
                if len(data["questions"]) < num_questions:
                    print("⚠️ Warning: OpenAI returned fewer questions than requested.")

                # ✅ Deduct Coins After Successful AI Quiz Generation
                user_balance.coins -= COINS_REQUIRED
                user_balance.save()

                # ✅ Log Coin Activity
                CoinActivity.objects.create(
                    user=user,
                    activity_type="AI Quiz Generation",
                    coins_spent=COINS_REQUIRED,
                    description=f"Generated an AI-powered quiz on {topic}."
                )

                return JsonResponse(data)

            except json.JSONDecodeError:
                print("❌ Error: OpenAI response is not valid JSON.")
                return JsonResponse({"error": "Invalid response format."}, status=500)

        except openai.error.AuthenticationError:
            return JsonResponse({"error": "❌ OpenAI Authentication Failed!"}, status=401)
        except openai.error.RateLimitError:
            return JsonResponse({"error": "⚠️ OpenAI Rate Limit Exceeded!"}, status=429)
        except Exception as e:
            return JsonResponse({"error": f"❌ Unexpected Error: {str(e)}"}, status=500)

##########################################################################################

@login_required
def start_ai_challenge(request):
    topic = request.session.get("challenge_topic", "general knowledge")
    # Reset or create a fresh challenge (score starts at 0)
    challenge, created = AIChallenge.objects.get_or_create(
        user=request.user,
        is_active=True,
    )
    challenge.current_score = 0
    challenge.streak = 0
    challenge.difficulty = "easy"
    challenge.is_active = True
    challenge.save()

    question_set = []
    for i in range(5):
        q_text, q_choices, q_correct = fetch_ai_question(challenge.difficulty, topic)
        if q_text is None:
            messages.error(request, "Error generating AI question. Please try again later.")
            return redirect("ai_challenge_end", challenge_id=challenge.id)
        question_set.append({
            "question": q_text,
            "choices": q_choices,
            "correct_answer": q_correct,
        })
        print(f"[start_ai_challenge] Generated question {i+1}: {q_text}")
    request.session["question_set"] = question_set
    request.session["current_index"] = 0
    return redirect("ai_challenge_play", challenge_id=challenge.id)


@login_required
def ai_challenge_set(request, challenge_id):
    challenge = get_object_or_404(AIChallenge, id=challenge_id, user=request.user)
    question_set = request.session.get("question_set", [])
    current_index = request.session.get("current_index", 0)
    total_questions = len(question_set)
    print(f"[ai_challenge_set] current_index: {current_index}, total_questions: {total_questions}")

    if total_questions == 0:
        messages.error(request, "No questions available. Please try again.")
        return redirect("ai_challenge_end", challenge_id=challenge.id)

    feedback = None
    if request.method == "POST":
        user_answer = request.POST.get("user_answer", "").strip()
        current_question = question_set[current_index]
        correct_answer = current_question.get("correct_answer")
        if user_answer.upper() == correct_answer.upper():
            challenge.double_score()
            challenge.streak += 1
            challenge.save()
            if challenge.streak % 3 == 0:
                challenge.increase_difficulty()
            feedback = "Correct!"
            messages.success(request, feedback)
            current_index += 1
            request.session["current_index"] = current_index
            print(f"[ai_challenge_set] Answer correct. New current_index: {current_index}")
        else:
            feedback = f"Wrong answer! The correct answer was: {correct_answer}."
            messages.error(request, feedback)
            challenge.end_challenge()
            return redirect("ai_challenge_end", challenge_id=challenge.id)

    if current_index >= total_questions:
        print("[ai_challenge_set] Question set complete.")
        return render(request, "mrsafe_app/ai_challenge/ai_challenge_set_complete.html", {
            "challenge": challenge,
            "feedback": feedback,
            "progress": f"{total_questions}/{total_questions}",
        })
    else:
        current_question = question_set[current_index]
        progress = f"{current_index+1}/{total_questions}"
        return render(request, "mrsafe_app/ai_challenge/ai_challenge_set.html", {
            "challenge": challenge,
            "question": current_question["question"],
            "choices": current_question["choices"],
            "progress": progress,
            "feedback": feedback,
        })

@login_required
def continue_ai_challenge(request, challenge_id):
    challenge = get_object_or_404(AIChallenge, id=challenge_id, user=request.user)
    topic = request.session.get("challenge_topic", "general knowledge")
    question_set = []
    for i in range(5):
        q_text, q_choices, q_correct = fetch_ai_question(challenge.difficulty, topic)
        if q_text is None:
            messages.error(request, "Error generating AI question. Please try again later.")
            return redirect("ai_challenge_end", challenge_id=challenge.id)
        question_set.append({
            "question": q_text,
            "choices": q_choices,
            "correct_answer": q_correct,
        })
        print(f"[continue_ai_challenge] Generated question {i+1}: {q_text}")
    request.session["question_set"] = question_set
    request.session["current_index"] = 0
    return redirect("ai_challenge_set", challenge_id=challenge.id)

@login_required
def ai_challenge_end(request, challenge_id):
    challenge = get_object_or_404(AIChallenge, id=challenge_id, user=request.user)
    return render(request, "mrsafe_app/ai_challenge/ai_challenge_end.html", {"challenge": challenge})

logger = logging.getLogger(__name__)

@login_required
def ai_challenge(request):
    try:
        # Debugging Logs
        logger.info(f"User {request.user.username} is attempting AI challenge.")

        # Check if "ai_challenge" coin activity exists
        ai_activity = CoinActivity.objects.get(name="ai_challenge", is_active=True)

        # Get user balance
        user = request.user
        user_balance, created = UserCoinBalance.objects.get_or_create(user=user)

        # Check if user has enough coins
        if user_balance.balance < ai_activity.coin_amount:
            messages.error(request, "❌ Insufficient coins to participate in the AI challenge.")
            logger.warning(f"User {user.username} has insufficient coins.")
            return redirect("mrsafe_app:profile")

        # Deduct coins
        user_balance.update_balance(ai_activity.coin_amount, "spend", ai_activity)
        user_balance.save()

        # Log transaction
        CoinTransaction.objects.create(
            user=user,
            amount=ai_activity.coin_amount,
            transaction_type="spent",
            activity=ai_activity
        )

        logger.info(f"User {user.username} spent {ai_activity.coin_amount} coins for AI challenge.")

        # Proceed to the challenge
        return render(request, "mrsafe_app/ai_challenge/ai_challenge.html")

    except CoinActivity.DoesNotExist:
        messages.error(request, "❌ Coin activity 'ai_challenge' not found or inactive.")
        logger.error("CoinActivity 'ai_challenge' does not exist.")
        return redirect("mrsafe_app:profile")

    except Exception as e:
        logger.exception(f"Unexpected error in ai_challenge: {e}")
        messages.error(request, "❌ Something went wrong. Try again later.")
        return redirect("mrsafe_app:profile")

@login_required
def choose_topic(request):
    if request.method == "POST":
        topic = request.POST.get("topic", "general knowledge")
        request.session["challenge_topic"] = topic
        return redirect("start_ai_challenge")
    return render(request, "mrsafe_app/ai_challenge/choose_topic.html")

#_______________________________________________________________________

def leaderboard_view(request):
    top_players = AIChallengeLeaderboard.get_top_players()
    data = [{"username": p.user.username, "score": p.score} for p in top_players]
    return JsonResponse({"leaderboard": data})
#______________________________________________________________________________

@csrf_exempt  # ✅ Allows POST requests without CSRF token
def submit_score(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # ✅ Get JSON data from request
            score = data.get("score", 0)  # ✅ Extract score
            return JsonResponse({"message": "Score submitted successfully!", "score": score})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)
#_______________________________________________________________________________________

def shopify_products_view(request):
    """View to display Shopify products in the QuizAi app"""
    products = get_products()

    if "error" in products:
        return render(request, "shopify_products.html", {"error": products["error"]})

    return render(request, "shopify_products.html", {"products": products})

def switch_language(request):
    lang_code = request.POST.get('language', settings.LANGUAGE_CODE)
    next_url = request.POST.get('next', '/')

    activate(lang_code)  # Change the language

    response = redirect(next_url)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response

def shopify_store_view(request):
    """View to display the full Shopify store and available products"""
    products = get_products()

    if "error" in products:
        return render(request, "shopify_store.html", {"error": products["error"]})

    return render(request, "shopify_store.html", {"products": products})

def terms_and_conditions(request):
    terms = TermsAndConditions.objects.first()  # ✅ Get the first terms entry
    return render(request, "mrsafe_app/base/terms_and_conditions.html", {"terms": terms})

# views.py

def terms_view(request):
    terms = TermsAndConditions.objects.first()  # Get the first terms entry
    return render(request, "mrsafe_app/base/terms.html", {"terms": terms})

def privacy_policy(request):
    # Assuming you have a model for storing privacy content, or using static content
    return render(request, 'mrsafe_app/base/privacy_policy.html', {
        'title': 'Privacy Policy',
        'content': 'Your privacy policy content goes here.'
    })

#_PVP Challenge____________________________________________________________________________________

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_ai_questions(topic, difficulty, num_questions=5):
    prompt = (
        f"Generate {num_questions} {difficulty}-level multiple-choice questions on the topic: {topic}.\n"
        "Each question must have 4 answer choices (A, B, C, D) and a correct answer.\n"
        "Return in JSON format:\n"
        '{"questions": [{"question": "...", "choices": {"A": "...", "B": "...", "C": "...", "D": "..."}, "correct_answer": "A"}]}'
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI quiz generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2000
        )

        response_text = response.choices[0].message.content.strip()
        data = json.loads(response_text)
        return data.get("questions", [])

    except Exception as e:
        print("❌ AI Error:", e)
        return []

################################################################################################

def edit_reward(request, reward_id):
    reward = get_object_or_404(Reward, id=reward_id)
    if request.method == "POST":
        form = RewardForm(request.POST, request.FILES, instance=reward)
        if form.is_valid():
            form.save()
            return redirect('mrsafe_app:manage_rewards')  # ✅ Correct Redirect to the Named URL
    else:
        form = RewardForm(instance=reward)

    return render(request, 'mrsafe_app/admin/edit_reward.html', {'form': form, 'reward': reward})


def delete_reward(request, reward_id):
    reward = get_object_or_404(Reward, id=reward_id)
    if request.method == "POST":
        reward.delete()
        return redirect('manage_rewards')  # ✅ Redirect to Rewards Management
    return redirect('manage_rewards')

def add_reward(request):
    if request.method == "POST":
        form = RewardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Reward added successfully!")
            return redirect("manage_rewards")
    else:
        form = RewardForm()

    return render(request, "mrsafe_app/admin/add_reward.html", {"form": form})


def manage_rewards(request):
    rewards = Reward.objects.all()
    return render(request, "mrsafe_app/admin/manage_rewards.html", {"rewards": rewards})

from django.http import JsonResponse

######################COiNS Coins Coins ###################################################

def update_user_coins(request):
    """Handles adding or deducting coins from a user."""
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        amount = int(request.POST.get("amount"))
        action = request.POST.get("action")

        user = get_object_or_404(User, id=user_id)
        user_balance, created = UserCoinBalance.objects.get_or_create(user=user)

        # Fetch the appropriate coin activity (if needed for logging or extra tracking)
        try:
            coin_activity = CoinActivity.objects.get(name=action, is_active=True)
        except CoinActivity.DoesNotExist:
            messages.error(request, f"❌ The '{action}' activity is not found or is inactive.")
            return redirect("mrsafe_app:admin_dashboard")

        # Handle the action (add or deduct coins)
        if action == "add":
            # Using the update_balance method to add coins
            user_balance.update_balance(action)  # Using action as the activity name
            transaction_type = "earned"
            messages.success(request, f"✅ {amount} coins added to {user.username}.")

        elif action == "deduct":
            if user_balance.balance < amount:
                messages.error(request, "❌ Insufficient balance.")
                return redirect("mrsafe_app:admin_dashboard")
            # Using the update_balance method to deduct coins
            user_balance.update_balance(action)  # Using action as the activity name
            transaction_type = "spent"
            messages.success(request, f"⚠️ {amount} coins deducted from {user.username}.")

        # Log the transaction
        CoinTransaction.objects.create(
            user=user, amount=amount, transaction_type=transaction_type
        )

        # Save the updated balance
        user_balance.save()

    return redirect("mrsafe_app:admin_dashboard")

def add_coin_activity(request):
    """Allows admin to add new coin activities dynamically."""
    if request.method == "POST":
        name = request.POST["name"]
        activity_type = request.POST["activity_type"]
        coin_amount = int(request.POST["coin_amount"])
        is_active = request.POST.get("is_active", False) == "on"

        CoinActivity.objects.create(
            name=name, activity_type=activity_type, coin_amount=coin_amount, is_active=is_active
        )

        messages.success(request, f"✅ '{name}' activity added.")
        return redirect("mrsafe_app:admin_dashboard")

    return render(request, "mrsafe_app/admin/add_coin_activity.html")  # ✅ Ensure correct template path

def edit_coin_activity(request, activity_id):
    print(f"🔍 Debug: Looking for activity with ID {activity_id}")
    
    activity = get_object_or_404(CoinActivity, id=activity_id)
    
    print(f"✅ Found activity: {activity.name}")


    if request.method == "POST":
        activity.name = request.POST["name"]
        activity.activity_type = request.POST["activity_type"]
        activity.coin_amount = int(request.POST["coin_amount"])
        activity.is_active = "is_active" in request.POST  # ✅ Checkbox Handling

        activity.save()
        messages.success(request, f"✅ '{activity.name}' updated successfully!")
        return redirect("mrsafe_app:admin_dashboard")

    return render(request, "mrsafe_app/admin/edit_coin_activity.html", {"activity": activity})




def change_theme(request):
    """Handles theme change and stores it in session"""
    if request.method == 'POST':
        selected_theme = request.POST.get('theme', 'default')
        request.session['theme'] = selected_theme  # ✅ Store the theme in session
    return redirect(request.META.get('HTTP_REFERER', 'home'))  # Redirect back to previous page

from django.shortcuts import render

def test_css(request):
    return render(request, 'test_css.html')

#######################################################################################    




##############################################################################################

#############################################################################################
def view_ads(request):
    active_ads = AdActivity.objects.filter(is_active=True)
    return render(request, 'ads_view.html', {'active_ads': active_ads})

def create_google_ad_activity(request):
    if request.method == 'POST':
        form = AdActivityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New Google Ad Activity has been added successfully!')
            return redirect('mrsafe_app:google_ad_activity_list')  # Redirect to a list of ad activities or another page.
        else:
            messages.error(request, 'There was an error while adding the Google Ad Activity.')
    else:
        form = AdActivityForm()

    return render(request, 'mrsafe_app/create_google_ad_activity.html', {'form': form})

def add_google_ad_activity(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        ad_type = request.POST.get('ad_type')
        is_active = request.POST.get('is_active') == 'True'
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        AdActivity.objects.create(
            name=name,
            ad_type=ad_type,
            is_active=is_active,
            start_date=start_date,
            end_date=end_date
        )

        # ✅ Redirect back to the admin dashboard after adding
        return redirect('mrsafe_app:admin_dashboard')  # or your actual dashboard URL name

    # Only if GET request (optional separate page)
    return render(request, 'quizzes/add_google_ad_activity.html')


def google_ad_activity_list(request):
    activities = AdActivity.objects.all()
    return render(request, 'mrsafe_app/google_ad_activity_list.html', {'google_ad_activities': activities})
##################################################################################################


# 🔧 EDIT VIEW
def edit_google_ad_activity(request, pk):
    activity = get_object_or_404(AdActivity, pk=pk)

    if request.method == 'POST':
        activity.name = request.POST.get('name')
        activity.ad_type = request.POST.get('ad_type')
        activity.start_date = request.POST.get('start_date')
        activity.end_date = request.POST.get('end_date')
        activity.is_active = request.POST.get('is_active') == 'True'
        activity.save()
        return redirect('mrsafe_app:admin_dashboard')

    return render(request, 'mrsafe_app/edit_google_ad_activity.html', {
        'activity': activity,
    })


# ❌ DELETE VIEW
def delete_google_ad_activity(request, pk):
    activity = get_object_or_404(AdActivity, pk=pk)

    if request.method == 'POST':
        activity.delete()
        return redirect('mrsafe_app:admin_dashboard')

    return redirect('mrsafe_app:admin_dashboard')

#####################################################################################


##################################################################3
@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(StoreItem, id=item_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, item=item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('mrsafe_app:view_cart')

def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.item.price * item.quantity for item in cart_items)

    return render(request, "store/cart.html", {
        "cart_items": cart_items,
        "total_price": total_price
    })


@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.item.price * item.quantity for item in cart_items)

    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total_price': round(total_price, 2),
    })
# views.py
# views.py
import json
from datetime import timedelta
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from ..models import PremiumPlan, PremiumProfile, StoreItem, CartItem
from ..braintree_config import gateway


@csrf_exempt
@login_required
def process_payment(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."})

    try:
        data = json.loads(request.body)
        user = request.user
        nonce = data.get("nonce")
        plan_id = data.get("plan_id")
        cart_total = data.get("cart_total")

        # 🔹 PREMIUM PLAN PURCHASE
        if plan_id:
            plan = PremiumPlan.objects.get(id=plan_id)
            profile, _ = PremiumProfile.objects.get_or_create(user=user)

            if profile.is_active and profile.end_date:
                days_remaining = (profile.end_date.date() - now().date()).days
                if days_remaining >= 365:
                    return JsonResponse({
                        "success": False,
                        "error": "⛔ Your premium is already valid for more than a year."
                    })

            result = gateway.transaction.sale({
                "amount": str(plan.price),
                "payment_method_nonce": nonce,
                "options": {"submit_for_settlement": True}
            })

            if not result.is_success:
                error_detail = result.transaction.processor_response_text if result.transaction else result.message
                return JsonResponse({"success": False, "error": f"Payment failed: {error_detail}"})

            # ✅ Log the payment
            PaymentTransaction.objects.create(
                user=user,
                amount=plan.price,
                currency="USD",
                payment_method="google_pay",
                gateway_transaction_id=result.transaction.id,
                status="Success",
                notes=f"Premium Plan: {plan.name}"
            )

            # ✅ Extend premium
            now_time = now()
            base_date = profile.end_date if profile.end_date and profile.end_date > now_time else now_time
            new_expiry = base_date + timedelta(days=plan.duration_days)

            profile.start_date = now_time
            profile.end_date = new_expiry
            profile.plan = plan
            profile.is_active = True
            profile.trial_used = True
            profile.auto_renewal = True
            profile.save()

            # ✅ Add bonus coins and log it
            if plan.coin_bonus > 0:
                coin_balance, _ = UserCoinBalance.objects.get_or_create(user=user)
                coin_balance.balance += plan.coin_bonus
                coin_balance.save()

                CoinTransaction.objects.create(
                    user=user,
                    amount=plan.coin_bonus,
                    transaction_type="earned",
                    description=f"Bonus coins from Premium Plan: {plan.name}"
                )

            user.is_premium = True
            user.save(update_fields=["is_premium"])

            return JsonResponse({
                "success": True,
                "message": f"✅ Premium activated until {new_expiry.date()}!"
            })

        # 🔸 STORE CART PURCHASE
        elif cart_total:
            cart_items = CartItem.objects.select_related("item").filter(user=user)
            if not cart_items.exists():
                return JsonResponse({"success": False, "error": "🛒 Your cart is empty."})

            result = gateway.transaction.sale({
                "amount": str(cart_total),
                "payment_method_nonce": nonce,
                "options": {"submit_for_settlement": True}
            })

            if not result.is_success:
                error_detail = result.transaction.processor_response_text if result.transaction else result.message
                return JsonResponse({"success": False, "error": f"Payment failed: {error_detail}"})

            # ✅ Log the payment
            PaymentTransaction.objects.create(
                user=user,
                amount=cart_total,
                currency="USD",
                payment_method="google_pay",
                gateway_transaction_id=result.transaction.id,
                status="Success",
                notes="Store checkout purchase"
            )

            # ✅ Award coins
            total_awarded_coins = sum(
                cart_item.item.coins_amount * cart_item.quantity
                for cart_item in cart_items if hasattr(cart_item.item, 'coins_amount')
            )

            coin_balance, _ = UserCoinBalance.objects.get_or_create(user=user)
            coin_balance.balance += total_awarded_coins
            coin_balance.save()

            # ✅ Log coin transaction
            if total_awarded_coins > 0:
                CoinTransaction.objects.create(
                    user=user,
                    amount=total_awarded_coins,
                    transaction_type="earned",
                    description="Coins awarded from store purchase"
                )

            # ✅ Clear cart
            cart_items.delete()

            return JsonResponse({
                "success": True,
                "message": f"✅ Purchase successful! +{total_awarded_coins} coins awarded."
            })

        else:
            return JsonResponse({"success": False, "error": "Missing or invalid payment data."})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})



@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, user=request.user, item_id=item_id)
    cart_item.delete()
    return redirect('mrsafe_app:view_cart')

# views.py

###########################################################################################

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        environment=braintree.Environment.Sandbox,
        merchant_id=settings.BRAINTREE_MERCHANT_ID,
        public_key=settings.BRAINTREE_PUBLIC_KEY,
        private_key=settings.BRAINTREE_PRIVATE_KEY,
    )
)

def generate_client_token(request):
    token = gateway.client_token.generate()
    return JsonResponse({'clientToken': token})


def braintree_token(request):
    gateway = braintree.BraintreeGateway(
        braintree.Configuration(
            braintree.Environment.Sandbox,
            merchant_id='your_merchant_id',
            public_key='your_public_key',
            private_key='your_private_key'
        )
    )
    client_token = gateway.client_token.generate()
    return JsonResponse({'clientToken': client_token})


# views.py
from django.views.generic import TemplateView

class HelpView(TemplateView):
    template_name = 'mrsafe_app/base/help.html'

from django.views import View

class FAQView(View):
    def get(self, request):
        return render(request, 'mrsafe_app/base/faq.html')
    
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        sender_email = request.POST.get('email')
        user_message = request.POST.get('message')

        subject = f"📩 Contact Form Message from {name}"
        message = f"""
        📬 New Contact Submission:

        Name: {name}
        Email: {sender_email}

        Message:
        {user_message}
        """

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False
            )
            return render(request, 'mrsafe_app/base/contact.html', {
                'success': True,
                'message': '✅ Your message has been sent successfully!'
            })
        except Exception as e:
            return render(request, 'mrsafe_app/base/contact.html', {
                'success': False,
                'message': f"❌ Failed to send message: {str(e)}"
            })

    return render(request, 'mrsafe_app/base/contact.html')


# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from ..models import UserProfile, CoinActivity

@login_required
def premium_subscription_success(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.activate_premium(coin_bonus=1000)

    CoinActivity.objects.create(
        user=request.user,
        activity_type="premium_bonus",
        amount=1000
    )

    messages.success(request, "🎉 Premium membership activated! You received 1000 coins.")
    return redirect('mrsafe_app:profile')

# ✅ About Page
def about(request):
    User = get_user_model()
    users = User.objects.all()
    return render(request, 'mrsafe_app/base/about.html', {'users': users})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

    
#######################################################################################

######admin controls #############################################
from django.db.models import Sum, Avg




from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from mrsafe_app.models import CustomUser, PremiumProfile

@staff_member_required
def user_management_view(request):
    users = CustomUser.objects.all()

    # Attach .is_premium dynamically
    premium_user_ids = set(PremiumProfile.objects.filter(is_active=True).values_list('user_id', flat=True))
    
    for user in users:
        user.is_premium = user.id in premium_user_ids

    return render(request, 'mrsafe_app/admin/admin_user_management.html', {"users": users})


@login_required
def user_profile_view(request, user_id):
    if not request.user.is_staff:
        return redirect("mrsafe_app:profile")  # Redirect non-admins

    user = get_object_or_404(CustomUser, id=user_id)
    context = get_user_profile_data(user)
    print(context.keys())

    return render(request, "mrsafe_app/admin/user_profile.html", context)



# views.py
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from ..models import Category

@staff_member_required
def manage_categories_view(request):
    categories = Category.objects.all().order_by("name")
    return render(request, "mrsafe_app/admin/admin_category_manage.html", {"categories": categories})

from ..models import StoreItem
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def store_manage_view(request):
    store_items = StoreItem.objects.all()
    return render(request, "mrsafe_app/admin/admin_store_manage.html", {
        "store_items": store_items
    })

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.shortcuts import render

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def coin_manage_view(request):
    User = get_user_model()  # ✅ Correct way to access the custom user model
    users = User.objects.all()

    coin_activities = CoinActivity.objects.all()
    transactions = CoinTransaction.objects.all().order_by('-timestamp')  # ✅ You forgot to import this originally

    return render(request, "mrsafe_app/admin/admin_coin_manage.html", {
        "users": users,
        "coin_activities": coin_activities,  # ❗ Fix typo here
        "transactions": transactions         # ✅ Include this so template doesn’t break
    })

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from ..models import PremiumPlan
# Make sure this decorator exists

@login_required
@user_passes_test(is_admin)
def premium_plan_manage_view(request):
    premium_plans = PremiumPlan.objects.all()
    return render(request, "mrsafe_app/admin/admin_premium_manage.html", {
        "premium_plans": premium_plans
    })

@login_required
@user_passes_test(is_admin)
def reward_manage_view(request):
    from ..models import Reward
    rewards = Reward.objects.select_related('reward_type', 'challenge_type').all()
    return render(request, "mrsafe_app/admin/admin_rewards_manage.html", {
        "rewards": rewards
    })

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from ..models import AdActivity

@staff_member_required
def admin_google_ads_manage_view(request):
    ad_activities = AdActivity.objects.all().order_by('-start_date')
    return render(request, "mrsafe_app/admin/admin_google_ads_manage.html", {
        "ad_activities": ad_activities
    })
from django.db.models import Sum
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from mrsafe_app.models import CoinTransaction, CustomUser

from django.db.models import Sum
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from mrsafe_app.models import CoinTransaction, CustomUser

@login_required
def coin_transaction_history(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    sort = request.GET.get("sort", "date")
    per_page = request.GET.get("per_page", "10")

    # Handle "all"
    if per_page == "all":
        per_page = None
    else:
        per_page = int(per_page)

    # Sorting
    transactions = CoinTransaction.objects.filter(user=user).select_related("activity")
    if sort == "type":
        transactions = transactions.order_by("transaction_type", "-timestamp")
    else:
        transactions = transactions.order_by("-timestamp")

    # Totals
    total_earned = transactions.filter(transaction_type='earned').aggregate(total=Sum('amount'))['total'] or 0
    total_spent = transactions.filter(transaction_type='spent').aggregate(total=Sum('amount'))['total'] or 0

    # Pagination
    if per_page:
        paginator = Paginator(transactions, per_page)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
    else:
        # No pagination — show all
        page_obj = transactions

    return render(request, "mrsafe_app/admin/coin_transaction_history.html", {
        "user": user,
        "page_obj": page_obj,
        "sort": sort,
        "per_page": request.GET.get("per_page", "10"),
        "total_earned": total_earned,
        "total_spent": total_spent,
    })
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from mrsafe_app.models import CustomUser, PaymentTransaction

@login_required
def payment_history_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    sort = request.GET.get("sort", "date")
    per_page = request.GET.get("per_page", 10)

    payments = PaymentTransaction.objects.filter(user=user).order_by("-created_at")

    paginator = Paginator(payments, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "mrsafe_app/admin/payment_history.html", {
        "user": user,
        "page_obj": page_obj,
        "per_page": per_page,
        "sort": sort,
    })

from django.shortcuts import render

from django.shortcuts import render

def public_landing(request):
    return render(request, "index.html")

from django.contrib.auth import get_user_model
from django.shortcuts import render

def create_superuser_view(request):
    User = get_user_model()
    created = False

    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='YourSecurePassword123'  # Change before launch
        )
        created = True

    return render(request, "mrsafe/create_superuser.html", {"created": created})
