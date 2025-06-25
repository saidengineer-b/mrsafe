from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import set_language, i18n_patterns
from django.contrib.auth import views as auth_views
from .views import home

from .views import views_files
from .views import (
    # Auth & User
    
    CustomPasswordResetView, switch_language, upgrade_membership,
    enter_premium_code, remove_linked_user, join_trainer,
    add_to_cart,  edit_user, delete_user,
    update_user_coins, add_coin_activity, edit_coin_activity, 


    # Dashboard
    premium_dashboard, admin_dashboard, 

    


    # Competitions
    create_competition, competitions_list, start_competition,
    competition_live, competition_results, calculate_winner,




    # Store
    shopify_products_view, shopify_store_view, process_payment,payment_history_view,

    # Certificates
    user_management_view,manage_categories_view,coin_transaction_history,premium_plan_manage_view,reward_manage_view,admin_google_ads_manage_view,
    
    terms_view,edit_google_ad_activity,
    premium_subscription_success,my_stats,
    premium_membership_view,complete_premium_checkout,
   
   
    # inspect
   safety_image_test,
   
    )





app_name = 'mrsafe_app'  # Keep the namespace

# urls.pypip install django

from django.urls import path
from .views.views_files import HelpView,view_cart  # Ensure this imports the class

from django.urls import path
from .views.views_files import FAQView
from .views import (contact,
                    remove_from_cart,checkout,generate_client_token,delete_google_ad_activity,add_google_ad_activity,
                    google_ad_activity_list,
                    
                    change_theme,test_css,delete_item,
                    manage_rewards,
                    
                    terms_and_conditions,privacy_policy,
                    premium_membership,add_premium_plan,
                    register,profile,
                    edit_profile,about,store_home,add_item,edit_item,premium_checkout,public_landing, inspect)


from django.urls import path




from django.shortcuts import redirect






urlpatterns = [
    


path("inspect/", inspect, name="inspect"),

# urls.py


  
    path('safety-image-test/', safety_image_test, name='safety_image_test'),
    
    path('admin/user-management/', user_management_view, name='user_management'),
   
    path("admin/coin-history/<int:user_id>/", coin_transaction_history, name="coin_transaction_history"),
    path("admin/payments/<int:user_id>/", payment_history_view, name="payment_history"),

    # urls.py
    path('admin/categories/', manage_categories_view, name='manage_categories'),
   
   
    path("admin/premium-plans/", premium_plan_manage_view, name="premium_plan_manage"),
    path("admin/rewards/", reward_manage_view, name="admin_reward_manage"),

    path("admin/google-ads/", admin_google_ads_manage_view, name="google_ads_manage"),


 
    path("premium/", premium_membership_view, name="premium_membership"),
    path('premium/complete/', complete_premium_checkout, name='complete_premium_checkout'),
    
    path('premium/checkout/', premium_checkout, name='premium_checkout'),
    


    path("admin/add-premium-plan/", add_premium_plan, name="add_premium_plan"),
  
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('contact/', contact, name='contact'),

    path('faq/', FAQView.as_view(), name='faq'),

    path('help/', HelpView.as_view(), name='help'),  # Call .as_view() for class-based view

    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<int:item_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', checkout, name='checkout'),

    path('process-payment/', process_payment, name='process_payment'),
    
    path('braintree/token/', generate_client_token, name='braintree_token'),
    # quiz_app/urls.py

    path('edit-google-ad-activity/<int:pk>/', edit_google_ad_activity, name='edit_google_ad_activity'),
    path('delete-google-ad-activity/<int:pk>/', delete_google_ad_activity, name='delete_google_ad_activity'),
    path('add-google-ad-activity/', add_google_ad_activity, name='add_google_ad_activity'),

    path('create-google-ad-activity/', add_google_ad_activity, name='create_google_ad_activity'),
    path('google-ad-activities/', google_ad_activity_list, name='google_ad_activity_list'),




    path('process-payment/', process_payment, name='process_payment'),
   

    path('change-theme/', change_theme, name='change_theme'),
    # Other URLs...


    path('change-theme/', change_theme, name='change_theme'),
    path('test-css/', test_css, name='test_css'),  # ✅ Add this line


    path("edit-coin-activity/<int:activity_id>/", edit_coin_activity, name="edit_coin_activity"),  # ✅ Ensure this exists

    
    path("add-coin-activity/", add_coin_activity, name="add_coin_activity"),  # ✅ URL added
    path("update-user-coins/", update_user_coins, name="update_user_coins"),

    path('admin/manage-rewards/', manage_rewards, name='manage_rewards'),
    


 
#################################################################################################





#####################################################################################


    path("terms-and-conditions/", terms_and_conditions, name="terms_and_conditions"),

    path("terms/", terms_view, name="terms"),

    path('privacy-policy/', privacy_policy, name='privacy_policy'),

    path("shopify-store/", shopify_store_view, name="shopify_store"),

    path("shopify-products/", shopify_products_view, name="shopify_products"),

    path('switch-language/', switch_language, name='switch_language'),

    path('i18n/', include('django.conf.urls.i18n')),


    # ✅ Competition Management
    path("competitions/", competitions_list, name="competitions_list"),  # List of competitions
    path("quizzes/competition/create/", create_competition, name="create_competition"),

    # ✅ Competition Flow
    path("competitions/<int:competition_id>/start/", start_competition, name="start_competition"),

    path("competitions/<int:competition_id>/live/", competition_live, name="competition_live"),  # Live competition page
    path("competitions/<int:competition_id>/results/", competition_results, name="competition_results"),  # Show results

    # ✅ Calculate Winner
    path("competitions/calculate-winner/<int:competition_id>/", calculate_winner, name="calculate_winner"),  # Determine winner

    path('premium/', premium_membership, name='premium_membership'),
    path("premium-dashboard/", premium_dashboard, name="premium_dashboard"),  # ✅ Correct path
   
    path('join-trainer/', join_trainer, name='join_trainer'),  # ✅ Ensure the name matches

    path("enter-premium-code/", enter_premium_code, name="enter_premium_code"),

    path('remove-linked-user/<int:trainee_id>/', remove_linked_user, name='remove_linked_user'),

    path('store/add-to-cart/<int:item_id>/', add_to_cart, name='add_to_cart'),

    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("edit-user/<int:user_id>/", edit_user, name="edit_user"),  # ✅ Fix URL pattern
    path("delete-user/<int:user_id>/", delete_user, name="delete_user"),



    # 👤 User Authentication
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='quiz_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # 👤 Profile Management
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('my_stats/', my_stats, name='my_stats'),


    # ℹ️ Static Pages
    path('about/', about, name='about'),
    

    # 🛍️ Store URLs
    path('store/', store_home, name='store'),
    path('store/add/', add_item, name='add_item'),
    path('store/edit/<int:item_id>/', edit_item, name='edit_item'),
    path('store/delete/<int:item_id>/', delete_item, name='delete_item'),

    # 🌐 Language Switching
    path('i18n/', set_language, name='set_language'),

   
    # 🔑 Password Reset
    path('password_reset/', CustomPasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

   
    path('premium-dashboard/', premium_dashboard, name='premium_dashboard'),

    path("upgrade-membership/", upgrade_membership, name="upgrade_membership"),]




# ✅ Serve Media Files During Development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

