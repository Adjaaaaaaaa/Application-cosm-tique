"""
Django ORM implementation of ProfileRepository.

This repository implements the ProfileRepository interface using Django ORM.
"""

import logging
from typing import Optional, List
from django.contrib.auth.models import User as DjangoUser
from apps.accounts.models import UserProfile as DjangoUserProfile

from core.entities.user import User
from core.entities.profile import UserProfile
from core.value_objects.skin_type import SkinType
from core.value_objects.age_range import AgeRange
from core.exceptions import ProfileNotFoundError
from interfaces.repositories.profile_repository import ProfileRepository

logger = logging.getLogger(__name__)


class DjangoProfileRepository(ProfileRepository):
    """
    Django ORM implementation of ProfileRepository.
    
    This repository provides concrete implementation of user profile data access
    operations using Django's ORM.
    """
    
    def get_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        """
        Get user profile by user ID using Django ORM.
        
        Args:
            user_id: User identifier
            
        Returns:
            UserProfile entity or None if not found
        """
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            django_profile = DjangoUserProfile.objects.get(user=django_user)
            return self._to_domain_entity(django_profile)
        except DjangoUser.DoesNotExist:
            logger.warning(f"User with ID {user_id} not found")
            return None
        except DjangoUserProfile.DoesNotExist:
            logger.warning(f"Profile for user {user_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving profile for user {user_id}: {str(e)}")
            raise ProfileNotFoundError(f"Error retrieving profile for user {user_id}: {str(e)}")
    
    def get_by_user(self, user: User) -> Optional[UserProfile]:
        """
        Get user profile by user entity using Django ORM.
        
        Args:
            user: User entity
            
        Returns:
            UserProfile entity or None if not found
        """
        return self.get_by_user_id(user.id)
    
    def save(self, profile: UserProfile) -> UserProfile:
        """
        Save user profile entity using Django ORM.
        
        Args:
            profile: UserProfile entity to save
            
        Returns:
            Saved UserProfile entity
        """
        try:
            django_user = DjangoUser.objects.get(id=profile.user.id)
            
            if profile.id and profile.id > 0:
                # Update existing profile
                django_profile = DjangoUserProfile.objects.get(id=profile.id)
                self._update_django_profile(django_profile, profile)
                django_profile.save()
                logger.info(f"Updated profile {profile.id}")
            else:
                # Create new profile
                django_profile = DjangoUserProfile.objects.create(
                    user=django_user,
                    subscription_type=profile.subscription_type,
                    skin_type=profile.skin_type,
                    age_range=profile.age_range,
                    skin_concerns=profile.skin_concerns,
                    dermatological_conditions=profile.dermatological_conditions,
                    dermatological_other=profile.dermatological_other,
                    allergies=profile.allergies,
                    allergies_other=profile.allergies_other,
                    product_style=profile.product_style,
                    routine_frequency=profile.routine_frequency,
                    objectives=profile.objectives,
                    budget=profile.budget
                )
                logger.info(f"Created new profile {django_profile.id}")
            
            return self._to_domain_entity(django_profile)
            
        except DjangoUser.DoesNotExist:
            logger.error(f"User {profile.user.id} not found for profile save")
            raise ProfileNotFoundError(f"User {profile.user.id} not found")
        except Exception as e:
            logger.error(f"Error saving profile: {str(e)}")
            raise ProfileNotFoundError(f"Error saving profile: {str(e)}")
    
    def delete(self, user_id: int) -> bool:
        """
        Delete user profile by user ID using Django ORM.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deleted, False if not found
        """
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            django_profile = DjangoUserProfile.objects.get(user=django_user)
            django_profile.delete()
            logger.info(f"Deleted profile for user {user_id}")
            return True
        except DjangoUser.DoesNotExist:
            logger.warning(f"User {user_id} not found for profile deletion")
            return False
        except DjangoUserProfile.DoesNotExist:
            logger.warning(f"Profile for user {user_id} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Error deleting profile for user {user_id}: {str(e)}")
            raise ProfileNotFoundError(f"Error deleting profile for user {user_id}: {str(e)}")
    
    def exists(self, user_id: int) -> bool:
        """
        Check if user profile exists using Django ORM.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if profile exists, False otherwise
        """
        try:
            django_user = DjangoUser.objects.get(id=user_id)
            return DjangoUserProfile.objects.filter(user=django_user).exists()
        except DjangoUser.DoesNotExist:
            return False
    
    def get_premium_users(self) -> List[UserProfile]:
        """
        Get all users with premium or pro subscription using Django ORM.
        
        Returns:
            List of premium user profiles
        """
        try:
            django_profiles = DjangoUserProfile.objects.filter(
                subscription_type__in=['premium', 'pro']
            )
            return [self._to_domain_entity(profile) for profile in django_profiles]
        except Exception as e:
            logger.error(f"Error retrieving premium users: {str(e)}")
            raise ProfileNotFoundError(f"Error retrieving premium users: {str(e)}")
    
    def get_users_by_skin_type(self, skin_type: str) -> List[UserProfile]:
        """
        Get users by skin type using Django ORM.
        
        Args:
            skin_type: Skin type to filter by
            
        Returns:
            List of user profiles with specified skin type
        """
        try:
            django_profiles = DjangoUserProfile.objects.filter(skin_type=skin_type)
            return [self._to_domain_entity(profile) for profile in django_profiles]
        except Exception as e:
            logger.error(f"Error retrieving users by skin type {skin_type}: {str(e)}")
            raise ProfileNotFoundError(f"Error retrieving users by skin type {skin_type}: {str(e)}")
    
    def get_users_by_age_range(self, age_range: str) -> List[UserProfile]:
        """
        Get users by age range using Django ORM.
        
        Args:
            age_range: Age range to filter by
            
        Returns:
            List of user profiles with specified age range
        """
        try:
            django_profiles = DjangoUserProfile.objects.filter(age_range=age_range)
            return [self._to_domain_entity(profile) for profile in django_profiles]
        except Exception as e:
            logger.error(f"Error retrieving users by age range {age_range}: {str(e)}")
            raise ProfileNotFoundError(f"Error retrieving users by age range {age_range}: {str(e)}")
    
    def _to_domain_entity(self, django_profile: DjangoUserProfile) -> UserProfile:
        """
        Convert Django UserProfile model to domain entity.
        
        Args:
            django_profile: Django UserProfile model instance
            
        Returns:
            UserProfile domain entity
        """
        # Convert Django User to domain User
        user = User(
            user_id=django_profile.user.id,
            username=django_profile.user.username,
            email=django_profile.user.email,
            first_name=django_profile.user.first_name,
            last_name=django_profile.user.last_name,
            is_active=django_profile.user.is_active,
            is_staff=django_profile.user.is_staff,
            is_superuser=django_profile.user.is_superuser
        )
        
        # Create UserProfile domain entity
        return UserProfile(
            user=user,
            subscription_type=django_profile.subscription_type,
            skin_type=django_profile.skin_type,
            age_range=django_profile.age_range,
            skin_concerns=django_profile.get_skin_concerns_list(),
            dermatological_conditions=django_profile.get_dermatological_conditions_list(),
            dermatological_other=django_profile.dermatological_other,
            allergies=django_profile.get_allergies_list(),
            allergies_other=django_profile.allergies_other,
            product_style=django_profile.product_style,
            routine_frequency=django_profile.routine_frequency,
            objectives=django_profile.get_objectives_list(),
            budget=django_profile.budget
        )
    
    def _update_django_profile(self, django_profile: DjangoUserProfile, profile: UserProfile) -> None:
        """
        Update Django profile model with domain entity data.
        
        Args:
            django_profile: Django UserProfile model instance
            profile: UserProfile domain entity
        """
        django_profile.subscription_type = profile.subscription_type
        django_profile.skin_type = profile.skin_type
        django_profile.age_range = profile.age_range
        django_profile.set_skin_concerns_list(profile.skin_concerns)
        django_profile.set_dermatological_conditions_list(profile.dermatological_conditions)
        django_profile.dermatological_other = profile.dermatological_other
        django_profile.set_allergies_list(profile.allergies)
        django_profile.allergies_other = profile.allergies_other
        django_profile.product_style = profile.product_style
        django_profile.routine_frequency = profile.routine_frequency
        django_profile.set_objectives_list(profile.objectives)
        django_profile.budget = profile.budget
