from abc import ABC, abstractmethod
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


class BaseUser(ABC):
    """Abstract base class untuk semua user types - menerapkan Abstraksi"""
    
    def __init__(self, username, email, password):
        self._username = username  
        self._email = email        
        self._password_hash = generate_password_hash(password) 
        self._profile_image = None 
    

    @property
    def username(self):
        return self._username
    
    @property
    def email(self):
        return self._email
    
    @property
    def profile_image(self):
        return self._profile_image
    
    @username.setter
    def username(self, value):
        if len(value) < 3:
            raise ValueError("Username harus minimal 3 karakter")
        self._username = value
    
    @email.setter
    def email(self, value):
        if '@' not in value:
            raise ValueError("Email tidak valid")
        self._email = value
    
    @abstractmethod
    def get_user_type(self):
        """Return user type string"""
        pass
    
    @abstractmethod
    def get_permissions(self):
        """Return list of permissions for this user type"""
        pass
    
    def check_password(self, password):
        return check_password_hash(self._password_hash, password)
    
    def save(self):
        try:
            conn = sqlite3.connect('recipe_book.db')
            c = conn.cursor()
            c.execute('''INSERT INTO users (username, email, password_hash, user_type, profile_image)
                        VALUES (?, ?, ?, ?, ?)''',
                     (self._username, self._email, self._password_hash, 
                      self.get_user_type(), self._profile_image))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

class Creator(BaseUser):
    """Creator user yang bisa membuat dan mengelola resep"""
    
    def __init__(self, username, email, password):
        super().__init__(username, email, password)  
        self._recipe_count = 0
    
    def get_user_type(self):
        return "creator"
    
    def get_permissions(self):
        return ["create_recipe", "edit_recipe", "delete_recipe", "upload_image", "view_recipes"]
    
    def can_create_recipe(self):
        return True
    
    def can_edit_recipe(self, recipe_creator_id, current_user_id):
        return recipe_creator_id == current_user_id
    
    
    @property
    def recipe_count(self):
        return self._recipe_count
    
    def increment_recipe_count(self):
        self._recipe_count += 1

class RegularUser(BaseUser):
    """Regular user yang hanya bisa melihat dan mencari resep"""
    
    def __init__(self, username, email, password):
        super().__init__(username, email, password) 
        self._favorite_recipes = [] 
    
    def get_user_type(self):
        return "user"
    
    def get_permissions(self):
        return ["view_recipes", "search_recipes", "upload_profile_image"]
    
    
    def can_create_recipe(self):
        return False
    
    def add_favorite_recipe(self, recipe_id):
        if recipe_id not in self._favorite_recipes:
            self._favorite_recipes.append(recipe_id)
    
    def remove_favorite_recipe(self, recipe_id):
        if recipe_id in self._favorite_recipes:
            self._favorite_recipes.remove(recipe_id)
    
    
    @property
    def favorite_recipes(self):
        return self._favorite_recipes.copy()  

class UserFactory:
    """Factory class untuk membuat user objects - menerapkan Factory Pattern"""
    
    @staticmethod
    def create_user(user_type, username, email, password):
        """
        Factory method untuk membuat user berdasarkan type
        Polimorfisme - mengembalikan object yang berbeda berdasarkan input
        """
        if user_type.lower() == "creator":
            return Creator(username, email, password)
        elif user_type.lower() == "user":
            return RegularUser(username, email, password)
        else:
            raise ValueError(f"Unknown user type: {user_type}")

class UserManager:
    """Manager class untuk operasi user database"""
    
    @staticmethod
    def get_user_by_id(user_id):
        """Get user data from database by ID"""
        conn = sqlite3.connect('recipe_book.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = c.fetchone()
        conn.close()
        return user_data
    
    @staticmethod
    def get_user_by_username(username):
        """Get user data from database by username"""
        conn = sqlite3.connect('recipe_book.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_data = c.fetchone()
        conn.close()
        return user_data