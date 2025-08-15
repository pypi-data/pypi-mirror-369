# square_common_bl

## about

common business layer for my personal server.

## Installation

```shell
pip install square_common_bl
```

## env

- python>=3.12.0

## changelog

### v5.0.0

- greeting
    - **breaking change**: replace create_greeting_v0 with create_anonymous_greeting_v0.

### v4.0.0

- authentication
    - **breaking change**: remove update_password_v0.

### v3.1.2

- authentication
    - update_user_recovery_methods_v0 make parameters optional.
- dependencies
    - square_authentication_helper>=2.5.2.

### v3.1.1

- dependencies
    - square_authentication_helper>=2.5.1.

### v3.1.0

- authentication
    - add new endpoint update_user_recovery_methods_v0.

### v3.0.0

- authentication
    - **breaking change**: delete_user_v0 is now POST instead of DELETE.

### v2.7.0

- authentication
    - update parameters for update_password_v0.
    - add validate_email_verification_code_v0.
    - add send_verification_email_v0.
    - add update_profile_details_v0.
    - add send_reset_password_email_v0.
    - add generate_account_backup_codes_v0.

### v2.6.5

- remove config.ini and config.testing.ini from version control.

### v2.6.4

- env
    - add ALLOW_ORIGINS

### v2.6.3

- mock ini file for pytest.

### v2.6.2

- make profile_photo optional in update_profile_photo_v0.

### v2.6.1

- add python multipart as dependency.

### v2.6.0

- bump square_file_store_helper>=3.0.0.
- authentication
    - add update_profile_photo_v0.

### v2.5.0

- new dependency square_file_store_helper.
- config
    - add new section SQUARE_FILE_STORE_HELPER.
- update gitignore to add temp folder.
- authentication
    - add cleanup_task.
    - add get_user_profile_photo_v0.

### v2.4.1

- bump square_logger to 2.0.0.

### v2.4.0

- add pytest as dependency.
- add dummy test case.

### v2.3.1

- add error logs in all endpoints.

### v2.3.0

- add authentication -> logout_apps_v0.

### v2.2.0

- add authentication -> logout_all_v0.

### v2.1.0

- github actions for CI/CD for testing and auto build and push.

### v2.0.0

- remove authentication -> logout_v0, generate_access_token_v0.

### v1.11.0

- set allow_credentials=True.

### v1.10.0

- rename remove_app_for_self_v0 to logout_v0.

### v1.9.0

- add authentication -> get_user_details_v0.

### v1.8.0

- add authentication -> update_password_v0.

### v1.7.0

- add authentication -> update_username_v0.

### v1.6.0

- add authentication -> delete_user_v0.

### v1.5.0

- add authentication -> generate_access_token_v0.

### v1.4.0

- add authentication -> logout v0.

### v1.3.2

- validate extra params in greeting -> create_greeting v0.

### v1.3.1

- accept access_token as header instead of query param in greeting -> create_greeting v0.

### v1.3.0

- add square_authentication_helper as dependency.
- replace user_id with access_token in greeting -> create_greeting.

### v1.2.0

- initialize SquareDatabaseHelper in configuration.py.
- remove app_id from greeting -> create_greeting.

### v1.1.0

- add utils -> get_app_id_v0.

### v1.0.0

- initial implementation.

## Feedback is appreciated. Thank you!
