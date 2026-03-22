import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime

class Database:
    def __init__(self, db_path: str = "fastfood.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                image_url TEXT,
                category_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_name TEXT,
                phone TEXT,
                address TEXT,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                total_price REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # Insert default categories if they don't exist
        default_categories = [
            ("🌮 Hot Dogs",),
            ("🍕 Pizza",),
            ("🌯 Lavash",),
            ("🥤 Ichimlik",)
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO categories (name) VALUES (?)
        ''', default_categories)
        
        conn.commit()
        conn.close()
    
    def get_categories(self) -> List[Tuple[int, str]]:
        """Get all categories"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY name")
        categories = cursor.fetchall()
        conn.close()
        return categories
    
    def get_products_by_category(self, category_id: int) -> List[Tuple[int, str, str, float, str]]:
        """Get products by category"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, description, price, image_url 
            FROM products 
            WHERE category_id = ? 
            ORDER BY name
        ''', (category_id,))
        products = cursor.fetchall()
        conn.close()
        return products
    
    def get_product(self, product_id: int) -> Optional[Tuple[int, str, str, float, str, int]]:
        """Get single product details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, description, price, image_url, category_id 
            FROM products 
            WHERE id = ?
        ''', (product_id,))
        product = cursor.fetchone()
        conn.close()
        return product
    
    def add_category(self, name: str) -> bool:
        """Add new category"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def add_product(self, name: str, description: str, price: float, 
                   image_url: str, category_id: int) -> bool:
        """Add new product"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, description, price, image_url, category_id) 
                VALUES (?, ?, ?, ?, ?)
            ''', (name, description, price, image_url, category_id))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def update_product(self, product_id: int, name: str = None, 
                      description: str = None, price: float = None, 
                      image_url: str = None, category_id: int = None) -> bool:
        """Update product"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build dynamic update query
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if price is not None:
                updates.append("price = ?")
                params.append(price)
            if image_url is not None:
                updates.append("image_url = ?")
                params.append(image_url)
            if category_id is not None:
                updates.append("category_id = ?")
                params.append(category_id)
            
            if updates:
                query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
                params.append(product_id)
                cursor.execute(query, params)
                conn.commit()
                conn.close()
                return True
            return False
        except:
            return False
    
    def delete_product(self, product_id: int) -> bool:
        """Delete product"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def create_order(self, user_id: int, user_name: str, phone: str, 
                    address: str, product_id: int, quantity: int, 
                    total_price: float) -> bool:
        """Create new order"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders 
                (user_id, user_name, phone, address, product_id, quantity, total_price) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, user_name, phone, address, product_id, quantity, total_price))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_pending_orders(self) -> List[Tuple[int, int, str, str, str, str, int, float, str]]:
        """Get all pending orders"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.id, o.user_id, o.user_name, o.phone, o.address, 
                   p.name, o.quantity, o.total_price, o.created_at
            FROM orders o
            JOIN products p ON o.product_id = p.id
            WHERE o.status = 'pending'
            ORDER BY o.created_at DESC
        ''')
        orders = cursor.fetchall()
        conn.close()
        return orders
    
    def update_order_status(self, order_id: int, status: str) -> bool:
        """Update order status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_all_products(self) -> List[Tuple[int, str, str, float, str, str]]:
        """Get all products with category names"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.name, p.description, p.price, p.image_url, c.name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            ORDER BY c.name, p.name
        ''')
        products = cursor.fetchall()
        conn.close()
        return products
    
    def get_category_by_id(self, category_id: int) -> Optional[Tuple[int, str]]:
        """Get category by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories WHERE id = ?", (category_id,))
        category = cursor.fetchone()
        conn.close()
        return category
    
    def delete_category(self, category_id: int) -> bool:
        """Delete category (only if no products in it)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if category has products
            cursor.execute("SELECT COUNT(*) FROM products WHERE category_id = ?", (category_id,))
            product_count = cursor.fetchone()[0]
            
            if product_count > 0:
                conn.close()
                return False
            
            # Delete category
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_product_by_name(self, name: str) -> Optional[Tuple[int, str, str, float, str, int]]:
        """Get product by name"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, price, image_url, category_id FROM products WHERE name = ?", (name,))
        product = cursor.fetchone()
        conn.close()
        return product
