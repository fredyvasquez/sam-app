import json
import traceback

inventory = {"120P90":{"SKU": "120P90", "Name" : "Google Home", "Price" : 49.99, "Inventory Qty" : 10}, 
                "43N23P":{"SKU": "43N23P", "Name" : "MacBook Pro", "Price" : 5399.99, "Inventory Qty" : 5},
                "A304SD":{"SKU": "A304SD", "Name" : "Alexa Speaker", "Price" : 109.50, "Inventory Qty" : 10},
                "234234":{"SKU": "234234", "Name" : "Raspberry Pi B", "Price" : 30.00, "Inventory Qty" : 2}}


def lambda_handler(event, context):
    
    try:
        print(event)
        cart = json.loads(event['body'])
        #cart = [{"SKU": "120P90", "Quantity":2}, {"SKU": "A304SD", "Quantity":1}, {"SKU": "234234", "Quantity":1}] 
        #cart = [{"SKU": "43N23P", "Quantity":1}, {"SKU": "234234", "Quantity":1}] 
        #cart = [{"SKU": "234234", "Quantity":1}, {"SKU": "43N23P", "Quantity":1}] 
        # cart = [{"SKU": "120P90", "Quantity":3}, {"SKU": "43N23P", "Quantity":1}, {"SKU": "A304SD", "Quantity":1}]
        #cart = [{"SKU": "A304SD", "Quantity":3}] 
        availableItems = checkout(cart)

    except Exception as e:
        print("Something went wrong")
        # Send some context about the error to Logs
        print(e)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Something went wrong",
                "exception": str(e),
                "stack": str(traceback.format_exc()),
                # "cart" : cart
            }),
        }

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": availableItems
        }),
    }

# Find the item in the inventory
def getItemFromInventory(sku):
    item = inventory.get(sku)
    # for i in inventory:
    #     if i["SKU"] == sku:
    #         return i

    return item
#def getItemFromInventory

# Apply discounts and promotions
def applyDisccounts(availableItems):
    total_cost = 0
    #for item in availableItems:
    for key, item in availableItems.items():
        # Each MacBook comes with a free Raspberry
        if item["SKU"] == "43N23P" :
            item["Total"] = item["Quantity"] * item["Price"]
            total_cost += item["Total"] 
        
        # 3 Google home for the price of 2
        if item["SKU"] == "120P90" :
            item["Total"] = ((item["Quantity"] / 3) // 1 * 2 + item["Quantity"] % 3) * item["Price"]
            total_cost += item["Total"]
        
        # 3 or more Alexa Speakers will have a 10% discount on all Alexa speakers
        if item["SKU"] == "A304SD":
            if item["Quantity"] >= 3:
                item["Total"] = item["Total"] * 0.9

            total_cost += item["Total"]

        # Each MacBook comes with a free Raspberry
        if item["SKU"] == "234234" :
            if availableItems.get("43N23P") is not None:
                if availableItems["43N23P"]["Quantity"] >= item["Quantity"]:
                    item["Total"] = 0
                else: 
                    item["Total"] = (item["Quantity"] - availableItems["43N23P"]["Quantity"]) * item["Price"]
            else:
                item["Total"] = item["Quantity"] * item["Price"]
            total_cost += item["Total"]

    return {"AvailableItems" : availableItems, "Total" : total_cost}

#def applyDisccounts

# proceeds to checkout the cart, validates tue ammount of requested items and apply disscounts if required
def checkout(cart):
    # Calculate the total cost of the cart
    availableItems = {}
    total_cost = 0

    for item in cart:
        sku = item["SKU"]
        quantity = item["Quantity"]
    
        inventory_item = getItemFromInventory(sku)
        if inventory_item is not None:
            price = inventory_item["Price"]
            inventory_qty = inventory_item["Inventory Qty"]
            # enough inventory
            if inventory_qty >= quantity :
                # Update inventory
                inventory_item["Inventory Qty"] -= quantity

               # Add the cost to the total without disccounts
                total_cost = price * quantity
                availableItems[sku] = ({"SKU": sku, "Quantity":quantity, "Message": "Available", "Price": price,"Total" : total_cost})
            else:
                availableItems[sku] = ({"SKU":sku, "Quantity":0, "Message": f"There are not enough items available with SKU {sku}", "Price": price,"Total" : 0})
        else:
            availableItems[sku] = ({"SKU":sku, "Quantity":0, "Message": f"Item with SKU {sku} is not available in inventory.", "Price": 0,"Total" : 0})

        # Apply discounts and promotions
        results = applyDisccounts(availableItems) 

    formattedTotal = "{:.2f}".format(results["Total"])
    return{"Available Items": results["AvailableItems"], "Total":formattedTotal}

