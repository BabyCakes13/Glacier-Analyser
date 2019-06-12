from colors import *
import definitions
import signal
import subprocess


class Multiprocess:
    def __init__(self, max_processes=definitions.MAX_PROCESSES, handler=None):
        self.max_threads = max_processes
        self.process_queue = []
        self.handler = handler

    def start_processing(self, task, task_name):
        self.poll_process_done()
        print(blue("Processes in queue before add: "), blue(len(self.process_queue)))

        sp = subprocess.Popen(task)
        self.process_queue.append((task_name, sp))
        print(blue("Processes in queue after add: "), blue(len(self.process_queue)))

    def check_process_full(self):
        """Checks if the process queue is full."""
        if len(self.process_queue) >= self.max_threads:
            task_name, sp = self.process_queue.pop()
            sp.wait()

    def check_process_done(self):
        """Checks if a process from the process queue is done, removes if so."""
        for task_name, sp in self.process_queue:
            if sp.poll() is not None:
                self.process_queue.remove((task_name, sp))
                print(blue("Query done: "), blue(task_name))
                if self.handler is not None:
                    self.handler(task_name, sp.returncode)

    def poll_process_done(self):
        """Keep asking if done."""
        while len(self.process_queue) >= self.max_threads:
            self.check_process_done()

    def wait_all_process_done(self):
        """Checks if a process from the process queue is done, removes if so."""
        while len(self.process_queue) > 0:
            self.check_process_done()

    def kill_all_humans(self):
        for task_name, sp in self.process_queue:
            sp.send_signal(signal.SIGINT)
