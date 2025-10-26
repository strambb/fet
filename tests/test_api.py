def test_app_alive(testclient):
    response = testclient.get("/healthz")
    assert response.status_code == 200


class TestUserAPI:
    def test_can_get_token(self):
        raise NotImplementedError

    def test_user_is_admin(self):
        raise NotImplementedError

    def test_user_is_approver(self):
        raise NotImplementedError

    def test_user_is_authenticated(self):
        raise NotImplementedError

    def test_user_has_org(self):
        raise NotImplementedError


class TestExpenseAPI:
    def test_can_create_expense(self):
        raise NotImplementedError

    def test_can_submit_expense(self):
        raise NotImplementedError

    def test_can_get_my_expenses(self):
        raise NotImplementedError

    def test_can_approve_expense(self):
        raise NotImplementedError

    def test_can_reject_expense(self):
        raise NotImplementedError

    def test_can_update_expense(self):
        raise NotImplementedError

    def test_can_delete_expense(self):
        raise NotImplementedError

    def test_can_get_expense_by_id(self, add_fake_org, add_fake_user, add_fake_expense, testclient):
        org = add_fake_org(name = "fake_org")
        submitter = add_fake_user(org_id = org["id"])      
        expense = add_expense(
            submitter_id = submitter["id"],
            organization_id = org["id"]
        )
        token = 
        response = testclient.get(expense)

    def test_can_get_expenses_by_status(self):
        raise NotImplementedError

    def test_can_get_pending_expenses(self):
        raise NotImplementedError

    def test_can_get_approved_expenses(self):
        raise NotImplementedError

    def test_can_get_rejected_expenses(self):
        raise NotImplementedError

    def test_cannot_approve_own_expense(self):
        raise NotImplementedError

    def test_cannot_submit_without_required_fields(self):
        raise NotImplementedError

    def test_cannot_approve_without_permission(self):
        raise NotImplementedError

    def test_cannot_update_submitted_expense(self):
        raise NotImplementedError

    def test_cannot_delete_approved_expense(self):
        raise NotImplementedError
