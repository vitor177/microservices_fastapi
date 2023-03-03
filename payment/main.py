from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import redis
from starlette.requests import Request
import requests
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

# Must be a differente database
redis = redis.Redis(
  host='redis-18539.c9.us-east-1-4.ec2.cloud.redislabs.com',
  port=18539,
  password='h2KU7BuJgK2rcnwMWOXKLE3OYB7z8glK',
  decode_responses=True)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str # pending, completed and refunded

    class Meta:
        database = redis

@app.get('/orders/{pk}')
def get(pk: str):
    order = Order.get(pk)
    redis.xadd('refound_order', order.dict(), '*')
    return order

@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks): # id, quantity
    body = await request.json()

    req = requests.get('http://localhost:8000/products/%s' % body['id'])

    product = req.json()


    order = Order(
        product_id = body['id'], price=product['price'], fee=0.2*product['price'], total=1.2*product['price'], quantity=body['quantity'], status='pending'
    )
    order.save()

    background_tasks.add_task(order_completed, order)

    return order

def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed', order.dict(), '*')