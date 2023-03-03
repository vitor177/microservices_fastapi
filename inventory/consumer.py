from main import redis, Product
import time 

key = 'order_completed'

group = 'inventory-group'


try:
    redis.xgroup_create(key, group)
except:
    print("Falha")

while (True):
    try:
        results = redis.xreadgroup(group, key, {key:'>'}, None)

        if results != []:
            
            for result in results:
                obj = result[1][0][1]

                string = obj['product_id']

                try:
                    product = Product.get(string)
                    product.quantity = product.quantity - int(obj['quantity'])
                    product.save()
                except:
                    redis.xadd('refound_order', obj, '*')



    
    except Exception as e:
        print(str(e))

    time.sleep(1)