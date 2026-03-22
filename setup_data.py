#!/usr/bin/env python3
"""
Setup script to add sample data to the fast food bot database
"""

import sqlite3
from database import Database

def add_sample_data():
    """Add sample categories and products"""
    db = Database()
    
    # Sample products
    sample_products = [
        # Hot Dogs
        ("Classic Hot Dog", "Go'shtli sosiska, sous", 18000, "https://example.com/hotdog1.jpg", 1),
        ("Cheese Hot Dog", "Pishloq qo'shilgan hot dog", 22000, "https://example.com/hotdog2.jpg", 1),
        ("Spicy Hot Dog", "O'tkir sosiska, maxsus sous", 25000, "https://example.com/hotdog3.jpg", 1),
        
        # Pizza
        ("Margherita", "Pishloq, pomidor sousi, rayhon", 45000, "https://example.com/pizza1.jpg", 2),
        ("Pepperoni", "Pishloq, pepperoni, pomidor sousi", 55000, "https://example.com/pizza2.jpg", 2),
        ("Hawaiian", "Pishloq, ananas, shinka", 50000, "https://example.com/pizza3.jpg", 2),
        ("Four Cheese", "To'rt xil pishloq", 60000, "https://example.com/pizza4.jpg", 2),
        
        # Lavash
        ("Chicken Lavash", "Tovuq go'shti, sabzavotlar, sous", 35000, "https://example.com/lavash1.jpg", 3),
        ("Beef Lavash", "Mol go'shti, piyoz, pomidor", 40000, "https://example.com/lavash2.jpg", 3),
        ("Vegetarian Lavash", "Sabzavotlar, pishloq, sous", 30000, "https://example.com/lavash3.jpg", 3),
        
        # Drinks
        ("Coca-Cola", "0.5L", 8000, "https://example.com/cola.jpg", 4),
        ("Fanta", "0.5L", 8000, "https://example.com/fanta.jpg", 4),
        ("Sprite", "0.5L", 8000, "https://example.com/sprite.jpg", 4),
        ("Fresh Juice", "Orange/Apple/Banana", 12000, "https://example.com/juice.jpg", 4),
        ("Mineral Water", "1L", 5000, "https://example.com/water.jpg", 4),
    ]
    
    print("Adding sample products...")
    for name, description, price, image_url, category_id in sample_products:
        success = db.add_product(name, description, price, image_url, category_id)
        if success:
            print(f"✅ Added: {name}")
        else:
            print(f"❌ Failed to add: {name}")
    
    print("\nSample data setup complete!")

def show_database_stats():
    """Show current database statistics"""
    db = Database()
    
    categories = db.get_categories()
    products = db.get_all_products()
    
    print(f"\n📊 Database Statistics:")
    print(f"📂 Categories: {len(categories)}")
    print(f"🍔 Products: {len(products)}")
    
    print(f"\n📂 Categories:")
    for cat_id, cat_name in categories:
        product_count = len(db.get_products_by_category(cat_id))
        print(f"  {cat_name}: {product_count} products")

if __name__ == "__main__":
    print("🍔 Fast Food Bot - Data Setup")
    print("=" * 40)
    
    # Show current stats
    show_database_stats()
    
    # Add sample data automatically
    print("\nAdding sample data...")
    add_sample_data()
    show_database_stats()
