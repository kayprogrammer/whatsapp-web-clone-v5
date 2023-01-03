from fastapi import Depends
from sqlalchemy.orm import Session
from . hashers import Hasher
from . validators import *
from . models import Timezone

class UserManager(object):
    @classmethod
    def create_user(cls, db: Session, **kwargs):
        name = kwargs.get('name')
        email = kwargs.get('email')
        phone = kwargs.get('phone')
        password = kwargs.get('password')
        tz = kwargs.get('tz')

        if not name:
            raise ValueError("Users must submit a name")

        if not tz:
            raise ValueError("Users must submit a timezone")
        
        validate_email(email)
        validate_phone(phone)
        validate_password(password)
            
        timezone = Timezone.query.filter_by(name=tz).first()
        if not timezone:
            raise ValueError('Invalid Timezone')

        kwargs.pop('tz', None)
        kwargs['tz_id'] = timezone.pkid
        kwargs['is_admin'] = False
        hashed_password = Hasher.get_password_hash(password)
        kwargs['password'] = hashed_password
        obj = cls(**kwargs)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @classmethod
    def create_superuser(cls, db: Session, **kwargs):
        name = kwargs.get('name')
        email = kwargs.get('email')
        phone = kwargs.get('phone')
        password = kwargs.get('password')
        tz = kwargs.get('tz')

        if not name:
            raise ValueError("Users must submit a name")

        if not tz:
            raise ValueError("Users must submit a timezone")
        
        validate_email(email)
        validate_phone(phone)
        validate_password(password)
            
        timezone = Timezone.query.filter_by(name=tz).first()
        if not timezone:
            raise ValueError('Invalid Timezone')

        kwargs.pop('tz', None)
        kwargs['tz_id'] = timezone.pkid
        kwargs['is_admin'] = True
        kwargs['password'] = Hasher.get_password_hash(password)

        obj = cls(**kwargs)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

class OtpManager(object):
    @classmethod
    def get_or_create(cls, db: Session, **kwargs):
        print(kwargs)
        instance = cls.query.filter_by(**kwargs).first()

        if instance:
            return instance
        else:
            instance = cls(**kwargs)
            db.add(instance)
            db.commit()
            return instance