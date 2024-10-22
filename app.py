from flask import Flask, request, jsonify, render_template, redirect, url_for
import mysql.connector
import mysql.connector.errorcode
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Set up database credentials using environment variables
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user=DB_USER,
            password=DB_PASSWORD,
            database='warehouse'
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Authentication error: Invalid username or password")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(f'Database connection error: {err}')
        return None

# Home page
@app.route('/')
def index():
    return redirect(url_for('view_index'))

# Dashboard
@app.route('/index', methods=['GET'])
def view_index():
    return render_template('index.html')

# **Customers**

# View all customers
@app.route('/customers', methods=['GET'])
def view_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM customers')
    customers_list = cursor.fetchall()
    conn.close()
    return render_template('customers.html', customers=customers_list)

# Add a new customer
@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form.get('name')
        contact_info = request.form.get('contact_info')

        if not name or not contact_info:
            return jsonify({'error': 'Invalid customer data'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO customers (name, contact_info) VALUES (%s, %s)', (name, contact_info))
        conn.commit()
        conn.close()
        return redirect(url_for('view_customers'))
    else:
        return render_template('add_customer.html')

# Edit an existing customer
@app.route('/edit_customer/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form.get('name')
        contact_info = request.form.get('contact_info')

        if not name or not contact_info:
            return jsonify({'error': 'Invalid customer data'}), 400

        cursor.execute('UPDATE customers SET name = %s, contact_info = %s WHERE id = %s', (name, contact_info, customer_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_customers'))
    else:
        cursor.execute('SELECT * FROM customers WHERE id = %s', (customer_id,))
        customer = cursor.fetchone()
        conn.close()
        if customer is None:
            return jsonify({'error': 'Customer not found'}), 404
        return render_template('edit_customer.html', customer=customer)

# Delete a customer
@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM customers WHERE id = %s', (customer_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_customers'))

# **Products**

# View all products
@app.route('/products', methods=['GET'])
def view_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT products.id, products.name, categories.name AS category, products.quantity, products.unit_price, suppliers.name AS supplier
        FROM products
        LEFT JOIN categories ON products.category_id = categories.id
        LEFT JOIN suppliers ON products.supplier_id = suppliers.id
    ''')
    products_list = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=products_list)

# Add a new product
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        quantity = request.form.get('quantity')
        unit_price = request.form.get('unit_price')
        supplier_id = request.form.get('supplier_id')

        if not name or not category_id or not quantity or not unit_price or not supplier_id:
            return jsonify({'error': 'Invalid product data'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, category_id, quantity, unit_price, supplier_id) VALUES (%s, %s, %s, %s, %s)',
                       (name, category_id, quantity, unit_price, supplier_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_products'))
    else:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM categories')
        categories = cursor.fetchall()
        cursor.execute('SELECT * FROM suppliers')
        suppliers = cursor.fetchall()
        conn.close()
        return render_template('add_product.html', categories=categories, suppliers=suppliers)

# Edit an existing product
@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        quantity = request.form.get('quantity')
        unit_price = request.form.get('unit_price')
        supplier_id = request.form.get('supplier_id')

        if not name or not category_id or not quantity or not unit_price or not supplier_id:
            return jsonify({'error': 'Invalid product data'}), 400

        cursor.execute('''
            UPDATE products
            SET name = %s, category_id = %s, quantity = %s, unit_price = %s, supplier_id = %s
            WHERE id = %s
        ''', (name, category_id, quantity, unit_price, supplier_id, product_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_products'))
    else:
        cursor.execute('SELECT * FROM products WHERE id = %s', (product_id,))
        product = cursor.fetchone()
        cursor.execute('SELECT * FROM categories')
        categories = cursor.fetchall()
        cursor.execute('SELECT * FROM suppliers')
        suppliers = cursor.fetchall()
        conn.close()
        if product is None:
            return jsonify({'error': 'Product not found'}), 404
        return render_template('edit_product.html', product=product, categories=categories, suppliers=suppliers)

# Delete a product
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = %s', (product_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_products'))

# **Categories**

# View all categories
@app.route('/categories', methods=['GET'])
def view_categories():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM categories')
    categories_list = cursor.fetchall()
    conn.close()
    return render_template('categories.html', categories=categories_list)

# Add a new category
@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            return jsonify({'error': 'Invalid category data'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO categories (name) VALUES (%s)', (name,))
        conn.commit()
        conn.close()
        return redirect(url_for('view_categories'))
    else:
        return render_template('add_category.html')

# Edit an existing category
@app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            return jsonify({'error': 'Invalid category data'}), 400

        cursor.execute('UPDATE categories SET name = %s WHERE id = %s', (name, category_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_categories'))
    else:
        cursor.execute('SELECT * FROM categories WHERE id = %s', (category_id,))
        category = cursor.fetchone()
        conn.close()
        if category is None:
            return jsonify({'error': 'Category not found'}), 404
        return render_template('edit_category.html', category=category)

# Delete a category
@app.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM categories WHERE id = %s', (category_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_categories'))

# **Suppliers**

# View all suppliers
@app.route('/suppliers', methods=['GET'])
def view_suppliers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM suppliers')
    suppliers_list = cursor.fetchall()
    conn.close()
    return render_template('suppliers.html', suppliers=suppliers_list)

# Add a new supplier
@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        name = request.form.get('name')
        contact_info = request.form.get('contact_info')

        if not name or not contact_info:
            return jsonify({'error': 'Invalid supplier data'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO suppliers (name, contact_info) VALUES (%s, %s)', (name, contact_info))
        conn.commit()
        conn.close()
        return redirect(url_for('view_suppliers'))
    else:
        return render_template('add_supplier.html')

# Edit an existing supplier
@app.route('/edit_supplier/<int:supplier_id>', methods=['GET', 'POST'])
def edit_supplier(supplier_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form.get('name')
        contact_info = request.form.get('contact_info')

        if not name or not contact_info:
            return jsonify({'error': 'Invalid supplier data'}), 400

        cursor.execute('UPDATE suppliers SET name = %s, contact_info = %s WHERE id = %s', (name, contact_info, supplier_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_suppliers'))
    else:
        cursor.execute('SELECT * FROM suppliers WHERE id = %s', (supplier_id,))
        supplier = cursor.fetchone()
        conn.close()
        if supplier is None:
            return jsonify({'error': 'Supplier not found'}), 404
        return render_template('edit_supplier.html', supplier=supplier)

# Delete a supplier
@app.route('/delete_supplier/<int:supplier_id>', methods=['POST'])
def delete_supplier(supplier_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM suppliers WHERE id = %s', (supplier_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_suppliers'))

# **Warehouses**

# View all warehouses
@app.route('/warehouses', methods=['GET'])
def view_warehouses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM warehouses')
    warehouses_list = cursor.fetchall()
    conn.close()
    return render_template('warehouses.html', warehouses=warehouses_list)

# Add a new warehouse
@app.route('/add_warehouse', methods=['GET', 'POST'])
def add_warehouse():
    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            return jsonify({'error': 'Invalid warehouse data'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO warehouses (name) VALUES (%s)', (name,))
        conn.commit()
        conn.close()
        return redirect(url_for('view_warehouses'))
    else:
        return render_template('add_warehouse.html')

# Edit an existing warehouse
@app.route('/edit_warehouse/<int:warehouse_id>', methods=['GET', 'POST'])
def edit_warehouse(warehouse_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form.get('name')

        if not name:
            return jsonify({'error': 'Invalid warehouse data'}), 400

        cursor.execute('UPDATE warehouses SET name = %s WHERE id = %s', (name, warehouse_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_warehouses'))
    else:
        cursor.execute('SELECT * FROM warehouses WHERE id = %s', (warehouse_id,))
        warehouse = cursor.fetchone()
        conn.close()
        if warehouse is None:
            return jsonify({'error': 'Warehouse not found'}), 404
        return render_template('edit_warehouse.html', warehouse=warehouse)

# Delete a warehouse
@app.route('/delete_warehouse/<int:warehouse_id>', methods=['POST'])
def delete_warehouse(warehouse_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM warehouses WHERE id = %s', (warehouse_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_warehouses'))

# **Transactions**

# View all transactions
@app.route('/transactions', methods=['GET'])
def view_transactions():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT transactions.id, products.name AS product, transactions.transaction_type, transactions.quantity, transactions.date
        FROM transactions
        LEFT JOIN products ON transactions.product_id = products.id
    ''')
    transactions_list = cursor.fetchall()
    conn.close()
    return render_template('transactions.html', transactions=transactions_list)

# Add a new transaction
@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        transaction_type = request.form.get('transaction_type')
        quantity = int(request.form.get('quantity'))

        if not product_id or not transaction_type or not quantity:
            return jsonify({'error': 'Invalid transaction data'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO transactions (product_id, transaction_type, quantity) VALUES (%s, %s, %s)',
                       (product_id, transaction_type, quantity))
        if transaction_type == 'in':
            cursor.execute('UPDATE products SET quantity = quantity + %s WHERE id = %s', (quantity, product_id))
        elif transaction_type == 'out':
            cursor.execute('UPDATE products SET quantity = quantity - %s WHERE id = %s', (quantity, product_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_transactions'))
    else:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        conn.close()
        return render_template('add_transaction.html', products=products)

# Edit an existing transaction
@app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        transaction_type = request.form.get('transaction_type')
        quantity = int(request.form.get('quantity'))

        if not product_id or not transaction_type or not quantity:
            return jsonify({'error': 'Invalid transaction data'}), 400

        # Retrieve the old transaction
        cursor.execute('SELECT * FROM transactions WHERE id = %s', (transaction_id,))
        old_transaction = cursor.fetchone()
        old_quantity = old_transaction['quantity']
        old_product_id = old_transaction['product_id']
        old_transaction_type = old_transaction['transaction_type']

        # Revert the product quantity based on the old transaction
        if old_transaction_type == 'in':
            cursor.execute('UPDATE products SET quantity = quantity - %s WHERE id = %s', (old_quantity, old_product_id))
        elif old_transaction_type == 'out':
            cursor.execute('UPDATE products SET quantity = quantity + %s WHERE id = %s', (old_quantity, old_product_id))

        # Apply the new transaction quantity
        if transaction_type == 'in':
            cursor.execute('UPDATE products SET quantity = quantity + %s WHERE id = %s', (quantity, product_id))
        elif transaction_type == 'out':
            cursor.execute('UPDATE products SET quantity = quantity - %s WHERE id = %s', (quantity, product_id))

        # Update the transaction
        cursor.execute('''
            UPDATE transactions
            SET product_id = %s, transaction_type = %s, quantity = %s
            WHERE id = %s
        ''', (product_id, transaction_type, quantity, transaction_id))

        conn.commit()
        conn.close()
        return redirect(url_for('view_transactions'))
    else:
        cursor.execute('SELECT * FROM transactions WHERE id = %s', (transaction_id,))
        transaction = cursor.fetchone()
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        conn.close()
        if transaction is None:
            return jsonify({'error': 'Transaction not found'}), 404
        return render_template('edit_transaction.html', transaction=transaction, products=products)

# Delete a transaction
@app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Retrieve the transaction to adjust product quantity
    cursor.execute('SELECT * FROM transactions WHERE id = %s', (transaction_id,))
    transaction = cursor.fetchone()
    if transaction is not None:
        product_id = transaction['product_id']
        transaction_type = transaction['transaction_type']
        quantity = transaction['quantity']
        # Revert the product quantity
        if transaction_type == 'in':
            cursor.execute('UPDATE products SET quantity = quantity - %s WHERE id = %s', (quantity, product_id))
        elif transaction_type == 'out':
            cursor.execute('UPDATE products SET quantity = quantity + %s WHERE id = %s', (quantity, product_id))
    # Delete the transaction
    cursor.execute('DELETE FROM transactions WHERE id = %s', (transaction_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_transactions'))

# **Sales Orders**

# View all sales orders
@app.route('/sales_orders', methods=['GET'])
def view_sales_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT so.id, c.name AS customer_name, so.order_date, so.status, so.total_amount
        FROM sales_orders so
        JOIN customers c ON so.customer_id = c.id
    ''')
    sales_orders = cursor.fetchall()
    conn.close()
    return render_template('sales_orders.html', sales_orders=sales_orders)

# Add a new sales order
@app.route('/add_sales_order', methods=['GET', 'POST'])
def add_sales_order():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')

        if not customer_id or not product_ids or not quantities:
            return jsonify({'error': 'Invalid sales order data'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Create a new sales order
        cursor.execute('INSERT INTO sales_orders (customer_id) VALUES (%s)', (customer_id,))
        sales_order_id = cursor.lastrowid

        total_amount = 0

        # Add order items
        for product_id, quantity in zip(product_ids, quantities):
            cursor.execute('SELECT unit_price FROM products WHERE id = %s', (product_id,))
            unit_price = cursor.fetchone()[0]
            quantity = int(quantity)
            total_price = unit_price * quantity
            total_amount += total_price

            cursor.execute('''
                INSERT INTO sales_order_items (sales_order_id, product_id, quantity, unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s)
            ''', (sales_order_id, product_id, quantity, unit_price, total_price))

            # Update product quantity
            cursor.execute('UPDATE products SET quantity = quantity - %s WHERE id = %s', (quantity, product_id))

        # Update the total amount of the sales order
        cursor.execute('UPDATE sales_orders SET total_amount = %s WHERE id = %s', (total_amount, sales_order_id))

        conn.commit()
        conn.close()
        return redirect(url_for('view_sales_orders'))
    else:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM customers')
        customers = cursor.fetchall()
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        conn.close()
        return render_template('add_sales_order.html', customers=customers, products=products)

# Edit an existing sales order
@app.route('/edit_sales_order/<int:sales_order_id>', methods=['GET', 'POST'])
def edit_sales_order(sales_order_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        status = request.form.get('status')
        cursor.execute('UPDATE sales_orders SET status = %s WHERE id = %s', (status, sales_order_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_sales_orders'))
    else:
        # Retrieve sales order details
        cursor.execute('''
            SELECT so.*, c.name AS customer_name
            FROM sales_orders so
            JOIN customers c ON so.customer_id = c.id
            WHERE so.id = %s
        ''', (sales_order_id,))
        sales_order = cursor.fetchone()

        # Retrieve order items
        cursor.execute('''
            SELECT soi.*, p.name AS product_name
            FROM sales_order_items soi
            JOIN products p ON soi.product_id = p.id
            WHERE soi.sales_order_id = %s
        ''', (sales_order_id,))
        order_items = cursor.fetchall()

        conn.close()
        return render_template('edit_sales_order.html', sales_order=sales_order, order_items=order_items)

# Delete a sales order
@app.route('/delete_sales_order/<int:sales_order_id>', methods=['POST'])
def delete_sales_order(sales_order_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Revert product quantities
    cursor.execute('SELECT product_id, quantity FROM sales_order_items WHERE sales_order_id = %s', (sales_order_id,))
    items = cursor.fetchall()
    for item in items:
        cursor.execute('UPDATE products SET quantity = quantity + %s WHERE id = %s', (item[1], item[0]))

    # Delete order items
    cursor.execute('DELETE FROM sales_order_items WHERE sales_order_id = %s', (sales_order_id,))
    # Delete the sales order
    cursor.execute('DELETE FROM sales_orders WHERE id = %s', (sales_order_id,))

    conn.commit()
    conn.close()
    return redirect(url_for('view_sales_orders'))

# View sales order details
@app.route('/sales_order/<int:sales_order_id>', methods=['GET'])
def view_sales_order(sales_order_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Retrieve sales order details
    cursor.execute('''
        SELECT so.*, c.name AS customer_name
        FROM sales_orders so
        JOIN customers c ON so.customer_id = c.id
        WHERE so.id = %s
    ''', (sales_order_id,))
    sales_order = cursor.fetchone()

    # Check if the order exists
    if not sales_order:
        conn.close()
        return "Order not found", 404

    # Retrieve order items
    cursor.execute('''
        SELECT soi.*, p.name AS product_name
        FROM sales_order_items soi
        JOIN products p ON soi.product_id = p.id
        WHERE soi.sales_order_id = %s
    ''', (sales_order_id,))
    order_items = cursor.fetchall()

    conn.close()
    return render_template('view_sales_order.html', sales_order=sales_order, order_items=order_items)

# **Purchase Orders**

# View all purchase orders
@app.route('/purchase_orders', methods=['GET'])
def view_purchase_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT po.id, s.name AS supplier_name, po.order_date, po.status, po.total_amount
        FROM purchase_orders po
        JOIN suppliers s ON po.supplier_id = s.id
    ''')
    purchase_orders = cursor.fetchall()
    conn.close()
    return render_template('purchase_orders.html', purchase_orders=purchase_orders)

# Add a new purchase order
@app.route('/add_purchase_order', methods=['GET', 'POST'])
def add_purchase_order():
    if request.method == 'POST':
        supplier_id = request.form.get('supplier_id')
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')

        if not supplier_id or not product_ids or not quantities:
            return jsonify({'error': 'Invalid purchase order data'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Create a new purchase order
        cursor.execute('INSERT INTO purchase_orders (supplier_id) VALUES (%s)', (supplier_id,))
        purchase_order_id = cursor.lastrowid

        total_amount = 0

        # Add order items
        for product_id, quantity in zip(product_ids, quantities):
            cursor.execute('SELECT unit_price FROM products WHERE id = %s', (product_id,))
            unit_price = cursor.fetchone()[0]
            quantity = int(quantity)
            total_price = unit_price * quantity
            total_amount += total_price

            cursor.execute('''
                INSERT INTO purchase_order_items (purchase_order_id, product_id, quantity, unit_price, total_price)
                VALUES (%s, %s, %s, %s, %s)
            ''', (purchase_order_id, product_id, quantity, unit_price, total_price))

            # Update product quantity
            cursor.execute('UPDATE products SET quantity = quantity + %s WHERE id = %s', (quantity, product_id))

        # Update the total amount of the purchase order
        cursor.execute('UPDATE purchase_orders SET total_amount = %s WHERE id = %s', (total_amount, purchase_order_id))

        conn.commit()
        conn.close()
        return redirect(url_for('view_purchase_orders'))
    else:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM suppliers')
        suppliers = cursor.fetchall()
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        conn.close()
        return render_template('add_purchase_order.html', suppliers=suppliers, products=products)

# Edit an existing purchase order
@app.route('/edit_purchase_order/<int:purchase_order_id>', methods=['GET', 'POST'])
def edit_purchase_order(purchase_order_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        status = request.form.get('status')
        cursor.execute('UPDATE purchase_orders SET status = %s WHERE id = %s', (status, purchase_order_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_purchase_orders'))
    else:
        # Retrieve purchase order details
        cursor.execute('''
            SELECT po.*, s.name AS supplier_name
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            WHERE po.id = %s
        ''', (purchase_order_id,))
        purchase_order = cursor.fetchone()

        # Retrieve order items
        cursor.execute('''
            SELECT poi.*, p.name AS product_name
            FROM purchase_order_items poi
            JOIN products p ON poi.product_id = p.id
            WHERE poi.purchase_order_id = %s
        ''', (purchase_order_id,))
        order_items = cursor.fetchall()

        conn.close()
        return render_template('edit_purchase_order.html', purchase_order=purchase_order, order_items=order_items)

# Delete a purchase order
@app.route('/delete_purchase_order/<int:purchase_order_id>', methods=['POST'])
def delete_purchase_order(purchase_order_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Revert product quantities
    cursor.execute('SELECT product_id, quantity FROM purchase_order_items WHERE purchase_order_id = %s', (purchase_order_id,))
    items = cursor.fetchall()
    for item in items:
        cursor.execute('UPDATE products SET quantity = quantity - %s WHERE id = %s', (item[1], item[0]))

    # Delete order items
    cursor.execute('DELETE FROM purchase_order_items WHERE purchase_order_id = %s', (purchase_order_id,))
    # Delete the purchase order
    cursor.execute('DELETE FROM purchase_orders WHERE id = %s', (purchase_order_id,))

    conn.commit()
    conn.close()
    return redirect(url_for('view_purchase_orders'))

# View purchase order details
@app.route('/purchase_order/<int:purchase_order_id>', methods=['GET'])
def view_purchase_order(purchase_order_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Retrieve purchase order details
    cursor.execute('''
        SELECT po.*, s.name AS supplier_name
        FROM purchase_orders po
        JOIN suppliers s ON po.supplier_id = s.id
        WHERE po.id = %s
    ''', (purchase_order_id,))
    purchase_order = cursor.fetchone()

    # Check if the order exists
    if not purchase_order:
        conn.close()
        return "Order not found", 404

    # Retrieve order items
    cursor.execute('''
        SELECT poi.*, p.name AS product_name
        FROM purchase_order_items poi
        JOIN products p ON poi.product_id = p.id
        WHERE poi.purchase_order_id = %s
    ''', (purchase_order_id,))
    order_items = cursor.fetchall()

    conn.close()
    return render_template('view_purchase_order.html', purchase_order=purchase_order, order_items=order_items)

if __name__ == '__main__':
    app.run(debug=True)
