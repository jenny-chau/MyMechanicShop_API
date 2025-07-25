# My Mechanic Shop API

## Project Overview
- Build an API for a mechanic shop to store, access, and edit customer, mechanics, and service ticket information

## Programming Languages, Frameworks, Tools
- Python
- Flask
- SQLAlchemy
- Marshmallow
- MySQL
- Postman (API testing)
- Organized with Application Factory Pattern

## Models
- Customer
    - Name
    - Email (must be unique)
    - Phone
- Service Ticket
    - VIN (string)
    - Service Date (format YYYY-MM-DD)
    - Service Description (string)
    - Customer_id (foreign key)
- Mechanic
    - Name
    - Email (must be unique)
    - Phone
    - Salary
- One-to-Many relationship between Customer and Service Ticket
- Many-to-Many relationship between Service Ticket and Mechanic (using service_mechanics association table)

## RESTful endpoints
- Customer routes
    - POST '/' : Creates a new Customer
    - GET '/' : Gets all customers
    - GET '/<customer_id>' : Gets specific customer based on id
    - PUT '/<customer_id>' : Updates customer data
    - DELETE '/<customer_id>' : Delete customer based on customer id
- Service Ticket routes
    - POST '/': Pass in all the required information to create the service_ticket.
    - PUT '/<ticket_id>/assign-mechanic/<mechanic-id>: Adds a relationship between a service ticket and the mechanics.
    - PUT '/<ticket_id>/remove-mechanic/<mechanic-id>: Removes the relationship from the service ticket and the mechanic.
    - GET '/': Retrieves all service tickets.
- Mechanic routes
    - POST '/' : Creates a new Mechanic
    - GET '/': Retrieves all Mechanics
    - PUT '/<int:id>':  Updates a specific Mechanic based on the id passed in through the url.
    - DELETE '/<int:id'>: Deletes a specific Mechanic based on the id passed in through the url.

## Getting Started
1. Clone this Github repository
2. Create a virtual environment
3. In the virtual environment terminal, `pip install -r requirements.txt`
4. Open MySQLWorkbench and add a connection. Create a database named "mymechanicshop". Edit line 2 of config.py with your MySQL connection username, password, and host (usually localhost)
5. Open Postman and import "Mechanic Shop.postman_collection.json" to view all routes. Edit host and port if needed.
6. Run "app.py"
7. Start by creating a customer and a mechanic and continue
8. Verify using MySQLWorkbench