from pytest import fixture

from cfripper.rules.privilege_escalation import PrivilegeEscalationRule
from tests.utils import get_cfmodel_from


@fixture()
def valid_role_inline_policy():
    return get_cfmodel_from("rules/PrivilegeEscalationRule/valid_role_inline_policy.json").resolve()


@fixture()
def privilege_escalation_role_cf():
    return get_cfmodel_from("rules/PrivilegeEscalationRule/privilege_escalation_role.yaml").resolve()


@fixture()
def valid_privilege_escalation_on_s3_bucket_policy():
    return get_cfmodel_from("rules/PrivilegeEscalationRule/privilege_escalation_s3_bucket_policy.yaml").resolve()


def test_valid_role_inline_policy(valid_role_inline_policy):
    rule = PrivilegeEscalationRule(None)
    result = rule.invoke(valid_role_inline_policy)

    assert not result.valid
    assert len(result.failed_rules) == 1
    assert len(result.failed_monitored_rules) == 0
    assert result.failed_rules[0].rule == "PrivilegeEscalationRule"
    assert (
        result.failed_rules[0].reason
        == "PolicyA has blacklisted IAM actions: ['iam:AddUserToGroup', 'iam:CreatePolicy']"
    )


def test_privilege_escalation_using_role(privilege_escalation_role_cf):
    rule = PrivilegeEscalationRule(None)
    result = rule.invoke(privilege_escalation_role_cf)

    assert not result.valid
    assert len(result.failed_rules) == 1
    assert len(result.failed_monitored_rules) == 0
    assert result.failed_rules[0].rule == "PrivilegeEscalationRule"
    assert (
        result.failed_rules[0].reason
        == "PrivilegeInjectorRole has blacklisted IAM actions: ['iam:UpdateAssumeRolePolicy']"
    )


def test_valid_privilege_escalation_on_s3_bucket_policy(valid_privilege_escalation_on_s3_bucket_policy):
    rule = PrivilegeEscalationRule(None)
    result = rule.invoke(valid_privilege_escalation_on_s3_bucket_policy)
    assert result.valid


def test_rule_supports_filter_config(privilege_escalation_role_cf, default_allow_all_config):
    rule = PrivilegeEscalationRule(default_allow_all_config)
    result = rule.invoke(privilege_escalation_role_cf)
    assert result.valid
