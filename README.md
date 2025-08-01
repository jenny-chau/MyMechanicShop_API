# My Mechanic Shop API

## Project Overview
- Build an API for a mechanic shop to store, access, and edit customer, mechanics, and service ticket information

## Programming Languages, Frameworks, Tools
- Python
- Flask (limiter, caching, blueprints)
- SQLAlchemy
- Marshmallow
- MySQL
- Postman (API testing)
- JWT tokens using python-jose package
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
- Inventory
    - Item name
    - Item price
- One-to-Many relationship between Customer and Service Ticket
- Many-to-Many relationship between Service Ticket and Mechanic (using service_mechanics association table)
- Many-to-Many relationship betwen Inventory items and Service ticket using a model that also stores quantity of item

## RESTful endpoints
- Customer routes
    - POST '/customers/login' : Customer login
    - POST '/customers/' : Creates a new Customer
    - GET '/customers/' : Gets all customers (can be paginated using query parameters)
    - GET '/customers/<customer_id>' : Gets specific customer based on id
    - PUT '/customers/' : Updates customer data (login required)
    - DELETE '/customers/' : Delete customer based on customer id (login required)
    - GET '/customers/my-tickets' : Gets all service tickets associated with customer (login required)
- Service Ticket routes
    - POST '/serviceticket/': Pass in all the required information to create the service_ticket.
    - PUT '/serviceticket/<ticket_id>/assign-mechanic: Adds a relationship between a service ticket and the mechanics. (mechanic login required)
    - PUT '/serviceticket/<ticket_id>/remove-mechanic: Removes the relationship from the service ticket and the mechanic. (mechanic login required)
    - GET '/serviceticket/': Retrieves all service tickets.
    - PUT '/serviceticket/<ticket_id>/edit' : Add/removes mechanics from service ticket. Takes in 'remove_ids', and 'add_ids'. Logged in mechanic may add/remove other mechanics by their ids passed in. (mechanic login required)
    - PUT '/serviceticket/add_items' : Add item to service ticket (mechanic login required)
- Mechanic routes
    - POST '/mechanics/login' : Mechanic login
    - POST '/mechanics/' : Creates a new Mechanic
    - GET '/mechanics/': Retrieves all Mechanics (mechanic data excludes password and salary)
    - PUT '/mechanics/':  Update Mechanic
    - DELETE '/mechanics/': Delete mechanic
    - GET '/mechanics/ranked' : rank mechanics based on most service tickets worked on (mechanic data excludes password and salary)
- Inventory routes
    - POST '/inventory/' : create item (mechanic login required)
    - GET '/inventory/' : get all items
    - GET '/inventory/<item_id> : get item by id
    - PUT '/inventory/<item_id> : update item (mechanic login required)
    - DELETE '/inventory/<item_id>' : delete item (and all instances of this item in service tickets) (mechanic login required)

## Getting Started
1. Clone this Github repository
2. Create a virtual environment
3. In the virtual environment terminal, `pip install -r requirements.txt`
4. Open MySQLWorkbench and add a connection. Create a database named "mymechanicshop". Edit line 2 of config.py with your MySQL connection username, password, and host (usually localhost)
5. Open Postman and import "Mechanic Shop.postman_collection.json" to view all routes. Edit host and port if needed.
6. Run "app.py"
7. Start by creating a customer and a mechanic and continue
8. Verify using MySQLWorkbench