# encoding=utf-8
from psi.app.service import Info
from flask_security import RoleMixin
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref

from psi.app.models.data_security_mixin import DataSecurityMixin

db = Info.get_db()

# 角色与用户的关系表
roles_users = db.Table('roles_users',
                       db.Column('id', db.Integer(), primary_key=True),
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin, DataSecurityMixin):
    """角色模型

    使用角色模型作为权限模型
    """
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    # 父级角色
    parent_id = db.Column(Integer, ForeignKey('role.id'))
    parent = relationship('Role', remote_side=id, backref=backref('sub_roles', lazy='joined'))
    # 系统角色
    is_system = db.Column(db.Boolean, default=False, nullable=False)

    def __unicode__(self):
        return self.name

    @hybrid_property
    def shadow_is_system(self):
        return self.is_system

    @shadow_is_system.setter
    def shadow_is_system(self, val):
        pass

    @hybrid_property
    def shadow_name(self):
        return self.name

    @shadow_name.setter
    def shadow_name(self, val):
        pass

    def __str__(self):
        return self.__unicode__()

    def can_delete(self):
        return len(self.sub_roles) == 0 or self.is_system == False
