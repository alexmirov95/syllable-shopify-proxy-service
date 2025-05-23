"""app.py

Syllable Shopify Proxy Service.
Serves as proxy layer between Syllable Agents and Shopify APIs.

Endpoints:
    - GET /shopify/order-by-number
    - GET /shopify/order-by-confirmation-number-and-email
    - GET /shopify/products
    - GET /shopify/get-product-url

To run the application locally:
    1. Install dependencies
        $ pip install -r requirements.txt
    2. Run the application
        $ python app.py
    3. Use curl or Postman to test the endpoints.
"""
import logging
from flask import Flask, request, jsonify

from shopify import GetOrders, GetProducts, GetCustomerID, GetOrdersForCustomerId

logging.basicConfig(
    level=logging.INFO
)
app = Flask(__name__)


@app.route('/')
def health_check():
    app.logger.info('Service up.')
    return "Ok.", 200


@app.route('/shopify/order-by-number', methods=['GET'])
def shopify_order_by_number():
    """Get a shopify order by order number.

    Headers:
        X-Shopify-Access-Token (str):  Shopify access token.
    
    Query Parameters:
        store_name (str):  Unique Shopify store ID string.
        api_version (str, optional):  Shopify API version. 
        order_number (str):  Unique Shopify order number.
    
    Returns:
        A json object with field `order` that contains the order info.
    """
    shopify_access_token = request.headers.get('X-Shopify-Access-Token')
    if not shopify_access_token:
        return jsonify({"error": "Missing or invalid Shopify token in request headers"}), 400
    store_name = request.args.get('store_name')
    shopify_api_version = request.args.get('api_version')
    order_number = request.args.get('order_number')
    try:
        orders = GetOrders(store_name, shopify_access_token, shopify_api_version, 
                           order_number=order_number)
        app.logger.info(f"Num orders found for {order_number}: {len(orders)}")

        order = orders[0] if orders else f'No orders with order number {order_number} found.'
        return jsonify({
            'order': order,
        }), 200
    
    except ValueError as e:
        app.logger.error(f"ValueError: {e}")
        return jsonify({"error": f"Invalid parameter provided. {e}"}), 400

    except Exception as e:
        app.logger.error("Error retrieving orders by order number")
        return jsonify({"error": "An error occurred while retrieving orders."}), 500


@app.route('/shopify/order-by-confirmation-number-and-email', methods=['GET'])
def shopify_order_by_confirmation_number_and_email():
    """Get list of Shopify orders using order confirmation number and/or user email address.
    
    Headers:
        X-Shopify-Access-Token (str):  Shopify access token.

    Query Parameters:
        store_name (str):  Unique Shopify store ID string.
        api_version (str, optional):  Shopify API version. 
        confirmation_number (str, optional):  Shopify order confirmation number (non unique).
        email (str, optional):  User email address associated with an order. 
    
    Returns:
        A json object with field `order` that is a list of matched order search results.
    """
    shopify_access_token = request.headers.get('X-Shopify-Access-Token')
    if not shopify_access_token:
        return jsonify({"error": "Missing or invalid Shopify token in request headers"}), 400
    
    store_name = request.args.get('store_name')
    shopify_api_version = request.args.get('api_version')
    confirmation_number = request.args.get('confirmation_number')
    email = request.args.get('email')
    
    try:
        customer_id = GetCustomerID(store_name, email, shopify_access_token, shopify_api_version)
        if not customer_id:
            return jsonify({
            'Error': f'Invalid Email. Customer not found with email {email}',
        }), 400

        orders = GetOrdersForCustomerId(store_name, customer_id, shopify_access_token, shopify_api_version)
        app.logger.info(f"Num orders found for {email}: {len(orders)}")
        
        order = f'No orders for {email} with confirmation number {confirmation_number} found.'
        # Match the order by confirmation number
        for o in orders:
            if o['confirmationNumber'] == confirmation_number:
                order = o
                break

        return jsonify({
            'order': order,
        }), 200

    except ValueError as e:
        app.logger.error(f"ValueError: {e}")
        return jsonify({"error": f"Invalid parameter provided. {e}"}), 400
            
    except Exception as e:
        app.logger.error(f"Error retrieving orders by email and confirmation number: {e}")
        return jsonify({"error": "An error occurred while retrieving orders."}), 500


@app.route('/shopify/products', methods=['GET'])
def get_shopify_products():
    """Get a list of products from a Shopify store by product_id or search key word.

    Headers:
        X-Shopify-Access-Token (str):  Shopify access token.

    Query Parameters:
        store_name (str):  Unique Shopify store ID string.
        api_version (str, optional):  Shopify API version. 
        product_id (str, optional):  Unique Shopify store item product ID.
        product_name (str, optional):  Keyword to search for in the product title or
            description in a Shopify store.

    Returns:
        A json object with field `products` that is a list of matched products from the 
        Shopifiy store.
    """
    shopify_access_token = request.headers.get('X-Shopify-Access-Token')
    if not shopify_access_token:
        return jsonify({"error": "Missing or invalid Shopify token in request headers"}), 400
    
    store_name = request.args.get('store_name')
    shopify_api_version = request.args.get('api_version')
    product_id = request.args.get('product_id')
    product_name = request.args.get('product_name')
    
    try:
        # Search for products by product_id or product_name
        products = GetProducts(store_name, shopify_access_token, shopify_api_version,
                           product_id=product_id, product_name=product_name)

        # If no results by title search, search product description
        if not products and product_name:
            app.logger.info(f"No products found by title search, searching by description: {product_name}")
            products = GetProducts(store_name, shopify_access_token, shopify_api_version,
                           description=product_name)

        if len(products) <= 0:
            products = "No products found."
        app.logger.info(f"Num orders found for product_id: {product_id} product_name: {product_name}: {len(products)}")

        return jsonify({
            'products': products,
        }), 200
        
    except ValueError as e:
        app.logger.error(f"ValueError: {e}")
        return jsonify({"error": f"Invalid parameter provided. {e}"}), 400
            
    except Exception as e:
        app.logger.error(f"Error retrieving orders by product_id or product_name: {e}")
        return jsonify({"error": "An error occurred while retrieving products."}), 500


@app.route('/shopify/get-product-url', methods=['GET'])
def get_product_url():
    """Returns the url for a Shopify store product.

    Query Parameters:
        store_name (str):  Unique Shopify store ID string.
        product_handle (str):  Shopify product handle. Example: "polo-shirt-1"

    Returns (str):
        Complete URL to the product in the Shopify store.
    """
    store_name = request.args.get('store_name')
    product_handle = request.args.get('product_handle')

    if not store_name or not product_handle:
        return jsonify({
            'error': 'Missing store_name or product_handle'
        }), 400

    return jsonify({
        'product_url': f'https://{store_name}.myshopify.com/products/{product_handle}',
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
