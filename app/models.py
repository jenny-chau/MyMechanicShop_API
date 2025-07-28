from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import List
from datetime import date

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

service_mechanics = db.Table(
    "service_mechanics",
    Base.metadata,
    db.Column('ticket_id', db.ForeignKey('service_tickets.id')),
    db.Column('mechanic_id', db.ForeignKey('mechanics.id'))
)

class Customer(Base):
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(255), nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    
    tickets: Mapped[List['ServiceTicket']] = db.relationship(back_populates='customer', cascade='all, delete') # If customer gets deleted, delete all service tickets associated with customer
    
class ServiceTicket(Base):
    __tablename__ = "service_tickets"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(255), nullable=False)
    service_date: Mapped[date] = mapped_column(nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("customers.id"))
    
    customer: Mapped['Customer'] = db.relationship(back_populates='tickets')
    mechanics: Mapped[List['Mechanic']] = db.relationship(secondary=service_mechanics, back_populates='tickets')
    items: Mapped[List['InventoryServiceTicket']] = db.relationship(back_populates="tickets", cascade='all, delete')
    
class Mechanic(Base):
    __tablename__ = "mechanics"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(255), nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    salary: Mapped[float]
    
    tickets: Mapped[List['ServiceTicket']] = db.relationship(secondary=service_mechanics, back_populates='mechanics')
    
class Inventory(Base):
    __tablename__ = 'inventory'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float]
    
    service_tickets: Mapped[List['InventoryServiceTicket']] = db.relationship(back_populates='item', cascade='all, delete') # If item is deleted, entries in the 'InventoryServiceTicket' table will be deleted too
    
class InventoryServiceTicket(Base):
    __tablename__ = 'inventory_service_ticket'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    quantity: Mapped[int] = mapped_column(nullable = False)
    inventory_id: Mapped[int] = mapped_column(db.ForeignKey("inventory.id"), nullable = False)
    service_ticket_id: Mapped[int] = mapped_column(db.ForeignKey("service_tickets.id"), nullable = False)
    
    item: Mapped['Inventory'] = db.relationship(back_populates = 'service_tickets')
    tickets: Mapped['ServiceTicket'] = db.relationship(back_populates = 'items')