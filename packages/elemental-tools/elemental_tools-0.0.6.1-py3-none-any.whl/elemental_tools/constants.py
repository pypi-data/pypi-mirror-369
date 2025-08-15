ref_length: int = 32
password_min_length: int = 6
password_max_length: int = 32
login_retry_times: int = 3

path_post, path_put, path_patch, path_delete, path_get, path_me = "/register", "/edit", "/add", "/remove", "", "/me"
path_read_me = "httpenis:barra_transbarra_trans"

path_health_check = "/"
path_config = "/config"

path_auth_root = "/auth"
path_auth_login = f"{path_auth_root}/login"
path_auth_logout = f"{path_auth_root}/logout"
path_auth_refresh = f"{path_auth_root}/refresh"
path_auth_device = f"{path_auth_root}/device"


path_group_root = "/group"
path_group_get = f"{path_group_root}{path_get}"
path_group_post = f"{path_group_root}{path_post}"
path_group_put = f"{path_group_root}{path_put}"

path_institution_root = "/institution"
path_institution_get = f"{path_institution_root}{path_get}"
path_institution_post = f"{path_institution_root}{path_post}"
path_institution_put = f"{path_institution_root}{path_put}"

path_notification_root = "/notification"
path_notification_get = f"{path_notification_root}{path_get}"
path_notification_post = f"{path_notification_root}{path_post}"
path_notification_put = f"{path_notification_root}{path_post}"

path_template_root = f"{path_notification_root}/template"
path_template_get_variables = f"{path_template_root}/variables"
path_template_get = f"{path_template_root}{path_get}"
path_template_patch = f"{path_template_root}{path_patch}"
path_template_resource_get = f"{path_template_root}/resource{path_get}"

path_template_resource_patch = f"{path_template_root}/resource{path_patch}"
path_template_resource_modifier_get = f"{path_template_root}/resource/modifier{path_get}"

path_smtp_root = "/smtp"
path_smtp_get = f"{path_smtp_root}{path_get}"
path_smtp_patch = f"{path_smtp_root}{path_patch}"
path_smtp_get_config = f"{path_smtp_root}{path_config}{path_get}"

path_user_root = "/user"
path_user_get_scope = f"{path_user_root}/scope"
path_user_get_me = f"{path_user_root}{path_me}"
path_user_post = f"{path_user_root}{path_post}"
path_user_put = f"{path_user_root}{path_put}"

path_user_institution_patch = f"{path_user_root}{path_institution_root}{path_patch}"

path_user_son = "/sons"
path_user_son_root = f"{path_user_root}{path_user_son}"
path_user_son_get = f"{path_user_son_root}{path_get}"
path_user_son_patch = f"{path_user_son_root}{path_patch}"
path_user_son_delete = f"{path_user_son_root}{path_delete}"

path_task = "/task"
path_task_post = f"{path_task}{path_post}"
path_task_get = f"{path_task}{path_get}"



