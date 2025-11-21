"""Database models"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from app.db import Base


class Restaurant(Base):
    """Restaurant model"""
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    business_hours = Column(JSON, nullable=True)  # {"monday": "9:00-17:00", ...}
    prep_time_minutes = Column(Integer, default=30)
    is_paused = Column(Boolean, default=False)
    
    # Relationships
    menu_groups = relationship("MenuGroup", back_populates="restaurant", cascade="all, delete-orphan")
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Restaurant(id={self.id}, name={self.name})>"


class MenuGroup(Base):
    """Menu group/category model"""
    __tablename__ = "menu_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_groups")
    menu_items = relationship("MenuItem", back_populates="group")
    
    def __repr__(self):
        return f"<MenuGroup(id={self.id}, name={self.name})>"


class MenuItem(Base):
    """Menu item model"""
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("menu_groups.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)  # Price in cents
    tags = Column(JSON, default=list)  # ["vegetarian", "spicy", etc.]
    
    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_items")
    group = relationship("MenuGroup", back_populates="menu_items")
    
    def __repr__(self):
        return f"<MenuItem(id={self.id}, name={self.name}, price={self.price})>"


class ChatSession(Base):
    """Chat session model for maintaining conversation state"""
    __tablename__ = "chat_sessions"
    
    id = Column(String(255), primary_key=True)  # session_id
    owner_id = Column(Integer, nullable=False, index=True)
    current_function = Column(String(255), nullable=True)
    collected_arguments = Column(JSON, default=dict)
    missing_fields = Column(JSON, default=list)
    status = Column(String(50), default="idle")  # idle, collecting
    last_bot_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, status={self.status})>"
