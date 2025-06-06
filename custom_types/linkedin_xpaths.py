from dataclasses import dataclass


@dataclass
class LinkedinXPaths:
    login_sign_in_button: str = ""
    login_email_field: str = ""
    login_password_field: str = ""

    search_no_jobs_found_class: str = ""
    search_results_list_item: str = ""
    search_results_list_item_title: str = ""
    search_results_list_item_company: str = ""
    search_results_list_item_location: str = ""
    search_results_list_item_link: str = ""
    search_results_list_item_footer: str = ""

    search_job_description: str = ""
    search_job_hiring_team: str = ""

    search_easy_apply_button: str = ""

    easy_apply_dialog: str = ""
    easy_apply_element_common: str = ""

    easy_apply_element_textbox_label: str = ""
    easy_apply_element_textbox_label_2: str = ""
    easy_apply_element_dropdown_label: str = ""
    easy_apply_element_checkbox_label: str = ""
    easy_apply_element_radio_label: str = ""

    easy_apply_element_textbox_element: str = ""
    easy_apply_element_textbox_element_2: str = ""
    easy_apply_element_dropdown_element: str = ""
    easy_apply_element_checkbox_element: str = ""
    easy_apply_element_radio_element: str = ""

    easy_apply_element_dropdown_data: str = ""
    easy_apply_element_checkbox_data: str = ""
    easy_apply_element_radio_root: str = ""
    easy_apply_element_radio_data: str = ""

    easy_apply_element_upload_container: str = ""
    easy_apply_element_upload_input: str = ""

    easy_apply_cards_container: str = ""

    easy_apply_element_radio_find: str = ""
    easy_apply_textbox_suggestions: str = ""
    easy_apply_textbox_suggestions_data: str = ""
    easy_apply_textbox_suggestions_find: str = ""

    easy_apply_dialog_advance_button: str = ""

    easy_apply_dialog_close_button: str = ""
    easy_apply_dialog_save_alert: str = ""
    easy_apply_dialog_save_alert_discard_button: str = ""

    easy_apply_dialog_review_button: str = ""
    easy_apply_dialog_unfollow_company: str = ""
    easy_apply_dialog_submit_button: str = ""
    easy_apply_dialog_popup: str = ""
    easy_apply_dialog_popup_dismiss_button: str = ""

    @staticmethod
    def from_linkedin_xpaths_yaml(linkedin_xpaths_yaml):
        xpaths = LinkedinXPaths()
        xpaths.login_sign_in_button = linkedin_xpaths_yaml["login_sign_in_button"]
        xpaths.login_email_field = linkedin_xpaths_yaml["login_email_field"]
        xpaths.login_password_field = linkedin_xpaths_yaml["login_password_field"]

        xpaths.search_no_jobs_found_class = linkedin_xpaths_yaml["search_no_jobs_found_class"]

        xpaths.search_results_list_item = linkedin_xpaths_yaml["search_results_list_item"]
        xpaths.search_results_list_item_title = linkedin_xpaths_yaml["search_results_list_item_title"]
        xpaths.search_results_list_item_company = linkedin_xpaths_yaml["search_results_list_item_company"]
        xpaths.search_results_list_item_location = linkedin_xpaths_yaml["search_results_list_item_location"]
        xpaths.search_results_list_item_link = linkedin_xpaths_yaml["search_results_list_item_link"]
        xpaths.search_results_list_item_footer = linkedin_xpaths_yaml["search_results_list_item_footer"]

        xpaths.search_job_description = linkedin_xpaths_yaml["search_job_description"]
        xpaths.search_job_hiring_team = linkedin_xpaths_yaml["search_job_hiring_team"]

        xpaths.search_easy_apply_button = linkedin_xpaths_yaml["search_easy_apply_button"]

        xpaths.easy_apply_dialog = linkedin_xpaths_yaml["easy_apply_dialog"]
        xpaths.easy_apply_element_common = linkedin_xpaths_yaml["easy_apply_element_common"]

        xpaths.easy_apply_element_textbox_label = linkedin_xpaths_yaml["easy_apply_element_textbox_label"]
        xpaths.easy_apply_element_textbox_label_2 = linkedin_xpaths_yaml["easy_apply_element_textbox_label_2"]
        xpaths.easy_apply_element_dropdown_label = linkedin_xpaths_yaml["easy_apply_element_dropdown_label"]
        xpaths.easy_apply_element_checkbox_label = linkedin_xpaths_yaml["easy_apply_element_checkbox_label"]
        xpaths.easy_apply_element_radio_label = linkedin_xpaths_yaml["easy_apply_element_radio_label"]

        xpaths.easy_apply_element_textbox_element = linkedin_xpaths_yaml["easy_apply_element_textbox_element"]
        xpaths.easy_apply_element_textbox_element_2 = linkedin_xpaths_yaml["easy_apply_element_textbox_element_2"]
        xpaths.easy_apply_element_dropdown_element = linkedin_xpaths_yaml["easy_apply_element_dropdown_element"]
        xpaths.easy_apply_element_checkbox_element = linkedin_xpaths_yaml["easy_apply_element_checkbox_element"]
        xpaths.easy_apply_element_radio_element = linkedin_xpaths_yaml["easy_apply_element_radio_element"]

        #
        #
        xpaths.easy_apply_element_dropdown_data = linkedin_xpaths_yaml["easy_apply_element_dropdown_data"]
        xpaths.easy_apply_element_checkbox_data = linkedin_xpaths_yaml["easy_apply_element_checkbox_data"]
        xpaths.easy_apply_element_radio_root = linkedin_xpaths_yaml["easy_apply_element_radio_root"]
        xpaths.easy_apply_element_radio_data = linkedin_xpaths_yaml["easy_apply_element_radio_data"]

        xpaths.easy_apply_element_upload_container = linkedin_xpaths_yaml["easy_apply_element_upload_container"]
        xpaths.easy_apply_element_upload_input = linkedin_xpaths_yaml["easy_apply_element_upload_input"]

        xpaths.easy_apply_cards_container = linkedin_xpaths_yaml["easy_apply_cards_container"]

        xpaths.easy_apply_element_radio_find = linkedin_xpaths_yaml["easy_apply_element_radio_find"]

        xpaths.easy_apply_textbox_suggestions = linkedin_xpaths_yaml["easy_apply_textbox_suggestions"]
        xpaths.easy_apply_textbox_suggestions_data = linkedin_xpaths_yaml["easy_apply_textbox_suggestions_data"]
        xpaths.easy_apply_textbox_suggestions_find = linkedin_xpaths_yaml["easy_apply_textbox_suggestions_find"]

        xpaths.easy_apply_dialog_advance_button = linkedin_xpaths_yaml["easy_apply_dialog_advance_button"]

        xpaths.easy_apply_dialog_close_button = linkedin_xpaths_yaml["easy_apply_dialog_close_button"]
        xpaths.easy_apply_dialog_save_alert = linkedin_xpaths_yaml["easy_apply_dialog_save_alert"]
        xpaths.easy_apply_dialog_save_alert_discard_button = linkedin_xpaths_yaml["easy_apply_dialog_save_alert_discard_button"]

        xpaths.easy_apply_dialog_review_button = linkedin_xpaths_yaml["easy_apply_dialog_review_button"]
        xpaths.easy_apply_dialog_unfollow_company = linkedin_xpaths_yaml["easy_apply_dialog_unfollow_company"]
        xpaths.easy_apply_dialog_submit_button = linkedin_xpaths_yaml["easy_apply_dialog_submit_button"]
        xpaths.easy_apply_dialog_popup = linkedin_xpaths_yaml["easy_apply_dialog_popup"]
        xpaths.easy_apply_dialog_popup_dismiss_button = linkedin_xpaths_yaml["easy_apply_dialog_popup_dismiss_button"]

        return xpaths
