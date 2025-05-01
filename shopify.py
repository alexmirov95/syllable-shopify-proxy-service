"""shopify.py

Functions to query Shopify GraphQL API.
"""

import requests, logging

NUM_ORDERS_TO_RETURN = 50 # Number of orders to return from Shopify.
NUM_PRODUCTS_TO_RETURN = 20 # Number of produts to return from Shopify.
SHOPIFY_API_VERSION = '2025-04' # Default Shopify API version.

def GetOrders(store_name: str, shopify_access_token: str, 
              api_verison: str = SHOPIFY_API_VERSION, order_number: str = None, 
              email: str = None, confirmation_number: str = None) -> list:
    """Gets orders from Shopify by order_number, user email, and/or confirmation_number.

    Args:
        store_name (str): Unique Shopify store ID string.
        shopify_access_token (str): Shopify API access token.
        api_version (str, optional):  Shopify API version.
        order_number (str, optional):  Unique Shopify order number.
        email (str, optional):  User email address associated with an order. 
        confirmation_number (str, optional):  Shopify order confirmation number (non unique).

    returns (list):
        List of Shopify orders matching search criteria, descending by order creation time.
    """
    api_verison = api_verison or SHOPIFY_API_VERSION
    url = f"https://{store_name}.myshopify.com/admin/api/{api_verison}/graphql.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": shopify_access_token,
    }
    query = """
        fragment Money on MoneyBag {
            presentmentMoney {
                amount
                currencyCode
            }
        }
        fragment Return on Return {
            name
            id
            status
            decline {
                note
                reason
            }
            totalQuantity
            returnLineItems (first: 10) {
                nodes {
                    id
                    quantity
                    refundableQuantity
                    refundedQuantity
                    returnReason 
                    returnReasonNote
                }
            }
        }

        query GetOrderByOrderNumber ($query: String!, $num_orders: Int!) {
            orders(first: $num_orders, query: $query, sortKey: CREATED_AT, reverse: true) {
                nodes {
                    id
                    orderNumber: name
                    confirmationNumber
                    displayFulfillmentStatus
                    displayFinancialStatus
                    fullyPaid
                    createdAt
                    requiresShipping
                    processedAt
                    updatedAt
                    cancelReason
                    closed
                    confirmed
                    currencyCode
                    note
                    totalWeightGrams: totalWeight
                    currentTotalPriceSet {...Money}
                    currentShippingPriceSet {...Money}
                    shippingLine {
                        title
                        carrierIdentifier
                        code
                        currentDiscountedPriceSet {...Money}
                        deliveryCategory
                    }
                    fulfillments (first: 10) {
                        createdAt
                        deliveredAt
                        displayStatus
                        estimatedDeliveryAt
                        inTransitAt
                        name
                        status
                        requiresShipping
                        trackingInfo {
                            company
                            number
                            url
                        }
                    }
                    refundable
                    refunds {
                        return {...Return}
                        refundLineItems (first: 10) {
                            nodes {
                                id
                                quantity
                                priceSet {...Money}
                                subtotalSet {...Money}
                                totalTaxSet {...Money}
                            }
                        }
                        createdAt
                        note
                        id
                    }
                    returns (first: 10) {
                        nodes {...Return}
                    }
                }
            }
        }
    """

    # Construct query string based on input parameters
    query_string = None
    if order_number is not None:
        query_string = f'name:{order_number}'
    elif email and confirmation_number:
        query_string = f'email:{email}'
    else:
        raise ValueError("Either order_number or both email and confirmation number must be provided.")

    try:
        # Get recent orders by query
        response = requests.post(url, headers=headers, json={ 
            'query': query,  
            'variables': { 
                'query': query_string, 
                'num_orders': NUM_ORDERS_TO_RETURN 
            }
        })
        response.raise_for_status()
        result = response.json()
        orders = result.get('data', {}).get('orders', {}).get('nodes', [])
        return orders
    
    except Exception as e:
        logging.error(e)
        raise Exception(f"Shopify order search error: {e}")
    

def GetOrdersForCustomerId(store_name: str, customer_id: str, shopify_access_token: str, 
              api_verison: str = SHOPIFY_API_VERSION) -> list:
    """Gets orders from Shopify placed by a customer.

    Args:
        store_name (str): Unique Shopify store ID string.
        shopify_access_token (str): Shopify API access token.
        api_version (str, optional):  Shopify API version.
        customer_id (str, optional):  Unique customer ID.

    returns (list):
        List of Shopify orders matching search criteria, descending by order creation time.
    """
    api_verison = api_verison or SHOPIFY_API_VERSION
    url = f"https://{store_name}.myshopify.com/admin/api/{api_verison}/graphql.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": shopify_access_token,
    }
    query = """
        fragment Money on MoneyBag {
            presentmentMoney {
                amount
                currencyCode
            }
        }
        fragment Return on Return {
            name
            id
            status
            decline {
                note
                reason
            }
            totalQuantity
            returnLineItems (first: 10) {
                nodes {
                    id
                    quantity
                    refundableQuantity
                    refundedQuantity
                    returnReason 
                    returnReasonNote
                }
            }
        }

        query GetOrderByOrderCustomer ($customer_id: ID!, $num_orders: Int!) {
            customer(id: $customer_id) {
            orders(first: $num_orders, sortKey: CREATED_AT, reverse: true) {
                nodes {
                    id
                    orderNumber: name
                    confirmationNumber
                    displayFulfillmentStatus
                    displayFinancialStatus
                    fullyPaid
                    createdAt
                    requiresShipping
                    processedAt
                    updatedAt
                    cancelReason
                    closed
                    confirmed
                    currencyCode
                    note
                    totalWeightGrams: totalWeight
                    currentTotalPriceSet {...Money}
                    currentShippingPriceSet {...Money}
                    shippingLine {
                        title
                        carrierIdentifier
                        code
                        currentDiscountedPriceSet {...Money}
                        deliveryCategory
                    }
                    fulfillments (first: 10) {
                        createdAt
                        deliveredAt
                        displayStatus
                        estimatedDeliveryAt
                        inTransitAt
                        name
                        status
                        requiresShipping
                        trackingInfo {
                            company
                            number
                            url
                        }
                    }
                    refundable
                    refunds {
                        return {...Return}
                        refundLineItems (first: 10) {
                            nodes {
                                id
                                quantity
                                priceSet {...Money}
                                subtotalSet {...Money}
                                totalTaxSet {...Money}
                            }
                        }
                        createdAt
                        note
                        id
                    }
                    returns (first: 10) {
                        nodes {...Return}
                    }
                }
            }
            }
        }
    """

    # Construct query string based on input parameters
    if not customer_id:
        raise ValueError("Either order_number or both email and confirmation number must be provided.")
    
    try:
        # Get recent orders by query
        response = requests.post(url, headers=headers, json={ 
            'query': query,  
            'variables': { 
                'customer_id': customer_id, 
                'num_orders': NUM_ORDERS_TO_RETURN 
            }
        })
        response.raise_for_status()
        result = response.json()
        orders = result.get('data', {}).get('customer', {}).get('orders', {}).get('nodes', [])
        return orders
    
    except Exception as e:
        logging.error(e)
        raise Exception(f"Shopify order search error: {e}")



def GetCustomerID(store_name: str, email: str, shopify_access_token: str, 
                api_verison: str = SHOPIFY_API_VERSION) -> str:
    """Get unique customer ID for a Shopify customer by their email address.
    
    Args:
        store_name (str): Unique Shopify store ID string.
        shopify_access_token (str): Shopify API access token.
        api_version (str, optional):  Shopify API version.
        email (str):  Email address associated with a customer.

    returns (str):
        Customer ID string if found, else returns None.

    """
    api_verison = api_verison or SHOPIFY_API_VERSION
    url = f"https://{store_name}.myshopify.com/admin/api/{api_verison}/graphql.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": shopify_access_token,
    }
    query = """
        query FindCustomerByEmail ($query: String!) {
        customers (first: 1, query: $query) {
            nodes {
            id
            email
            }
        }
        }
    """
    # Build search query string based on input parameters
    if not email:
        raise ValueError("Customer email must be provided.")
    
    try:
        # Get products by query
        response = requests.post(url, headers=headers, json={
            "query": query, 
            "variables": { 
                "query": f"email:{email}"
            } 
        })
        response.raise_for_status()
        result = response.json()
        customers = result.get('data', {}).get('customers', {}).get('nodes', [])
        return customers[0].get('id') if customers else None
    
    except Exception as e:
        logging.error(e)
        raise Exception(f"Shopify customer search error: {e}")


def GetProducts(store_name: str, shopify_access_token: str, 
                api_verison: str = SHOPIFY_API_VERSION, product_id: str = None, 
                product_name: str = None, description: str = None) -> list:
    """Returns list of products from Shopify that meets search criteria.

    Args:
        store_name (str): Unique Shopify store ID string.
        shopify_access_token (str): Shopify API access token.
        api_version (str, optional):  Shopify API version.
        product_id (str, optional):  Unique Shopify store item product ID.
        product_name (str, optional):  Keyword to search for in the product title.
        description (str, optional):  Keyword to search for in the product description.

    returns (list):
        List of Shopify store products matching search criteria.
    """
    api_verison = api_verison or SHOPIFY_API_VERSION
    url = f"https://{store_name}.myshopify.com/admin/api/{api_verison}/graphql.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": shopify_access_token,
    }
    query = """
        fragment Money on MoneyV2 {
            amount
            currencyCode
        }

        query GetProducts ($query: String!, $num_products: Int!) {
        products(query: $query, first: $num_products) {
            edges {
            node {
                id
                title
                description
                category {
                    fullName
                    name
                    id
                }
                feedback {
                    summary
                }
                status
                tags
                totalInventory
                vendor
                hasOnlyDefaultVariant
                currentPrice: priceRangeV2 {
                    maxVariantPrice {...Money}
                    minVariantPrice {...Money}
                }
                fullPrice: compareAtPriceRange {
                    maxVariantCompareAtPrice {...Money}
                    minVariantCompareAtPrice {...Money}
                }
                variants(first: 10) {
                edges {
                    node {
                    displayName
                    title
                    price 
                    availableForSale
                    OutOfStockOrderingPolicy: inventoryPolicy
                    }
                }
                }
            }
            }
        }
        }
    """
    # Build search query string based on input parameters
    query_string = None
    if product_id is not None:
        query_string = f'id:{product_id}'
    elif product_name is not None:
        query_string = f'title:*{product_name}*'
    elif description is not None:
        query_string = f'description:*{description}*'
    else:
        raise ValueError("product_name or product_id must be provided.")
    
    try:
        # Get products by query
        response = requests.post(url, headers=headers, json={
            "query": query, 
            "variables": { 
                "query": query_string,
                "num_products": NUM_PRODUCTS_TO_RETURN,
            } 
        })
        response.raise_for_status()
        result = response.json()
        products = result.get('data', {}).get('products', {}).get('edges', [])
        return products
    
    except Exception as e:
        logging.error(e)
        raise Exception(f"Shopify product search error: {e}")
