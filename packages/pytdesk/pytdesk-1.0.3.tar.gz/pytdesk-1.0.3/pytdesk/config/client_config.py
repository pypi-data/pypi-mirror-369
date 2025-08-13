########################################################################################################################
# USER MODULE
########################################################################################################################
USER_FILTERS = {
    "page",
    "kw",
    "status",
    "role",
    "employment",
    "country",
    "language",
    "incorporated",
    "min_rating",
    "min_rate",
    "max_rate"
}

########################################################################################################################
# EXPENSES MODULE
########################################################################################################################
# EXPENSE MODULE
EXPENSE_FILTERS = {
    "page",
    "kw",
    "status",
    "ids",
    "task_id",
    "currency",
    "invoiced",
    "project_id",
    "min_date",
    "max_date",
    "min_amount",
    "max_amount"
}

########################################################################################################################
# OPPORTUNITIES MODULE
########################################################################################################################
OPPORTUNITY_FILTERS = {
    "page",
    "kw",
    "status",
    "ids",
    "currency"
}

CREATE_OPPORTUNITY_FIELDS = {
    "all_project_managers_can_manage_team",
    "brief",
    "budget",
    "clients",
    "custom_field_answers",
    "deadline",
    "documents",
    "external_project_id",
    "only_managers_can_view_project_team",
    "owner_id",
    "started_at",
    "tags",
    "title",
    "invitations_only",
    "max_applicants",
    "rate_guide_unit",
    "rate_guide_min",
    "rate_guide_max",
    "rate_guide_fixed"
}

UPDATE_OPPORTUNITY_FIELDS = {
    "title",
    "brief",
    "all_project_managers_can_manage_team",
    "clients",
    "custom_field_answers",
    "deadline",
    "documents",
    "external_project_id",
    "only_managers_can_view_project_team",
    "started_at",
    "tags",
    "invitations_only",
    "max_applicants",
    "rate_guide_unit",
    "rate_guide_min",
    "rate_guide_max",
    "rate_guide_fixed"
}
########################################################################################################################
# TASKS MODULE
########################################################################################################################
TASK_FILTERS = {
    "page",
    "kw",
    "status",
    "ids"
}

UPDATE_TASK_FIELDS = {
    "checklist",
    "deadline",
    "description",
    "starts_on",
    "tags",
    "title",
    "custom_field_answers",
    "skill_ids"
}

CREATE_TASK_FIELDS = {
    "deadline",
    "starts_on",
    "checklist",
    "tags",
    "custom_field_answers",
    "skill_ids",
    "owner_user_id"
}

TASK_ASSIGNMENT_FIELDS = {
    "capped_value",
    "currency",
    "legal_documents",
    "message",
    "rate_amount",
    "rate_id",
    "rate_is_capped",
    "rate_unit",
    "suggest_rate",
    "user_id"
}

########################################################################################################################
# PROJECTS MODULE
########################################################################################################################
PROJECT_FILTERS = {
    "page",
    "kw",
    "status",
    "ids",
    "currency"
}

PROJECT_WORKSHEET_FILTERS = {
    "page",
    "kw",
    "status",
    "ids",
    "task_id",
    "currency",
    "invoiced",
    "min_date",
    "max_date",
    "min_amount",
    "max_amount"
}

PROJECT_EXPENSE_FILTERS = {
    "page",
    "kw",
    "status",
    "ids",
    "task_id",
    "currency",
    "invoiced",
    "min_date",
    "max_date",
    "min_amount",
    "max_amount"
}

PROJECT_TASK_FILTERS = {
    "page",
    "kw",
    "status",
    "ids"
}

PROJECT_TEAM_FILTERS = {
    "page",
    "kw"
}

CREATE_PROJECT_FIELDS = {
    "all_project_managers_can_manage_team",
    "budget",
    "clients",
    "custom_field_answers",
    "deadline",
    "documents",
    "external_project_id",
    "only_managers_can_view_project_team",
    "tags"
}

UPDATE_PROJECT_FIELDS = {
    "all_project_managers_can_manage_team",
    "brief",
    "clients",
    "deadline",
    "documents",
    "external_project_id",
    "only_managers_can_view_project_team",
    "started_at",
    "tags",
    "title"
}

########################################################################################################################
# INVOICES MODULE
########################################################################################################################
INVOICE_FILTERS = {
    "page",
    "kw",
    "status",
    "currency",
    "project_id",
    "raised_by",
    "min_date",
    "max_date",
    "min_amount",
    "max_amount"
}

########################################################################################################################
# PROFORMA INVOICES MODULE
########################################################################################################################
PROFORMA_INVOICE_FILTERS = {
    "kw",
    "status",
    "ids",
    "task_id",
    "currency",
    "invoiced",
    "project_id",
    "min_date",
    "max_date",
    "min_amount",
    "max_amount"
}

########################################################################################################################
# WORKSHEETS MODULE
########################################################################################################################
WORKSHEET_FILTERS = {
    "page",
    "kw",
    "status",
    "ids",
    "task_id",
    "currency",
    "invoiced",
    "project_id",
    "min_date",
    "max_date",
    "min_amount",
    "max_amount",
    "user_id"
}

########################################################################################################################
########################################################################################################################
