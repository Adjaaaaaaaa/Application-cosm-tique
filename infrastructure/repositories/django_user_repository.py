"""
Django ORM implementation of UserRepository.

This repository implements the UserRepository interface using Django ORM.
"""

import logging
from typing import Optional, List
from django.contrib.auth.models import User as DjangoUser

from core.entities.user import User
from core.exceptions import UserNotFoundError
from interfaces.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class DjangoUserRepository(UserRepository):
    """
    Django ORM implementation of UserRepository.
    
    This repository provides concrete implementation of user data access
    operations using Django's ORM.
    """
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID using Django ORM.
        
        Args:
            user_id: User identifier
            
        Returns:
            User entity or None if not found
        """
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            return self._to_domain_entity(django_user)
        except DjangoUser.DoesNotExist:
            logger.warning(f"User with ID {user_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user {user_id}: {str(e)}")
            raise UserNotFoundError(f"Error retrieving user {user_id}: {str(e)}")
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username using Django ORM.
        
        Args:
            username: Username
            
        Returns:
            User entity or None if not found
        """
        try:
            django_user = DjangoUser.objects.get(username=username)
            return self._to_domain_entity(django_user)
        except DjangoUser.DoesNotExist:
            logger.warning(f"User with username {username} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user {username}: {str(e)}")
            raise UserNotFoundError(f"Error retrieving user {username}: {str(e)}")
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address using Django ORM.
        
        Args:
            email: Email address
            
        Returns:
            User entity or None if not found
        """
        try:
            django_user = DjangoUser.objects.get(email=email)
            return self._to_domain_entity(django_user)
        except DjangoUser.DoesNotExist:
            logger.warning(f"User with email {email} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving user {email}: {str(e)}")
            raise UserNotFoundError(f"Error retrieving user {email}: {str(e)}")
    
    def save(self, user: User) -> User:
        """
        Save user entity using Django ORM.
        
        Args:
            user: User entity to save
            
        Returns:
            Saved user entity with updated ID if new
        """
        try:
            if user.id and user.id > 0:
                # Update existing user
                django_user = DjangoUser.objects.get(id=user.id)
                django_user.username = user.username
                django_user.email = user.email
                django_user.first_name = user.first_name
                django_user.last_name = user.last_name
                django_user.is_active = user.is_active
                django_user.is_staff = user.is_staff
                django_user.is_superuser = user.is_superuser
                django_user.save()
                logger.info(f"Updated user {user.id}")
            else:
                # Create new user
                django_user = DjangoUser.objects.create(
                    username=user.username,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    is_active=user.is_active,
                    is_staff=user.is_staff,
                    is_superuser=user.is_superuser
                )
                logger.info(f"Created new user {django_user.id}")
            
            return self._to_domain_entity(django_user)
            
        except Exception as e:
            logger.error(f"Error saving user: {str(e)}")
            raise UserNotFoundError(f"Error saving user: {str(e)}")
    
    def delete(self, user_id: int) -> bool:
        """
        Delete user by ID using Django ORM.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deleted, False if not found
        """
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            django_user.delete()
            logger.info(f"Deleted user {user_id}")
            return True
        except DjangoUser.DoesNotExist:
            logger.warning(f"User {user_id} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            raise UserNotFoundError(f"Error deleting user {user_id}: {str(e)}")
    
    def exists(self, user_id: int) -> bool:
        """
        Check if user exists using Django ORM.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if user exists, False otherwise
        """
        return DjangoUser.objects.filter(id=user_id).exists()
    
    def get_all_active_users(self) -> List[User]:
        """
        Get all active users using Django ORM.
        
        Returns:
            List of active user entities
        """
        try:
            django_users = DjangoUser.objects.filter(is_active=True)
            return [self._to_domain_entity(user) for user in django_users]
        except Exception as e:
            logger.error(f"Error retrieving active users: {str(e)}")
            raise UserNotFoundError(f"Error retrieving active users: {str(e)}")
    
    def _to_domain_entity(self, django_user: DjangoUser) -> User:
        """
        Convert Django User model to domain entity.
        
        Args:
            django_user: Django User model instance
            
        Returns:
            User domain entity
        """
        return User(
            user_id=django_user.id,
            username=django_user.username,
            email=django_user.email,
            first_name=django_user.first_name,
            last_name=django_user.last_name,
            is_active=django_user.is_active,
            is_staff=django_user.is_staff,
            is_superuser=django_user.is_superuser
        )
