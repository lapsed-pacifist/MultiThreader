import Queue  # or queue in Python 3
import threading
import logging

class PrintThread(threading.Thread):
	def __init__(self, queue):
		super(PrintThread, self).__init__()
		self.queue = queue
	
	def write(self, p):
		print '[{}] {}'.format(*p)

	def run(self):
		while True:
			result = self.queue.get()
			self.write(result)
			self.queue.task_done()

class WriteThread(PrintThread):
	def __init__(self, queue, fname):
		super(WriteThread, self).__init__(queue)
		self.fname = fname

	def write(self, p):
		with open(self.fname, 'a') as f:
			f.write(u'{}\n'.format(p).encode('utf-8'))

class ProcessThread(threading.Thread):
	def __init__(self, in_queue, out_queue, display_queue, process_function):
		super(ProcessThread, self).__init__()
		self.in_queue = in_queue
		self.out_queue = out_queue
		self.process = process_function
		self.display_queue = display_queue

	def run(self):
		while True:
			path = self.in_queue.get()
			try:
				output = self.process(path)
				try:
					result, print_out = output
					if self.display_queue is not None:
						self.display_queue.put([print_out, self.name])
				except (ValueError, TypeError) as err:
					result = output
				self.out_queue.put(result)
				self.in_queue.task_done()
			except:
				logging.critical('Process {}'.format(self.name), exc_info=True)
				self.in_queue.task_done()


if __name__ == '__main__':
	logging.basicConfig(filename='multithreader.log', format='[%(asctime)s] %(message)s', filemode='w')

	TaskQueue = Queue.Queue()
	ResultQueue = Queue.Queue()
	# PrintQueue = Queue.Queue()
	
	tasks = xrange(10)

	out_dir = 'file.txt'

	# spawn threads to process
	workers = []
	for i in range(0, 5):
		t = ProcessThread(TaskQueue, ResultQueue, display_queue=None, process_function=lambda task: (task, task))
		t.setDaemon(True)
		workers.append(t)
		t.start()

	# spawn threads to print
	writer = WriteThread(ResultQueue, out_dir)
	writer.setDaemon(True)
	writer.start()

	# add paths to queue
	for task in tasks:
		TaskQueue.put(task)

	# wait for queues to get empty
	TaskQueue.join()
	ResultQueue.join()
	# PrintQueue.join()