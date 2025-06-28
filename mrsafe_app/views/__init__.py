from .views_premium import (
    upgrade_membership,premium_membership,subscribe_premium,add_premium_plan,
    premium_membership_view,premium_checkout,complete_premium_checkout
    ,premium_dashboard,
   
)


from .views_notifications import (
    get_notifications,
    mark_notification_as_read,
    clear_notifications,mark_all_as_read,
) 

from .views_inspect import (safety_image_test,inspect,save_observation,inspect_success,
                            observation_list,inspection_detail,inspection_create,inspection_list,
                            observation_detail,site_inspection_image_test,site_inspection_start,
                            dashboard,safe_site_observation) 


from .views_files import (
    public_landing,
    home,
    profile,
    register,
    
    edit_profile,
    login_view,
    CustomPasswordResetView,
    password_reset_done,
    store_home,
    add_item,
    edit_item,
    delete_item,
    admin_dashboard,
    edit_user,
    delete_user,
    create_course,
    edit_course,
    delete_course,
    add_store_item,
    edit_store_item,
    delete_store_item,
    add_to_cart,
    enter_premium_code,
    remove_linked_user,
    join_trainer,
    manage_groups,
    update_group,
    delete_group,
    create_group,
    add_members_to_group,
    assign_quiz_group,
    create_competition,
    competitions_list,
    calculate_winner,
    start_competition,
    competition_live,
    competition_results,
    generate_quiz_ai,
    start_ai_challenge,
    ai_challenge_set,
    continue_ai_challenge,
    ai_challenge_end,
    ai_challenge,
    choose_topic,
    leaderboard_view,
    submit_score,
    switch_language,
    shopify_products_view,
    shopify_store_view,
    terms_and_conditions,
    terms_view,
    privacy_policy,
    edit_reward,
    delete_reward,
    add_reward,
    manage_rewards,
    
    update_user_coins,
    add_coin_activity,
    edit_coin_activity,
    
    change_theme,
    test_css,
    process_payment,
    view_ads,
    create_google_ad_activity,
    add_google_ad_activity,
    google_ad_activity_list,
    edit_google_ad_activity,
    delete_google_ad_activity,
    generate_client_token,
    braintree_token,
    HelpView,
    FAQView,
    contact,
    view_cart,user_profile_view,coin_transaction_history,payment_history_view,
    checkout,manage_categories_view,
    coin_manage_view,
    store_manage_view,premium_plan_manage_view,reward_manage_view,user_profile_view,
    remove_from_cart,my_stats,user_management_view,admin_google_ads_manage_view,
    premium_subscription_success,about,
)





