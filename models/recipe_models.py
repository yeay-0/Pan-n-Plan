from abc import ABC, abstractmethod
import sqlite3
from datetime import datetime


class BaseContent(ABC):
    """Abstract base class untuk semua content types - menerapkan Abstraksi"""
    
    def __init__(self, title, description, creator_id):
        self._title = title          
        self._description = description  
        self._creator_id = creator_id    
        self._created_at = datetime.now()  
        self._id = None              
    
    @property
    def title(self):
        return self._title
    
    @property
    def description(self):
        return self._description
    
    @property
    def creator_id(self):
        return self._creator_id
    
    @property
    def created_at(self):
        return self._created_at
    
    @property
    def id(self):
        return self._id
    
    @title.setter
    def title(self, value):
        if not value or len(value.strip()) < 3:
            raise ValueError("Title harus minimal 3 karakter")
        self._title = value.strip()
    
    @description.setter
    def description(self, value):
        self._description = value.strip() if value else ""
   
    @abstractmethod
    def save(self):
        """Save content to database"""
        pass
    
    @abstractmethod
    def validate(self):
        """Validate content data"""
        pass

class Recipe(BaseContent):
    """Recipe class yang inherit dari BaseContent"""
    
    def __init__(self, title, description, ingredients, instructions, category, 
                 cooking_time=None, servings=None, image_path=None, creator_id=None):
        super().__init__(title, description, creator_id)  
        self._ingredients = ingredients   
        self._instructions = instructions 
        self._category = category         
        self._cooking_time = cooking_time 
        self._servings = servings         
        self._image_path = image_path     
    
    
    @property
    def ingredients(self):
        return self._ingredients
    
    @property
    def instructions(self):
        return self._instructions
    
    @property
    def category(self):
        return self._category
    
    @property
    def cooking_time(self):
        return self._cooking_time
    
    @property
    def servings(self):
        return self._servings
    
    @property
    def image_path(self):
        return self._image_path
    
    @ingredients.setter
    def ingredients(self, value):
        if not value or len(value.strip()) < 5:
            raise ValueError("Ingredients harus minimal 5 karakter")
        self._ingredients = value.strip()
    
    @instructions.setter
    def instructions(self, value):
        if not value or len(value.strip()) < 10:
            raise ValueError("Instructions harus minimal 10 karakter")
        self._instructions = value.strip()
    
    @category.setter
    def category(self, value):
        valid_categories = ['makanan_utama', 'makanan_pembuka', 'makanan_penutup', 
                           'minuman', 'cemilan', 'lainnya']
        if value not in valid_categories:
            raise ValueError(f"Category harus salah satu dari: {', '.join(valid_categories)}")
        self._category = value
    
    def validate(self):
        """Validate recipe data"""
        if not self._title or len(self._title.strip()) < 3:
            return False, "Title harus minimal 3 karakter"
        
        if not self._ingredients or len(self._ingredients.strip()) < 5:
            return False, "Ingredients harus minimal 5 karakter"
        
        if not self._instructions or len(self._instructions.strip()) < 10:
            return False, "Instructions harus minimal 10 karakter"
        
        if not self._category:
            return False, "Category harus dipilih"
        
        return True, "Valid"
    
    def save(self):
        """Save recipe to database"""
        is_valid, message = self.validate()
        if not is_valid:
            return False
        
        try:
            conn = sqlite3.connect('recipe_book.db')
            c = conn.cursor()
            c.execute('''INSERT INTO recipes 
                        (title, description, ingredients, instructions, category, 
                         cooking_time, servings, image_path, creator_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (self._title, self._description, self._ingredients, 
                      self._instructions, self._category, self._cooking_time,
                      self._servings, self._image_path, self._creator_id))
            
            self._id = c.lastrowid
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving recipe: {e}")
            return False

    def get_formatted_ingredients(self):
        """Return ingredients as list"""
        return [ingredient.strip() for ingredient in self._ingredients.split('\n') if ingredient.strip()]
    
    def get_formatted_instructions(self):
        """Return instructions as list"""
        return [instruction.strip() for instruction in self._instructions.split('\n') if instruction.strip()]
    
    def update(self, **kwargs):
        """Update recipe fields"""
        for key, value in kwargs.items():
            if hasattr(self, f"_{key}"):
                setattr(self, f"_{key}", value)

class SearchStrategy(ABC):
    """Abstract strategy untuk pencarian resep"""
    
    @abstractmethod
    def search(self, query, recipes):
        pass

class NameSearchStrategy(SearchStrategy):
    """Strategy untuk pencarian berdasarkan nama"""
    
    def search(self, query, recipes):
        if not query:
            return recipes
        
        query_lower = query.lower()
        return [recipe for recipe in recipes 
                if query_lower in recipe[1].lower()]  

class CategorySearchStrategy(SearchStrategy):
    """Strategy untuk pencarian berdasarkan kategori"""
    
    def search(self, category, recipes):
        if not category or category == 'all':
            return recipes
        
        return [recipe for recipe in recipes 
                if recipe[5] == category] 

class CombinedSearchStrategy(SearchStrategy):
    """Strategy untuk pencarian kombinasi nama dan kategori"""
    
    def search(self, query, recipes, category=None):
 
        if category and category != 'all':
            recipes = [recipe for recipe in recipes if recipe[5] == category]
        
        if query:
            query_lower = query.lower()
            recipes = [recipe for recipe in recipes 
                      if query_lower in recipe[1].lower()]
        
        return recipes

class RecipeManager:
    """Manager class untuk operasi recipe database - menerapkan berbagai design patterns"""
    
    def __init__(self):
        self._search_strategy = CombinedSearchStrategy() 
    
    def set_search_strategy(self, strategy: SearchStrategy):
        """Set search strategy - Strategy Pattern"""
        self._search_strategy = strategy
    
    def get_all_recipes(self):
        """Get all recipes from database"""
        conn = sqlite3.connect('recipe_book.db')
        c = conn.cursor()
        c.execute('''SELECT r.*, u.username 
                    FROM recipes r 
                    JOIN users u ON r.creator_id = u.id 
                    ORDER BY r.created_at DESC''')
        recipes = c.fetchall()
        conn.close()
        return recipes
    
    def get_recipe_by_id(self, recipe_id):
        """Get specific recipe by ID"""
        conn = sqlite3.connect('recipe_book.db')
        c = conn.cursor()
        c.execute('''SELECT r.*, u.username 
                    FROM recipes r 
                    JOIN users u ON r.creator_id = u.id 
                    WHERE r.id = ?''', (recipe_id,))
        recipe = c.fetchone()
        conn.close()
        return recipe
    
    def get_recipes_by_creator(self, creator_id):
        """Get all recipes by specific creator"""
        conn = sqlite3.connect('recipe_book.db')
        c = conn.cursor()
        c.execute('''SELECT r.*, u.username 
                    FROM recipes r 
                    JOIN users u ON r.creator_id = u.id 
                    WHERE r.creator_id = ? 
                    ORDER BY r.created_at DESC''', (creator_id,))
        recipes = c.fetchall()
        conn.close()
        return recipes
    
    def search_recipes(self, query=None, category=None):
        """Search recipes using current strategy"""
        all_recipes = self.get_all_recipes()
        return self._search_strategy.search(query, all_recipes, category)
    
    def get_recipes_by_category(self, category):
        """Get recipes by specific category"""
        conn = sqlite3.connect('recipe_book.db')
        c = conn.cursor()
        c.execute('''SELECT r.*, u.username 
                    FROM recipes r 
                    JOIN users u ON r.creator_id = u.id 
                    WHERE r.category = ? 
                    ORDER BY r.created_at DESC''', (category,))
        recipes = c.fetchall()
        conn.close()
        return recipes
    
    def delete_recipe(self, recipe_id, user_id):
        """Delete recipe (only by creator)"""
        recipe = self.get_recipe_by_id(recipe_id)
        if not recipe or recipe[9] != user_id: 
            return False
        
        conn = sqlite3.connect('recipe_book.db')
        c = conn.cursor()
        c.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))
        conn.commit()
        conn.close()
        return True
    
    def get_popular_categories(self):
        """Get categories with recipe count"""
        conn = sqlite3.connect('recipe_book.db')
        c = conn.cursor()
        c.execute('''SELECT category, COUNT(*) as count 
                    FROM recipes 
                    GROUP BY category 
                    ORDER BY count DESC''')
        categories = c.fetchall()
        conn.close()
        return categories
class RecipeStatistics:
    """Singleton class untuk statistik resep"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RecipeStatistics, cls).__new__(cls)
        return cls._instance
    
    def get_total_recipes(self):
        """Get total number of recipes"""
        conn = sqlite3.connect('recipe_book.db')
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM recipes')
        count = c.fetchone()[0]
        conn.close()
        return count
    
    def get_total_creators(self):
        """Get total number of creators"""
        conn = sqlite3.connect('recipe_book.db')
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM users WHERE user_type = "creator"')
        count = c.fetchone()[0]
        conn.close()
        return count