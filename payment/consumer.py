from main import redis, Order
import time 

key = 'refound_group'

group = 'payment-group'


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

                string = obj['pk']

                order = Order.get(string)

                order.status = 'refounded'
                order.save()
                


    
    except Exception as e:
        print(str(e))

    time.sleep(1)