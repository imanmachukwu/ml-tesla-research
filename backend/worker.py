import os
from redis import Redis
from rq import Worker, Queue

redis_conn = Redis(host=os.environ.get('REDIS_HOST', 'localhost'), port=6379)

if __name__ == '__main__':
	q = Queue(connection=redis_conn)    
	worker = Worker([q], connection=redis_conn)
	worker.work()
