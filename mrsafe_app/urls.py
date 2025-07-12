from django.urls import path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import set_language, i18n_patterns
from django.contrib.auth import views as auth_views
from .views import home
from django.urls import path
from . import views  # your view imports
from django.conf import settings
from django.conf.urls.static import static
from .views import views_files
from .views import (
    # Auth & User
    
    CustomPasswordResetView, switch_language, upgrade_membership,
    enter_premium_code, remove_linked_user, join_trainer,
    add_to_cart,  edit_user, delete_user,
    update_user_coins, add_coin_activity, edit_coin_activity, 


    # Dashboard
    premium_dashboard, admin_dashboard, 

   # Store
    process_payment,payment_history_view,

    # Certificates
    user_management_view,manage_categories_view,coin_transaction_history,premium_plan_manage_view,admin_google_ads_manage_view,
    
    terms_view,edit_google_ad_activity,
    premium_subscription_success,
    premium_membership_view,complete_premium_checkout,
   
   
    # inspect
   safety_image_test,   
    )

from django.contrib.auth.views import LogoutView




      # Temporary route

app_name = 'mrsafe_app'  # Keep the namespace

# urls.pypip install django

from django.urls import path
from .views.views_files import HelpView,view_cart  # Ensure this imports the class

from django.urls import path
from .views.views_files import FAQView
from .views import (contact,
                    remove_from_cart,generate_client_token,delete_google_ad_activity,add_google_ad_activity,
                    google_ad_activity_list,
                    
                    change_theme,test_css,delete_item,
                    
                    
                    terms_and_conditions,privacy_policy,
                    premium_membership,add_premium_plan,
                    register,profile,
                    edit_profile,about,store_home,add_item,edit_item,premium_checkout,public_landing, 
                    inspect,save_observation,inspect_success,observation_detail,
                    observation_list,inspection_detail,inspection_create,inspection_list,site_inspection_image_test
                    ,site_inspection_start,safe_site_observation,finalize_inspection,
                    export_inspection_pdf,export_inspection_ppt,
                    inspection_full_report,export_inspection_docx,
                    
                    
                    subscribe_premium,PremiumPlanListView,plan_checkout,CartCheckoutView
                    ,coin_manage_view,delete_coin_activity,SafetyDashboardView,notifications_api,notification_settings)


from django.urls import path

from django.shortcuts import redirect


urlpatterns = [
 path('settings/notifications/', views.notification_settings, name='notification_settings'),

path('api/notifications', views.notifications_api, name='notifications_api'),
  path('dashboard/', SafetyDashboardView.as_view(), name='safety_dashboard'),
  
  

path('register/', register, name='register'),
    
path('login/', auth_views.LoginView.as_view(template_name='mrsafe/login.html'), name='login'),

path(
    'logout/',
    LogoutView.as_view(
        next_page=None,  # To render the template
        template_name='mrsafe/logged_out.html'
    ),
    name='logout'
),


path('', home, name='home'),  # ✅ This makes /mrsafe/ go to home()

path("inspect/", safety_image_test, name="safety_image_test"),
path("save-observation/", save_observation, name="save_observation"),

path("inspect/", inspect, name="inspect"),
path('inspect/success/', inspect_success, name='inspect_success'),
path('observations/', observation_list, name='observation_list'),
path("observation/<int:pk>/", observation_detail, name="observation_detail"),

path('inspections/', inspection_list, name='inspection_list'),
path('inspections/create/', inspection_create, name='inspection_create'),
path('inspections/<int:inspection_id>/', inspection_detail, name='inspection_detail'),


    # Site Inspection Image Test (New View)
path('inspections/<int:inspection_id>/test/', site_inspection_image_test, name='site_inspection_image_test'),
path('inspections/<int:inspection_id>/start/', site_inspection_start, name='site_inspection_start'),

path("inspections/<int:inspection_id>/save/", safe_site_observation, name="save_observation"),
path("inspections/<int:inspection_id>/finalize/", finalize_inspection, name="finalize_inspection"),
path("inspections/<int:inspection_id>/export/pdf/", export_inspection_pdf, name="export_inspection_pdf"),
path("inspections/<int:inspection_id>/export/ppt/", export_inspection_ppt, name="export_inspection_ppt"),
path("inspections/<int:inspection_id>/report/",inspection_full_report, name="inspection_full_report"),
path("inspections/<int:inspection_id>/export/docx/", export_inspection_docx, name="export_inspection_docx"),
  
    path('safety-image-test/', safety_image_test, name='safety_image_test'),
    
path("premium/subscribe/<str:plan>/", subscribe_premium, name="subscribe_premium"),
    
    path('admin/user-management/', user_management_view, name='user_management'),
    path("admin/coins/", coin_manage_view, name="coin_manage"),
    path("admin/coins/delete/<int:activity_id>/", delete_coin_activity, name="delete_coin_activity"),

    path("admin/coin-history/<int:user_id>/", coin_transaction_history, name="coin_transaction_history"),
    path("admin/payments/<int:user_id>/", payment_history_view, name="payment_history"),

    # urls.py
    
   
    path("admin/premium-plans/", premium_plan_manage_view, name="premium_plan_manage"),
    

    path("admin/google-ads/", admin_google_ads_manage_view, name="google_ads_manage"),

    path("premium/", premium_membership_view, name="premium_membership"),
    path('plans/', PremiumPlanListView.as_view(), name='premium_plans'),
    path('plans/checkout/<slug:slug>/', plan_checkout, name='plan_checkout'),
   
    path('premium/complete/', complete_premium_checkout, name='complete_premium_checkout'),
    
    path('premium/checkout/', premium_checkout, name='premium_checkout'),
    path('cart/checkout/', CartCheckoutView, name='cart_checkout'),
    path("admin/add-premium-plan/", add_premium_plan, name="add_premium_plan"),
  
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('contact/', contact, name='contact'),

    path('faq/', FAQView.as_view(), name='faq'),

    path('help/', HelpView.as_view(), name='help'),  # Call .as_view() for class-based view

    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<int:item_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    

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

    #####################################################################################
    path("terms-and-conditions/", terms_and_conditions, name="terms_and_conditions"),

    path("terms/", terms_view, name="terms"),

    path('privacy-policy/', privacy_policy, name='privacy_policy'),

    path('switch-language/', switch_language, name='switch_language'),

    path('i18n/', include('django.conf.urls.i18n')),

    path('premium/', premium_membership, name='premium_membership'),
    path("premium-dashboard/", premium_dashboard, name="premium_dashboard"),  # ✅ Correct path
   
    path('join-trainer/', join_trainer, name='join_trainer'),  # ✅ Ensure the name matches

    path("enter-premium-code/", enter_premium_code, name="enter_premium_code"),

    path('remove-linked-user/<int:trainee_id>/', remove_linked_user, name='remove_linked_user'),

    path('store/add-to-cart/<int:item_id>/', add_to_cart, name='add_to_cart'),

    path("admin-dashboard/", admin_dashboard, name="admin_dashboard"),
    path("edit-user/<int:user_id>/", edit_user, name="edit_user"),  # ✅ Fix URL pattern
    path("delete-user/<int:user_id>/", delete_user, name="delete_user"),

    # 👤 Profile Management
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    
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

    path("upgrade-membership/", upgrade_membership, name="upgrade_membership"),
     path("ads.txt", serve, {"path": "ads.txt", "document_root": settings.BASE_DIR / "mrsafe_app"}),
    ]


# ✅ Serve Media Files During Development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)