# encoding: utf-8
from psi.app import const
from psi.app.service import Info
from flask_security import UserMixin
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relationship

from psi.app.models.data_security_mixin import DataSecurityMixin

db = Info.get_db()


class User(db.Model, UserMixin, DataSecurityMixin):
    from psi.app.models.role import roles_users

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    # 登录名
    login = db.Column(db.String(64), unique=True, nullable=False)
    # 显示名
    display = db.Column(db.String(255), nullable=False)
    # 邮箱
    email = db.Column(db.String(255), unique=True, nullable=False)
    # 密码
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=True)
    # 地区
    locale_id = db.Column(Integer, ForeignKey('enum_values.id'))
    locale = relationship('EnumValues', foreign_keys=[locale_id])
    # 时区
    timezone_id = db.Column(Integer, ForeignKey('enum_values.id'))
    timezone = relationship('EnumValues', foreign_keys=[timezone_id])
    # 组织
    organization_id = db.Column(Integer, ForeignKey('organization.id'))
    organization = relationship('Organization', foreign_keys=[organization_id])
    # 角色
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='joined'))

    def __unicode__(self):
        return self.display

    @staticmethod
    def locale_filter():
        from psi.app.models import EnumValues
        return EnumValues.type_filter(const.LANGUAGE_VALUES_KEY)

    @staticmethod
    def timezone_filter():
        from psi.app.models import EnumValues
        return EnumValues.type_filter(const.TIMEZONE_VALUES_KEY)
